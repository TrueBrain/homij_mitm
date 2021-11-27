import asyncio
import click
import gzip
import logging

from homij_mitm.homij_forwarder import HomijForwarder
from homij_mitm.influxdb import InfluxDBClient

log = logging.getLogger(__name__)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


async def replay_file(influxdb_client, homij_forwarder, replay):
    func = open
    if replay.endswith(".gz"):
        func = gzip.open

    count = 0
    with func(replay, "rb") as fp:
        for line in fp:
            line = line.strip()
            if not line or line.decode()[0] == "#":
                continue

            if count == 0:
                log.info("Starting new batch (batch of 1k, capped at 100k)")
                batch = influxdb_client.batch()

            count += 1
            await homij_forwarder.process_request(line)

            if count == 100 * 1000:
                count = 0

                log.info("Closing batch ...")
                batch.close()
                log.info("Batch closed")

    if count != 0:
        log.info("Closing batch ...")
        batch.close()
        log.info("Batch closed")


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--basen-id", help="The ID of the BaseN to intercept", required=True)
@click.option("--influxdb-url", help="URL of the InfluxDB server", required=True)
@click.option("--influxdb-token", help="Token to access the InfluxDB server", required=True)
@click.option("--influxdb-org", help="Organisation of the InfluxDB server", required=True)
@click.option("--influxdb-bucket", help="Bucket to use in the InfluxDB server", default="metrics", show_default=True)
@click.argument("files", nargs=-1)
def main(basen_id, influxdb_url, influxdb_token, influxdb_org, influxdb_bucket, files):
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
    )

    influxdb_client = InfluxDBClient(influxdb_url, influxdb_token, influxdb_org, bucket=influxdb_bucket)
    influxdb_client.connect()

    homij_forwarder = HomijForwarder(
        basen_id=basen_id, send_measurement=influxdb_client.send_measurement, log_filename=None
    )

    for file in files:
        asyncio.run(replay_file(influxdb_client, homij_forwarder, file))


if __name__ == "__main__":
    main(auto_envvar_prefix="HOMIJ_MITM")
