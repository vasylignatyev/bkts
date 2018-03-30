#!/usr/bin/python3

import time
import paho.mqtt.client as mqtt
import json
import random

cards = (
    '047B20FA4F5384',
    '04E027FA4F5384',
    '04BED5FA4F5380',
    '04B886C2205280',
    '04F124FA4F5384',
    '0467DAFA4F5381',
    '04A840FA4F5384',
    '047541FA4F5384',
    '0473DBFA4F5380',
    '04AFD5FA4F5380',
    '045728FA4F5384',
    '045589C2205280')

last_index = 0
client = None
cards_len = len(cards) - 1
message_id = 1
print("cards_len: {}".format(cards_len))


def on_connect(client, payload, flag, rc):
    print("connected OK" if rc == 0 else "Bad connnection = {}".format(rc))

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
client = mqtt.Client("RANDOM_MQTT")
client.on_connect = on_connect  # attach function to callback

connect_broker()

while 1:
    # last_index += 1
    # print(cards[last_index])
    random_index = random.randint(0, cards_len)
    print(cards[random_index])

    to_bkts({
        "qr":cards[random_index],
        "type": 12
    })

    time.sleep(1)



