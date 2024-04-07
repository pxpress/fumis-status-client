# fumis-status-client
## Information 
This is a client on python for Fumis based Pallet Stoves which are using WiRCU WIFI module. The project is based on https://github.com/frenck/python-fumis

## How to use
In `fumisclient.py` there are two classes `PalletStoveStatus` and `Client`. Each of them are doing the following
### PalletStoveStatus
This class contains extracted data fields from the server response:
* `id` - MAC address of the WIFI module of the stove.
* `cmd` - Last command code
* `cmd_str` - Last code translated to string
* `status` - Status number of the stove. For more infromation, please refer to `STATUS_MAPPING` in `fumisdatastructures.py`
* `status_str` - Status translated to string
* `mode` - Mode of the stove
* `action` - Current action of the stove
* `error_code`: self.error_code,
* `temp` - Temperature of the room sensor
* `temp_target` - Target temperature of the room
* `water`: Temperature of the water in the stove
* `water_target`: Target temperature of the water in the stove
* `fumes_temp`: Exhaust temperature

### Client
This is the client for sending commands and reading the status of the stove. The client initiates the connection to `SERVER_NAME` in this case is `"api.fumis.si"`. The client requires username and password. Those are the MAC address of the WiRCU WIFI module and a PIN code provided by the distributor. You can set the username and password by changing the values of the `CLIENT_USERNAME` and `CLIENT_PASSWORD` variables in `fumisclient.py` file. 
Because of the HTTP nature of the connection, everytime a function is called, it creates a HTTP Client to handle the connection.

Here are the methods implemented in the client:
* `cl = Client(CLIENT_USERNAME, CLIENT_PASSWORD)` - creates an instance of the Client
* `update_last_status(jdata)` - used mainly internaly to fill in the `last_status` instance of the PalletStoveStatus
* `cl.read_data()` - Reads current status of the stove. Returns instance of the PalletStoveStatus
* `cl.command_turn_on_off(cmd)` - Sends command to turn on or off the stove. Avoid using it. Use `turn_on` and `turn_off` instead.
* `cl.command_set_temp(temp_id, value)` - Sets target `value` for temperature. The `temp_id` is choosing between `TEMP_ROOM_ID` or `TEMP_WATER_ID`
* `cl.turn_on()` - Initiating turning on sequence
* `cl.turn_off()` - Initiating turning off sequence
* `cl.set_room_temp(value)` - Sets target `value` for room temperature. Doesn't automaticaly turn on the stove.
