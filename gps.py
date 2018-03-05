#!/usr/bin/python2

import pynmea2
import serial

import time

input = serial.Serial("/dev/ttyUSB1")
print(input)
streamreader = pynmea2.NMEAStreamReader(input, errors='ignore')
print(streamreader)
input.flushInput()
while 1:
    try:
        #print("1")
        for msg in streamreader.next():
            if type(msg) == pynmea2.types.talker.GGA:
                print msg
                print msg.timestamp
                print str(msg.latitude) + " ", str(msg.longitude)
                print str(msg.gps_qual)
                print "***********"
            elif type(msg) == pynmea2.types.talker.RMC:
                print "direction: "+str(msg.true_course)
                print "speed: "+str(msg.spd_over_grnd * 1.582) + " km/h"

    except:
        input.close()

