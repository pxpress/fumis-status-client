import sys
import threading
import time
import logging
import argparse

import fumisclient as fumis
import paho.mqtt.client as mqtt

MQTT_SERVER = "localhost"
MQTT_PORT = 1883

logger = logging.getLogger('fumis_daemon')
logger.setLevel(logging.DEBUG)
parser = argparse.ArgumentParser(description="Fumis daemon in Python")
parser.add_argument('-l', '--log-file', default='fumis_daemon.log')
args = parser.parse_args()
fh = logging.FileHandler(args.log_file)
fh.setLevel(logging.DEBUG)

formatstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(formatstr)

fh.setFormatter(formatter)
fh.setStream(sys.stderr)

logger.addHandler(fh)
logger.info("==== Beginning of the log =====")


def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code " + str(rc))
    client.subscribe("pallet_stove/state/set")
    client.subscribe("pallet_stove/power/set")
    client.subscribe("pallet_stove/mode/set")
    client.subscribe("pallet_stove/fan/set")
    client.subscribe("pallet_stove/temp_high/set")
    client.subscribe("pallet_stove/temp_low/set")
    client.subscribe("pallet_stove/temp_target/set")


def process_message(msg):
    logger.debug(f"Message Topic: {msg.topic}")
    if msg.topic == "pallet_stove/power/set":
        logger.debug("Received POWER request")
        if msg.payload.decode("utf-8") == "ON":
            logger.debug("Power ON")
            cl = fumis.Client(fumis.CLIENT_USERNAME, fumis.CLIENT_PASSWORD)
            cl.turn_on()
        elif msg.payload.decode("utf-8") == "OFF":
            logger.debug("Power OFF")
            cl = fumis.Client(fumis.CLIENT_USERNAME, fumis.CLIENT_PASSWORD)
            cl.turn_off()
    elif msg.topic == "pallet_stove/temp_target/set":
        logger.debug("Setting TEMPERATURE to")
        temperature = float(msg.payload.decode("utf-8"))
        logger.debug(temperature)
        cl = fumis.Client(fumis.CLIENT_USERNAME, fumis.CLIENT_PASSWORD)
        cl.set_room_temp(temperature)


def on_message(client, userdata, msg):
    logger.debug("MQTT Message received: " + msg.topic + " " + str(msg.payload))
    process_message(msg)


def update_fumis_status():

    while True:
        try:
            cl = fumis.Client(fumis.CLIENT_USERNAME, fumis.CLIENT_PASSWORD)
            client = mqtt.Client()
            client.connect(MQTT_SERVER, MQTT_PORT, 60)
            logger.debug("Reading data from cloud")
            cl.read_data()
            logger.debug(cl.last_status)
            logger.debug("Publishing data to MQTT")
            publish_data_mqtt(cl, client)
        except:
            logger.error("GENERAL ERROR: Unable to get data from fumis cloud")
        time.sleep(10)


def publish_data_mqtt(cl, client):
    client.publish("pallet_stove/fumes_temp", str(cl.last_status.fumes_temp))
    client.publish("pallet_stove/room/temperature", str(cl.last_status.temp))
    client.publish("pallet_stove/room/target", str(cl.last_status.temp_target))
    client.publish("pallet_stove/temp_target", str(cl.last_status.temp_target))
    client.publish("pallet_stove/water/temperature", str(cl.last_status.water))
    client.publish("pallet_stove/water/target", str(cl.last_status.water_target))
    client.publish("pallet_stove/status", str(cl.last_status.status))
    client.publish("pallet_stove/mode/state", cl.last_status.mode)
    client.publish("pallet_stove/error_code", str(cl.last_status.error_code))
    client.publish("pallet_stove/action", cl.last_status.action)
    client.publish("pallet_stove/state", bytes("ON", "utf-8"))
    client.publish("pallet_stove/available", "online")


def main():
    cmd_client = mqtt.Client()
    cmd_client.on_connect = on_connect
    cmd_client.on_message = on_message
    cmd_client.connect(MQTT_SERVER, MQTT_PORT, 60)
    update_thread = threading.Thread(target=update_fumis_status)
    update_thread.start()
    while True:
        cmd_client.loop()


if __name__ == '__main__':
    main()
