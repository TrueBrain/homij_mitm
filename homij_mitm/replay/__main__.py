import asyncio
import click
import logging

from homij_mitm.homij_forwarder import HomijForwarder
from homij_mitm.influxdb import InfluxDBClient

log = logging.getLogger(__name__)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


async def replay_file(homij_forwarder, replay):
    with open(replay, "rb") as fp:
        for line in fp.readlines():
            line = line.strip()
            if not line or line[0] == "#":
                continue

            await homij_forwarder.process_request(line)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--basen-id", help="The ID of the BaseN to intercept", required=True)
@click.option("--influxdb-url", help="URL of the InfluxDB server", required=True)
@click.option("--influxdb-token", help="Token to access the InfluxDB server", required=True)
@click.option("--influxdb-org", help="Organisation of the InfluxDB server", required=True)
@click.option("--influxdb-bucket", help="Bucket to use in the InfluxDB server", default="metrics", show_default=True)
@click.option("--replay", help="Replay a log-file", default="")
def main(basen_id, influxdb_url, influxdb_token, influxdb_org, influxdb_bucket, replay):
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
    )

    influxdb_client = InfluxDBClient(influxdb_url, influxdb_token, influxdb_org, bucket=influxdb_bucket)
    influxdb_client.connect()

    homij_forwarder = HomijForwarder(
        basen_id=basen_id, send_measurement=influxdb_client.send_measurement, log_filename=None
    )

    asyncio.run(replay_file(homij_forwarder, replay))


if __name__ == "__main__":
    main(auto_envvar_prefix="HOMIJ_MITM")
