import fumisdatastructures as ds
import http.client
import mimetypes
import json

SERVER_NAME = "api.fumis.si"

CLIENT_USERNAME = '<FUMIS MAC ADDRESS>'
CLIENT_PASSWORD = '<FUMIS PIN CODE>'

TEMP_ROOM_ID = 1
TEMP_WATER_ID = 5
TEMP_TARGET = "set"
TEMP_CURRENT = "actual"

CMD_ON = 2
CMD_OFF = 1

class PalletStoveStatus:
    def __init__(self, idn, cmd, cmd_str, status, status_str, mode, action, error_code, temp, temp_target, water,
                 water_target, fumes_temp):
        self.id = idn
        self.cmd = cmd
        self.cmd_str = cmd_str
        self.status = status
        self.status_str = status_str
        self.mode = mode
        self.action = action
        self.error_code = error_code
        self.temp = temp
        self.temp_target = temp_target
        self.water = water
        self.water_target = water_target
        self.fumes_temp = fumes_temp

    def __str__(self):
        result = {'id': self.id,
                  'cmd': self.cmd,
                  'cmd_str': self.cmd_str,
                  'status': self.status,
                  'status_str': self.status_str,
                  'mode': self.mode,
                  'action': self.action,
                  'error_code': self.error_code,
                  'temp': self.temp,
                  'temp_target': self.temp_target,
                  'water': self.water,
                  'water_target': self.water_target,
                  'fumes_temp': self.fumes_temp
                  }
        return json.dumps(result)


def get_temp_from_json(jdata, idn, temp_type):  # idn = 1 - room, 5 - water, target = "set", "actual"
    for temp_id in jdata["controller"]["temperatures"]:
        if temp_id["onMainScreen"]:
            if temp_id["id"] == idn:
                return temp_id[temp_type]


def get_temp_fumes_json(jdata):
    for temp_id in jdata['controller']['diagnostic']['variables']:
        if temp_id['id'] == 11:
            return temp_id['value']


class Client:
    def __init__(self, username, password):
        self.last_status = None
        self.username = username
        self.password = password

    def update_last_status(self, jdata):
        self.last_status = PalletStoveStatus(
            idn=jdata["unit"]["id"],
            cmd=jdata["controller"]["command"],
            cmd_str=ds.STATE_MAPPING[jdata["controller"]["command"]],
            status=jdata["controller"]["status"],
            status_str=ds.STATUS_MAPPING[jdata["controller"]["status"]],
            mode=ds.MODE_MAPPING[jdata["controller"]["status"]],
            action=ds.ACTION_MAPPING[jdata["controller"]["status"]],
            error_code=jdata["controller"]["error"],
            temp=get_temp_from_json(jdata, TEMP_ROOM_ID, TEMP_CURRENT),
            temp_target=get_temp_from_json(jdata, TEMP_ROOM_ID, TEMP_TARGET),
            water=get_temp_from_json(jdata, TEMP_WATER_ID, TEMP_CURRENT),
            water_target=get_temp_from_json(jdata, TEMP_WATER_ID, TEMP_TARGET),
            fumes_temp=get_temp_fumes_json(jdata),
        )

    def read_data(self):
        conn = http.client.HTTPSConnection(SERVER_NAME)
        payload = json.dumps(ds.get_payload_json(self.username, self.password))
        conn.request("POST", "/v1/status/", payload, ds.get_headers(self.username, self.password))
        res = conn.getresponse()
        data = res.read()
        jdata = json.loads(data.decode("utf-8"))
        self.update_last_status(jdata)
        return self.last_status

    def command_turn_on_off(self, cmd):
        conn = http.client.HTTPSConnection(SERVER_NAME)
        payload = ds.get_payload_json(self.username, self.password)

        payload['controller'] = {'command': cmd}
        payload_str = json.dumps(payload)
        conn.request("POST", "/v1/status/", payload_str, ds.get_headers(self.username, self.password))
        res = conn.getresponse()
        data = res.read()
        jdata = json.loads(data.decode("utf-8"))
        self.update_last_status(jdata)
        return self.last_status

    def command_set_temp(self, temp_id, value):
        conn = http.client.HTTPSConnection(SERVER_NAME)
        payload = ds.get_payload_json(self.username, self.password)

        payload['controller'] = {
            "temperatures": [
                {
                    "id": temp_id,
                    "set": value
                }
            ]}
        payload_str = json.dumps(payload)
        conn.request("POST", "/v1/status/", payload_str, ds.get_headers(self.username, self.password))
        res = conn.getresponse()
        data = res.read()
        jdata = json.loads(data.decode("utf-8"))
        self.update_last_status(jdata)
        return self.last_status

    def turn_on(self):
        return self.command_turn_on_off(CMD_ON)

    def turn_off(self):
        return self.command_turn_on_off(CMD_OFF)

    def set_room_temp(self, value):
        return self.command_set_temp(TEMP_ROOM_ID, value)
