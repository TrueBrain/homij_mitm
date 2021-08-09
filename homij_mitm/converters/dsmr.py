"""
'dsmr' is the Stedin smart (power)meter.

Example:
    {
        'power': 0.0,
        'energy_low': 3139.452,
        'energy_high': 1664.239,
        'energy_low_prod': 2447.221,
        'energy_high_prod': 5776.321,
        'tariff': 1.0,
        'power_prod': 0.046
    }

Use everything except power/power_prod. Those two are gauges; the others are
counters. A counter is always more precise, and the gauges in this case depend
strongly on when the measurement was done.

Otherwise the values are already in the correct format, and need no other
special processing.

tariff:
  1 = low
  2 = high
"""


def convert_measurement(data):
    payload = {
        "dsmr_tariff": {
            "value": data["tariff"],
            "unit": "enum",
        },
        "dsmr_energy_low": {
            "value": data["energy_low"],
            "unit": "kW",
        },
        "dsmr_energy_high": {
            "value": data["energy_high"],
            "unit": "kW",
        },
        "dsmr_energy": {
            "value": data["energy_low"] + data["energy_high"],
            "unit": "kW",
        },
        "dsmr_energy_low_prod": {
            "value": data["energy_low_prod"],
            "unit": "kW",
        },
        "dsmr_energy_high_prod": {
            "value": data["energy_high_prod"],
            "unit": "kW",
        },
        "dsmr_energy_prod": {
            "value": data["energy_low_prod"] + data["energy_high_prod"],
            "unit": "kW",
        },
    }

    return payload
