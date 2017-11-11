#!/usr/bin/python3

import sys
import time
import os.path
import logging
import socket
import fcntl
import struct
import platform
from time import localtime, strftime
import paho.mqtt.client
import urllib.request
import threading
import os.path
import errno
import json
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication


# mqtt
MQTT_BROKER = "192.168.88.10"
#MQTT_BROKER = "localhost"
MQTT_TOPICS = [("t_bkts", 1), ("t_driver", 1), ("t_informer", 1)]
MQTT_RECONNECT_TIME = 60
MQTT_REREGISTER_TIME = 60
MQTT_RESUBSCRIBE_TIME = 60

MQTT_TYPE_REG_REQ     = 200
MQTT_TYPE_REG_RESP    = 200 # ???
MQTT_TYPE_ROUTE       = 201
MQTT_TYPE_STATUS_REQ  = 202
MQTT_TYPE_STATUS_RESP = 202
MQTT_TYPE_STOP        = 220  # at stop
MQTT_TYPE_START       = 221  # after
MQTT_TYPE_MESG        = 230
MQTT_TYPE_MODE        = 40   # RefundMode (what the heck)

MQTT_STATUS_OK        = 0
MQTT_STATUS_ERR       = 1
MQTT_STATUS_UNAVAIL   = 2
MQTT_STATUS_FAULT     = 3
MQTT_STATUS_COLLISION = 7

MQTT_SKIP_LOGGING       = ("PINGREQ", "PINGRESP")

## obj
mqtt = None
timer = None

def datetime():
    return strftime("[%Y-%m-%d %H:%M:%S]", localtime())

def print_n_log(*args):
    print(datetime(), *args)
    logging.info("MQTT:", args)

class Mqtt:
    def __init__(self, broker, topics):
        self.broker = broker
        self.mac = "lst"
        self.topics = topics
        self.mqtt = paho.mqtt.client.Client(self.mac, clean_session=False)
        self.mqtt.on_message = self.on_message
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_publish = self.on_publish
        self.mqtt.on_subscribe = self.on_subscribe
        self.mqtt.on_log = self.on_log
        self.mqtt.on_disconnect = self.on_disconnect
        self.skip_logging = MQTT_SKIP_LOGGING
        self.connected = False
        self.subscribed = False
        self.alarm = dict(c=threading.Event(), s=threading.Event())
        self.message_id = 0;
        self.connect()

    def is_connected(self):
        return self.connected
    def is_subscribed(self):
        return self.subscribed
    def connect(self, delay = None):
        if delay is not None:
            self.alarm['c'].wait(timeout=delay)
        if self.connected:
            return
        print_n_log("Connecting to broker at", self.broker, "as", self.mac, "...")
        rc = None
        try:
            rc = self.mqtt.connect(self.broker)
            self.mqtt.loop_start()
        except Exception as e:
            print_n_log("Network error:", e)
        return rc
    def on_connect(self, mac, data, flags, rc):
        if rc is not 0:
            print_n_log("Not connected:", rc)
        else:
            self.connected = True
            self.alarm['c'].set()
            print_n_log("Connected")
            self.subscribe()
    def subscribe(self, delay = None):
        if delay is not None:
            self.alarm['s'].wait(timeout=delay)
        if self.subscribed:
            return
        print_n_log("Subscribing to topics", self.topics, "...")
        self.mqtt.subscribe(self.topics)
    def on_subscribe(self, mac, data, mid, granted_qos):
        print_n_log("Subscribed:", mid, granted_qos)
        self.subscribed = True
        self.alarm['s'].set()
    def publish(self, topic, data):
        print_n_log("Publish to", topic + ":", data, mesg)
        re = self.mqtt.publish(topic, mesg)
        self.message_id += 1
    def on_publish(self, mac, data, mid):
        print_n_log("Published mid:", mid)
    def on_message(self, mac, data, msg):
        print_n_log("Got message on", msg.topic, str(msg.payload)) # raw output
#        print_n_log("Got message on", msg.topic, msg.payload.decode("utf-8"))
    def on_log(self, mac, data, level, string):
        what = string.split()
        if len(what) == 2:
            for k in self.skip_logging:
                if (what[1] == k): # skip logging
                    return
        print_n_log("Logged:", string)
    def on_disconnect(self, mac, userdata, rc):
        self.connected = False
        self.subscribed = False
        print_n_log("Disconnected:", rc)
    def close(self):
        self.mqtt.disconnect()
        self.mqtt.loop_stop()

def starter():
    global mqtt
    if mqtt is None:
        return
    if not mqtt.is_connected():
        print_n_log("Reconnect in " + str(MQTT_RECONNECT_TIME) + "sec ...")
        mqtt.connect(MQTT_RECONNECT_TIME)
    elif not mqtt.is_subscribed():
        print_n_log("Resubscribe in " + str(MQTT_RESUBSCRIBE_TIME) + "sec ...")
        mqtt.subscribe(MQTT_RESUBSCRIBE_TIME)


if __name__ == "__main__":
#    logger = logging.getLogger('infotube')
#    logger.setLevel(level=logging.INFO)
    app = QApplication(sys.argv)
    timer = QTimer()
    timer.timeout.connect(starter)
    timer.start(1000)

    mqtt = Mqtt(MQTT_BROKER, MQTT_TOPICS)
    sys.exit(app.exec_())

