import influxdb
import logging

log = logging.getLogger(__name__)


class InfluxDBClient:
    def __init__(self, host, port=8086, database='default'):
        self._host = host
        self._port = port
        self._database = database

    def connect(self):
        self._client = influxdb.InfluxDBClient(host=self._host, port=self._port)
        self._client.switch_database(self._database)

    def send_measurement(self, sensor, fields, tags, sensor_time=None):
        if sensor_time is None:
            sensor_time = time.time()

        for field, payload in fields.items():
            tags['unit'] = payload['unit']
            if not self._client.write_points([{'measurement': field, 'time': int(sensor_time), 'fields': {'value': payload['value']}}], tags=tags, time_precision='ms'):
                log.error('Failed to write measurement for %s', sensor)
