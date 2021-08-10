import datetime
import importlib
import json
import logging
import ssl

from aiohttp import web
from aiohttp.web_log import AccessLogger
from homij_mitm import web_routes

log = logging.getLogger(__name__)


def convert_measurements(path, data):
    mod = importlib.import_module(f"homij_mitm.converters.{path}")
    return mod.convert_measurement(data)


class ErrorOnlyAccessLogger(AccessLogger):
    def log(self, request, response, time):
        # Only log if the status was not successful
        if not (200 <= response.status < 400):
            super().log(request, response, time)


class HomijForwarder:
    basen_id = None
    send_measurement = None
    log_fp = None
    log_filename = None
    log_fp_lines = 0

    async def process_request(self, data):
        # If this is not a JSON payload, don't bother
        if len(data) < 1 or chr(data[0]) != "{":
            return

        # For some reason, their custom JSON encoder adds one } too many
        payload = json.loads(data[:-1])

        # As these raspberries create an ad-hoc WiFi between all of them, it can
        # happen that information from neighbours is being pushed out of our
        # internet. Make sure we don't pick up on them for our sensor information.
        if payload["id"] != self.basen_id:
            return

        if len(payload["content"]["c"]) != 1 or len(payload["content"]["c"][0]["write"]["rows"]) != 1:
            log.error("Unexpected payload: %r", payload)
            return

        entry = payload["content"]["c"][0]["write"]["rows"][0]

        # Go through the channels and register the values
        fields = {}
        for channel in entry["channels"]:
            if channel["channel"] == "Error":
                # Silently ignore entries with errors in them; this mostly means the probe
                # failed or that the device is offline.
                return
            elif "long" in channel:
                fields[channel["channel"]] = int(channel["long"])
            else:
                fields[channel["channel"]] = float(channel["double"])

        # Error about empty channels; this should not happen
        if not fields:
            log.error("Empty channels: %r", entry["channels"])
            return

        fields = convert_measurements(entry["path"], fields)
        if fields is None:
            return

        tags = {
            "device": "homij",
            "sensor": entry["path"],
        }

        self.send_measurement(entry["path"], fields, tags, sensor_time=entry["time"])

    def rawfile_write(self, data, host):
        if not self.log_fp:
            return

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_fp.write(f"# [{current_time}] Host: {host}\n")
        self.log_fp.write(data.decode())
        self.log_fp.write("\n")
        self.log_fp.flush()

        self.log_fp_lines += 1
        # Log rotate once in a while
        if self.log_fp_lines > 10000:
            self.rawfile_open()
            self.log_fp_lines = 0

    def rawfile_open(self):
        if self.log_fp is not None:
            self.log_fp.close()

        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_fp = open(f"{self.log_filename}.{current_time}", "a")

    def __init__(self, basen_id, send_measurement, log_filename):
        web_routes.set_homij_forwarder(self)

        self.basen_id = basen_id
        self.send_measurement = send_measurement

        if log_filename:
            self.log_filename = log_filename
            self.rawfile_open()

    def run(self, port, cert_file, key_file):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(cert_file, key_file)

        app = web.Application()
        app.add_routes(web_routes.routes)
        web.run_app(app, ssl_context=ssl_context, port=port, access_log_class=ErrorOnlyAccessLogger)
