import click
import logging

from homij_mitm.homij_forwarder import HomijForwarder
from homij_mitm.influxdb import InfluxDBClient

log = logging.getLogger(__name__)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--cert-file", help="Certificate to use for SSL", required=True, type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    "--key-file",
    help="Private key of the certificate to use for SSL",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--log-folder", help="Folder to log the raw requests in", type=click.Path(exists=True, file_okay=False))
@click.option("--basen-id", help="The ID of the BaseN to intercept", required=True)
@click.option("--influxdb-url", help="URL of the InfluxDB server", required=True)
@click.option("--influxdb-token", help="Token to access the InfluxDB server", required=True)
@click.option("--influxdb-org", help="Organisation of the InfluxDB server", required=True)
@click.option("--influxdb-bucket", help="Bucket to use in the InfluxDB server", default="metrics", show_default=True)
@click.option("--port", help="Port of the server", default=443, show_default=True)
@click.option(
    "--dont-forward",
    help="Don't actually forward the request and always return a 200",
    is_flag=True,
    default=False,
    show_default=True,
)
def main(
    cert_file,
    key_file,
    log_folder,
    basen_id,
    influxdb_url,
    influxdb_token,
    influxdb_org,
    influxdb_bucket,
    port,
    dont_forward,
):
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
    )

    influxdb_client = InfluxDBClient(influxdb_url, influxdb_token, influxdb_org, bucket=influxdb_bucket)
    influxdb_client.connect()

    log_filename = f"{log_folder}/logging.txt" if log_folder else None
    homij_forwarder = HomijForwarder(
        basen_id=basen_id,
        send_measurement=influxdb_client.send_measurement,
        log_filename=log_filename,
        dont_forward=dont_forward,
    )
    homij_forwarder.run(port=port, cert_file=cert_file, key_file=key_file)


if __name__ == "__main__":
    main(auto_envvar_prefix="HOMIJ_MITM")
