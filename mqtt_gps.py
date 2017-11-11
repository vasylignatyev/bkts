#!/usr/bin/python3
import time
import paho.mqtt.client as mqtt
import json


message_id = 1
client = None


def on_connect(client, payload, flag, rc):
    print("connected OK" if rc == 0 else "Bad connnection = {}".format(rc))

def to_driver(payload):
    global message_id, client

    print("to_driver")
    message_id += 1
    payload['timestamp'] = 1
    payload['mac'] = "B827EB8C06A0"
    print(payload)
    resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
    client.publish("t_driver", resultJSON)
    return

def to_bkts(payload):
    global message_id, client

    print("to_bkts")
    message_id += 1
    payload['timestamp'] = 1
    print(payload)
    resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
    client.publish("t_bkts", resultJSON)
    return

def connect_broker():
    global broker, client
    print("Connection to broker ", broker)

    try:
        client.connect(broker)

    except Exception as e:
        print("Can't connect: ", e)
        time.sleep(5)
        connect_broker()

broker = "localhost"
client = mqtt.Client("GPS_MQTT")
client.on_connect = on_connect  # attach function to callback

connect_broker()

while 1:
    try:

        f = open("/opt/telecard/gps.txt", 'r')
        x = json.load(f)
        f.close()

        print(x)

        payload = dict(
            type=310,
            latitude=x.get('latitude'),
            longitude=x.get('longitude'),
        )
        to_driver(payload)

        payload = dict(
            type=110,
            latitude=x.get('latitude'),
            longitude=x.get('longitude'),
        )
        to_bkts(payload)

        time.sleep(2)

    except Exception as e:
        print(e)

