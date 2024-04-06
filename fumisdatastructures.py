STATUS_OFF = "off"
STATUS_PRE_HEATING = "pre_heating"
STATUS_IGNITION = "ignition"
STATUS_COMBUSTION = "combustion"
STATUS_ECO = "eco"
STATUS_COOLING = "cooling"
STATUS_UNKNOWN = "unknown"

STATUS_MAPPING = {
    0: STATUS_OFF,
    10: STATUS_PRE_HEATING,
    20: STATUS_IGNITION,
    30: STATUS_COMBUSTION,
    40: STATUS_ECO,
    50: STATUS_COOLING,
}

MODE_MAPPING = {
    0: "off",
    10: "heat",
    20: "heat",
    30: "heat",
    40: "auto",
    50: "cool"
}

ACTION_MAPPING = {
    0: "off",
    10: "heating",
    20: "heating",
    30: "heating",
    40: "idle",
    50: "cooling"
}

STATE_OFF = "off"
STATE_ON = "on"
STATE_UNKNOWN = "unknown"

STATE_MAPPING = {
    1: STATE_OFF,
    2: STATE_ON,
}


def get_payload_json(username, password):
    return {
        "unit": {
            "id": username,
            "pin": password,
            "version": "2.3.0"
        },
        "apiVersion": "1.3",
    }


def get_headers(username, password):
    return {
        'username': username,
        'password': password,
        'Content-Type': 'application/json; charset=UTF-8'
    }


