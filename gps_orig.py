#!/usr/bin/python2
import pynmea2
import serial
import time
import json
import datetime
import paho.mqtt.client as mqtt
import json


message_id = 1

def on_connect(self, client, payload, flag, rc):
    print("connected OK" if rc == 0 else "Bad connnection = {}".format(rc))

def to_driver(payload):
    global message_id, client

    print("to_driver")
    message_id += 1
    payload['timestamp'] = datetime.datetime.now().timestamp()
    # payload['mac'] = _mac
    print(payload)
    resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
    client.publish("t_driver", resultJSON)
    return

def to_bkts(self, payload):
    global message_id, client

    print("to_bkts")
    message_id += 1
    payload['timestamp'] = datetime.datetime.now().timestamp()
    # print(payload)
    resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
    client.publish("t_bkts", resultJSON)
    return

broker = "localhost"
client = mqtt.Client("GPS")  # create new instance
client.on_connect = on_connect  # attach function to callback
# client.on_message = self.on_message  # attach function to callback

print("Connection to broker ", broker)
try:
    client.connect(broker)

except Exception as e:
    print("Can't connect: ", e)
    exit(1)

input = None

print("Start..")
while 1:
    try:
        print("Try open tty..")
        input = serial.Serial("/dev/ttyUSB1")
        print(input)
        streamreader = pynmea2.NMEAStreamReader(input, errors='ignore')
        print(streamreader)
        input.flushInput()
    except Exception as e:
        print(e)
        time.sleep(5)
        continue
    break

while 1:
    try:
        print("Try get msg..")
        for msg in streamreader.next():
            if type(msg) == pynmea2.types.talker.GGA:
                f = open("/opt/telecard/gps.txt", 'w')
                print(msg)
                json.dump(dict(latitude=msg.latitude,longitude=msg.longitude), f)
                f.close()

    except Exception as e:
        print(e)
        input.close()
        time.sleep(1)

print("Finish")

