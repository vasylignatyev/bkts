#! /usr/bin/python2

import pynmea2
import serial
import datetime
import threading
import logging
import json
import paho.mqtt.client as mqtt


class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        # GPS vars
        # self.gps_dev = "/dev/ttyUSB1"
        self.gps_dev = "/dev/ttyACM0"
        self.input = None
        self.stream_reader = None

        # mqtt vars
        self.broker = "localhost"
        self.mqtt_clint_name = "GPS_MQTT"
        self.message_id = 0
        self.client = None

        # init events
        self.reading_done_ev = None
        self.sending_done_ev = None


        self.running = True  # setting the thread running to true

    def on_connect(self, client, payload, flag, rc):
        logging.warning("connected OK" if rc == 0 else "Bad connnection = {}".format(rc))

    def connect_broker(self):
        logging.debug("Connection to broker ", self.broker)

        not_connected = True
        while not_connected:
            try:
                client.connect(self.broker)
                not_connected = False
            except Exception as e:
                logging.error("Can't connect: ", str(e))
                time.sleep(5)

    def connect_gps(self):
        while True:
            try:
                logging.info("Try open device: {}".format(self.gps_dev))
                self.input = serial.Serial(self.gps_dev)
                self.input.flushInput()
                self.stream_reader = pynmea2.NMEAStreamReader(self.input, errors='ignore')
                return
            except Exception as e:
                logging.error("while opening gps device: {}".format(str(e)))
                time.sleep(5)

    def read_coordinates(self):
        while True:
            try:
                logging.debug("read_coordinates trying to read from device")
                for msg in self.streamreader.next():
                    if type(msg) == pynmea2.types.talker.GGA:
                        coordinates = {"latitude": msg.latitude, "longitude":msg.longitude}
                        logging.debug("Coordinates: {}".format(str(coordinates)))
                return coordinates
            except Exception as e:
                logging.error("while reading coordinates: {}".str(e))
                time.sleep(1)
                self.input.close()
                self.connect_gps()

    def to_driver(self, coordinates):
        logging.debug("to_driver: ")

        payload = {"type": 310}
        self.message_id += 1
        payload['message_id'] = self.message_id
        payload['timestamp'] = datetime.datetime.now().timestamp()

        result_json = json.dumps(payload, ensure_ascii=False).encode('utf8')
        client.publish("t_driver", result_json)
        return

    def to_bkts(self, payload):
        global message_id, client

        print("to_bkts")
        message_id += 1
        payload['timestamp'] = datetime.datetime.now().timestamp()
        resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
        client.publish("t_bkts", resultJSON)
        return

    def send_coordinates(self):
        pass


    def run(self):
        self.client = mqtt.Client(self.mqtt_clint_name)
        self.client.on_connect = self.on_connect  # attach function to callback
        self.connect_broker()
        self.connect_gps()

        # init events
        self.reading_done_ev = threading.Event()
        self.sending_done_ev = threading.Event()

        # init threads
        t1 = threading.Thread(target=self.read_coordinates(self.sending_done_ev, self.reading_done_ev))
        t2 = threading.Thread(target=self.send_coordinates(self.reading_done_ev, self.sending_done_ev))

        # start threads
        t1.start()
        t2.start()

        self.sending_done_ev    .set()  # initiate the first event

        # join threads to the main thread
        t1.join()
        t2.join()




if __name__ == '__main__':
    gps_poller = GpsPoller()  # create the thread
    try:
        gps_poller.run()
        pass

    except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
        print("\nKilling Thread...")

    print("Done.\nExiting.")