#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time
import threading
# import gps_emulator
import json
from uuid import getnode as get_mac
import os


def main():
    App()

class App(threading.Thread):
    def __init__(self):
        super(App, self).__init__()
        self.start()

    def run(self):
        Emulator()

class Emulator:
    def __init__(self):
        self.client = None

        try:
            with open("AAC04800010.json", 'r') as infile:
                self._gps_path = json.load(infile)
                infile.close()
        except Exception as e:
            # print(str(e))
            return

        # print("Path file containe '{}' points".format(len(self._gps_path)))

        self._message_id = 0
        self._dst = time.daylight and time.localtime().tm_isdst > 0
        self._utc_offset = - (time.altzone if self._dst else time.timezone)
        self._gps_idx = 0
        self.latitude = 0.0
        self.longitude = 0.0
        self._mac = hex(get_mac())[2:14]
        self._mac = self._mac.upper()
        # print("my MAC is: {}".format(self._mac))

        self.run()

    def run(self):
        thread = threading.Thread(target=self.generator, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def emmulate_gps(self):
        # print("emmulate_gps")

        if self._gps_idx >= self._gps_path.__len__():
            self._gps_idx = 0

        self.latitude,self.longitude  = self._gps_path[self._gps_idx]
        self._gps_idx += 1

        payload = dict(
            type=310,
            latitude=self.latitude,
            longitude=self.longitude,
        )
        self.to_driver(payload)

        payload = dict(
            type=110,
            latitude=self.latitude,
            longitude=self.longitude,
        )
        self.to_bkts(payload)

    def local_exec(self):
        self.emmulate_gps()

    def generator(self):
        broker = "localhost"
        self.client = mqtt.Client("GPS")  # create new instance

        # self.client.on_connect = self.on_connect  # attach function to callback
        # self.client.on_message = self.on_message  # attach function to callback

        # print("Connection to broker ", broker)
        try:
            self.client.connect(broker)
        except Exception as e:
            # print("Can't connect: ", e)
            exit(1)
        else:
            i = 0
            loop_flag = 1
            while loop_flag == 1:
                time.sleep(1)
                i += 1
                if i > 0:
                    i = 0
                    self.local_exec()

            self.client.loop_stop()
            self.client.disconnect()

    def to_driver(self, payload):
        #print("to_driver")
        self._message_id += 1
        payload['timestamp'] = int((time.time())) + self._utc_offset
        payload['mac'] = self._mac
        # print(payload)
        resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
        self.client.publish("t_driver", resultJSON)
        return

    def to_bkts(self, payload):
        # print("to_bkts")
        self._message_id += 1
        payload['timestamp'] = int((time.time())) + self._utc_offset
        # print(payload)
        resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
        self.client.publish("t_bkts", resultJSON)
        return

if __name__ == "__main__":
    main()
