import influxdb_client
import logging
import time

from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision

log = logging.getLogger(__name__)


class InfluxDBClient:
    def __init__(self, url, token, org, bucket="metrics"):
        self._url = url
        self._token = token
        self._org = org
        self._bucket = bucket

    def connect(self):
        self._client = influxdb_client.InfluxDBClient(url=self._url, token=self._token, org=self._org)
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)

    def send_measurement(self, sensor, fields, tags, sensor_time=None):
        if sensor_time is None:
            sensor_time = int(time.time() * 1000)

        points = []
        for field, payload in fields.items():
            tags["unit"] = payload["unit"]
            tags["sensor"] = sensor

            point = {
                "measurement": field,
                "tags": tags,
                "time": sensor_time,
                "fields": {
                    "value": payload["value"],
                },
            }

            points.append(influxdb_client.Point.from_dict(point, WritePrecision.MS))

        self._write_api.write(bucket=self._bucket, record=points)

    def batch(self):
        self._write_api = self._client.write_api(write_options=influxdb_client.WriteOptions())
        return self._write_api
