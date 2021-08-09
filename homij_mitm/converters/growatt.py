"""
'growatt' is the inverter for the solar panels.

Example:
    {
        "energy_today_high": 0.0,
        "energy_today_low": 34196.0,
        "energy_high": 1.0,
        "energy_low": 34196.0,
        "epv_today_high": 0.0,
        "epv_today_low": 61164.0,
        "epv_high": 0.0,
        "epv_low": 61164.0,
        "worktime_high": 712.0,
        "worktime_low": 59344.0,
        "active": 255.0,
        "reactive": 255.0,
        "voltage": 6000.0,
        "pf": 65535.0,
        "phigh": 0.0,
        "plow": 60000.0,
        "state": 1.0,
        "input_high": 0.0,
        "input_low": 2377.0,
        "pv1_voltage": 3371.0,
        "pv1_current": 4.0,
        "pv1_power_high": 0.0,
        "pv1_power_low": 1348.0,
        "pv2_voltage": 2573.0,
        "pv2_current": 4.0,
        "pv2_power_high": 0.0,
        "pv2_power_low": 1029.0,
        "output_high": 0.0,
        "output_low": 2077.0,
        "grid_freq": 4999.0,
        "grid_voltage": 2382.0,
        "grid_current": 3.0,
        "grid_output_high": 0.0,
        "grid_output_low": 714.0,
        "grid_voltage_2": 2388.0,
        "grid_current_2": 3.0,
        "grid_output_2_high": 0.0,
        "grid_output_2_low": 716.0,
        "grid_voltage_3": 2385.0,
        "grid_current_3": 3.0,
        "grid_output_3_high": 0.0,
        "grid_output_3_low": 715.0,
        "fault_iso": 0.0,
        "fault_gfci": 0.0,
        "fault_dci": 0.0,
        "fault_pv": 0.0,
        "fault_ac_volt": 0.0,
        "fault_ac_freq": 0.0,
        "fault_temperature": 0.0,
        "fault_code": 0.0,
        "temperature": 411.0
    }

Fault values are of no real interest, and there are a few values thare are
nearly always fixed. Next to the values given, also create a few values that
are a combination of them, to make graphs easier later on.

'total' values appear to be corrupted. This already happens on the Modbus. So
we have to ignore those values, and start fresh every day with counting.

'epv_' values are only of pv1, not of pv2 or the combination. As such, they
are not usable. This is a mistake in the code of Homij.

state:
    0 = waiting
    1 = normal
    3 = fault
"""


def get_high_low(data, label):
    return (int(data[f"{label}_high"]) << 16) | int(data[f"{label}_low"])


def convert_measurement(data):
    payload = {
        "growatt_state": {
            "value": data["state"],
            "unit": "enum",
        },
        "growatt_temperature": {
            "value": data["temperature"] / 10,
            "unit": "celcius",
        },
        "growatt_grid_energy_today": {
            "value": get_high_low(data, "energy_today") / 10,
            "unit": "kWh",
        },
        "growatt_pv_voltage_1": {
            "value": data["pv1_voltage"] / 10,
            "unit": "V",
        },
        "growatt_pv_voltage_2": {
            "value": data["pv2_voltage"] / 10,
            "unit": "V",
        },
        "growatt_pv_voltage": {
            "value": (data["pv1_voltage"] + data["pv2_voltage"]) / 2 / 10,
            "unit": "V",
        },
        "growatt_pv_current_1": {
            "value": data["pv1_current"] / 10,
            "unit": "A",
        },
        "growatt_pv_current_2": {
            "value": data["pv2_current"] / 10,
            "unit": "A",
        },
        "growatt_pv_current": {
            "value": (data["pv1_current"] + data["pv2_current"]) / 2 / 10,
            "unit": "A",
        },
        "growatt_pv_energy_1": {
            "value": get_high_low(data, "pv1_power") / 10,
            "unit": "W",
        },
        "growatt_pv_energy_2": {
            "value": get_high_low(data, "pv2_power") / 10,
            "unit": "W",
        },
        "growatt_pv_energy": {
            "value": get_high_low(data, "input") / 10,
            "unit": "W",
        },
        "growatt_grid_freq": {
            "value": data["grid_freq"] / 100,
            "unit": "Hz",
        },
        "growatt_grid_voltage_1": {
            "value": data["grid_voltage"] / 10,
            "unit": "V",
        },
        "growatt_grid_voltage_2": {
            "value": data["grid_voltage_2"] / 10,
            "unit": "V",
        },
        "growatt_grid_voltage_3": {
            "value": data["grid_voltage_3"] / 10,
            "unit": "V",
        },
        "growatt_grid_voltage": {
            "value": (data["grid_voltage"] + data["grid_voltage_2"] + data["grid_voltage_3"]) / 3 / 10,
            "unit": "V",
        },
        "growatt_grid_current_1": {
            "value": data["grid_current"] / 10,
            "unit": "A",
        },
        "growatt_grid_current_2": {
            "value": data["grid_current_2"] / 10,
            "unit": "A",
        },
        "growatt_grid_current_3": {
            "value": data["grid_current_3"] / 10,
            "unit": "A",
        },
        "growatt_grid_current": {
            "value": (data["grid_current"] + data["grid_current_2"] + data["grid_current_3"]) / 3 / 10,
            "unit": "A",
        },
        "growatt_grid_energy_1": {
            "value": get_high_low(data, "grid_output") / 10,
            "unit": "W",
        },
        "growatt_grid_energy_2": {
            "value": get_high_low(data, "grid_output_2") / 10,
            "unit": "W",
        },
        "growatt_grid_energy_3": {
            "value": get_high_low(data, "grid_output_3") / 10,
            "unit": "W",
        },
        "growatt_grid_energy": {
            "value": get_high_low(data, "output") / 10,
            "unit": "W",
        },
    }

    return payload
