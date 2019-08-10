"""
'a1m' is the boiler and everything around that.

Example:
    {
        "SlaveId": 1,
        "BaudRate": 3,
        "Parity": 0,
        "FirmwareVersion": 30012,
        "DetectedSystemType": 1,
        "FaultCode": 8000,
        "SystemState": 1,
        "OperatingMode": 0,
        "OperatingModeDHW": 1,
        "ACModeZone1": 0,
        "ACModeZone2": 2,
        "WaterTankSetpoint": 5000.0,
        "HCThermostatTargetZone1": 2100.0,
        "HCThermostatTargetZone2": 3500.0,
        "ForceDHW": 0,
        "Holiday": 0,
        "DHWOnProhibit": 0,
        "HeatingOnProhibitZone1": 0,
        "CoolingOnProhibitZone1": 1,
        "HeatingOnProhibitZone2": 0,
        "CoolingOnProhibitZone2": 1,
        "ServerScheduleRequest": 0,
        "CapacityMode": 0,
        "CapacityControlRatio": 0,
        "FanMode": 0,
        "CurrentHour": 0,
        "CurrentMinute": 0,
        "WaterTemperatureSetpoint": 0.0,
        "ThermostatTargetTemperatureZone1": 2100.0,
        "ThermostatTargetTemperatureZone2": 2000.0,
        "HCControlType": 0,
        "RefrigerantAddress": 0,
        "DefrostState": 0,
        "RefrigerantErrorInfo": 0,
        "ErrorDigit1": 0,
        "ErrorDigit2": 0,
        "HeatPumpFrequency": 0,
        "TemperatureSetpointZone1": 2100.0,
        "TemperatureSetpointZone2": 2000.0,
        "FlowTemperatureSetpointZone1": 3500.0,
        "FlowTemperatureSetpointZone2": 3500.0,
        "LegionellaTemperatureSetpoint": 6500.0,
        "DHWTemperatureDrop": 50.0,
        "RoomTemperatureZone1": 2600.0,
        "RoomTemperatureZone2": -3900.0,
        "RefrigerantLiquidTemperature": 3150.0,
        "OutdoorAmbientTemperature": 200.0,
        "FlowTemperature": 3500.0,
        "ReturnTemperature": 3100.0,
        "WaterTemperature": 4900.0,
        "FlowTemperatureZone1": 2500.0,
        "ReturnTemperatureZone1": 2500.0,
        "FlowTemperatureZone2": 2500.0
    }

Most information in here is pretty static, and not really usefl to track.
Mainly the temperatures are interesting.

operating_mode:
    0 = Stop
    1 = Hot Water
    2 = Heating
    3 = Cooling
    5 = Freeze Stat
    6 = Legionella
    7 = Heating-Eco
"""


def convert_measurement(data):
    payload = {
        'a1m_operating_mode': {
            'value': data['OperatingMode'],
            'unit': 'enum',
        },
        'a1m_thermostat_room': {
            'value': data['ThermostatTargetTemperatureZone1'] / 100,
            'unit': 'C',
        },
        'a1m_temperature_room': {
            'value': data['RoomTemperatureZone1'] / 100,
            'unit': 'C',
        },
        'a1m_temperature_water': {
            'value': data['WaterTemperature'] / 100,
            'unit': 'C',
        },
        'a1m_temperature_refrigerant_liquid': {
            'value': data['RefrigerantLiquidTemperature'] / 100,
            'unit': 'C',
        },
        'a1m_temperature_outside': {
            'value': data['OutdoorAmbientTemperature'] / 10,
            'unit': 'C',
        },
    }
    return payload
