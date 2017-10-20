#!/usr/bin/python3

import sys
import time
import fcntl
import struct
import socket
import syslog
import os.path
import platform
from enum import Enum
from time import localtime, strftime
#import atexit
#import ctypes
#from ctypes.util import find_library
from PyQt4.QtGui import QMainWindow, QApplication, QWidget, QStackedWidget, QFrame, QHBoxLayout, QLabel, QPixmap, QDialog
from PyQt4.QtCore import Qt, QTimer, QRect
import paho.mqtt.client
import urllib.request
import socketserver
import subprocess
import threading
import hashlib
import errno
import json
import vlc


## const

PROGNAME = "infotube"
SW_VERSION = "0.38"
HW_VERSION =  platform.machine() + "-" + platform.release().split("-")[-1]

BASE_DIR = "/opt/telecard/"+PROGNAME+"/"
MEDIA_DIR = BASE_DIR + "media/"

VLC_OPTIONS = ""
#VLC_OPTIONS += "--vout x11"
VLC_OPTIONS += "--vout dummy"
#VLC_OPTIONS += " --logo-position 6 --sub-filter logo --logo-file " + BASE_DIR + "logo0.png --logo-position 6"
#VLC_OPTIONS += " -v"
#VLC_OPTIONS += " --quiet"
#VLC_OPTIONS += "--ignore-config --avcodec-fast -v"
#    vlc http://dl6.mp3party.net/download/7952427 --vout dummy --sout "#duplicate{dst=std{access=file,mux=raw,dst=OUT.mp3},dst=display" --sout-all

WSU="1280"  # default: 1920x550 from display spec
RCFILE=BASE_DIR+"it"+WSU+".rc"
geom = None

#BASE_FF = '"Droid Sans"'
BASE_FF = 'FreeSet'
FFAMILY = 'font-family:'+BASE_FF+',arial,sans-serif;'   # font family
SPRFX = FFAMILY + "font-weight:800;"
FG_STYLE = "color:#6ea61d;"
BG_STYLE = "background-color:white;"
PANE_BG_STYLE = "background-color:black;"

def fn_style0(tag, prfx, lag=None):
    return dict(style=prfx+"font-size:"+str(geom[tag]['fs'])+"px;", geom=geom[tag]['g'], lag=lag)

def init_css():
    global font, info_style, cs0, cs1, cs2, cs3, stop_css
    font = SPRFX + "font-size:"+str(geom['win']['fs'])+"px;"
    info_style = dict(title=font+FG_STYLE, name=font+"padding-left:40px;", lag=font+FG_STYLE)
    cs0 = SPRFX + "background:transparent; color:black;"
    cs1 = SPRFX + "background:transparent; color:#1e9a49;"
    cs2 = cs1 +"font-size:"+str(geom['s1']['fs'])+"px;"
    cs3 = SPRFX + "background:transparent; color:#6eab26; font-size:"+str(geom['s1']['fs'])+"px;"
    stop_css = dict(
        up=fn_style0('up', cs0),
        bl=fn_style0('bl', cs0),
        br=fn_style0('br', cs0),
        s1=fn_style0('s1', cs1),
        s2=fn_style0('s2', cs0, lag=dict(style=cs3, geom=geom['s2']['g'])),
        s3=fn_style0('s3', cs0, lag=dict(style=cs3, geom=geom['s3']['g'])),
        route=fn_style0('rt', cs0),
        version=fn_style0('sw_v', cs0),
    )
    stop_css['version']['style'] += "color:white;"

STOPAT_NDX = 0  # in the main window stack
#PLAYER_NDX = 1
IMAGE_NDX = 0   # in the player stack
VIDEO_NDX = 1
URL_PREFIX = "http:"
TS_TEXT = "наступна"

class MediaType(Enum):
    NONE  = 0
    IMAGE = 1
    AUDIO = 2
    VIDEO = 4

BASE_IMAGE = BASE_DIR+"kyiv-"+WSU+".png"
BASE_MEDIA = dict(type=MediaType.IMAGE, file=BASE_IMAGE)
IMAGES = dict(vh=BASE_DIR+"tr-ico"+WSU+".png", dl=BASE_DIR+"rt-sep"+WSU+".png",
    at=BASE_DIR+"stop-at-"+WSU+".jpg", after=BASE_DIR+"stop-after-"+WSU+".jpg")

class SwType(Enum):
    NONE  = 0
    AV_OFF = 1
    FULL_OFF = 2

IFACE = "eth0"

## mqtt
MQTT_BROKER = "192.168.1.10"
#MQTT_BROKER = "localhost"
MQTT_TOPICS = [("t_informer", 1)]
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
MQTT_TYPE_SYNC        = 41   # media syncronization

MQTT_STATUS_OK        = 0
MQTT_STATUS_ERR       = 1
MQTT_STATUS_UNAVAIL   = 2
MQTT_STATUS_FAULT     = 3
MQTT_STATUS_COLLISION = 7

MQTT_SKIP_LOGGING       = ("PINGREQ", "PINGRESP")

## udp logger, plus
UDP_LOGGER_HOST = "localhost"
UDP_LOGGER_PORT = 10514
HDMI_LOG = "/var/log/hdmi.log"

## obj
mqtt = None
timer = None
player = None

station = None
station_lock = threading.RLock()
class Station:
    def __init__(self):
        self.state = None
        self.title = None
        self.template = None
        self.stops = None
        self.sync = None
    def set_state(self, value):
        with station_lock:
            self.state = value
    def set_title(self, value):
        with station_lock:
            self.title = value
    def set_template(self, template, stops):
        with station_lock:
            self.template = template
            self.stops = stops
    def set_sync(self, data):
        with station_lock:
            self.sync = data
    def attr(self):
        return self.state, self.title, self.template, self.stops, self.sync


STATUS_NA = -1
STATUS_HDMI_BIT     = 0
STATUS_AUDIO_BIT    = 1
STATUS_TEMP_BIT     = 2
hw_status = None
hw_status_lock = threading.RLock()
class HW_Status:
    def __init__(self):
        self.hdmi = STATUS_NA
        self.audio = STATUS_NA
        self.temp = STATUS_NA   # temperature
        self.changed = False
    def set_hdmi(self, value):
        with hw_status_lock:
            self.hdmi = value
            self.changed = True
    def set_audio(self, value):
        with hw_status_lock:
            self.audio = value
            self.changed = True
    def set_temperatue(self, value):
        with hw_status_lock:
            self.temp = value
            self.changed = True
    def attr(self):
        return self.hdmi, self.audio, self.temp
    def is_changed(self):
        return self.changed
    def clr_changed(self):
        self.changed = False

## func
def datetime():
    return strftime("[%Y-%m-%d %H:%M:%S]", localtime())

def print_n_log(*args):
    print(datetime(), *args)
    s = '['+PROGNAME.upper()+'] '
    s += "".join(" "+str(a) for a in args)
#    for a in args:
#        s += str(a)
    syslog.syslog(s)


class Stopat(QWidget):
    def __init__(self, images, parent=None, options = None):
        QWidget.__init__(self, parent)
        self.images = images
        self.options = options
        self.info = QFrame()
        self.mediacache = []
        self.threads = []
        self.synced = True

        LL0 = dict(lab=None, lag=None)
        self.elems = dict(
            at   =dict(up=LL0, bl=LL0, br=LL0), # up, bottom-left, bottom-right
            after=dict(s1=LL0, s2=LL0, s3=LL0), # 1st stop, 2nd stop, 3rd stop
        )
        self.bgs =dict(unregistered="bg-"+WSU+".jpg", registered="bg-noinfo2-"+WSU+".jpg",
                disconnected="bg-"+WSU+".jpg", connected="bg-noinfo2-"+WSU+".jpg")
        self.tags_l1 = ('at', 'after')
        for t in self.tags_l1:
            self.bgs[t] = BG_STYLE if self.images is None else "background-image:url(" + self.images[t] + ");"
        self.set_bg("unregistered")

        self.setContentsMargins(0, 0, 0, 0)
        self.route = self.setlabel(None, 'route', Qt.AlignCenter)
        self.tags_l2 = dict(
            at=dict(    # up, bottom-left, bottom-right
                up=dict(text=None,    lag=None, align=Qt.AlignCenter),
                bl=dict(text=TS_TEXT, lag=None, align=(Qt.AlignVCenter|Qt.AlignLeft)),
                br=dict(text=None,    lag=None, align=(Qt.AlignVCenter|Qt.AlignLeft)),
            ),
            after=dict( # 1st stop, 2nd stop, 3rd stop
                s1=dict(text=None, lag=None, align=Qt.AlignCenter),
                s2=dict(text=None, lag=0, align=Qt.AlignVCenter|Qt.AlignLeft),
                s3=dict(text=None, lag=0, align=Qt.AlignVCenter|Qt.AlignLeft),
            )
        )
        for t1 in self.tags_l1:
            for t2 in self.tags_l2[t1]:
                v = self.tags_l2[t1][t2]
                self.elems[t1][t2] = self.setlabel(v['text'], t2, v['align'], v['lag'])

        for t1 in self.elems:   # hide them all
            for t2 in self.elems[t1]:
                for t3 in self.elems[t1][t2]:
                    v = self.elems[t1][t2][t3]
                    if v is not None:
                        v.hide()

        self.sw_label = QLabel(PROGNAME+"-"+SW_VERSION, self.info)
        self.sw_label.setStyleSheet(stop_css['version']['style'])
        self.sw_label.setGeometry(stop_css['version']['geom']['x'], stop_css['version']['geom']['y'], stop_css['version']['geom']['w'], stop_css['version']['geom']['h'])
        self.sw_timer = QTimer()
        self.sw_timer.timeout.connect(self.rm_sw)
        self.sw_timer.start(5000)

        self.box = QHBoxLayout()
        self.box.setSpacing(0)
        self.box.setContentsMargins(0, 0, 0, 0)
        self.box.addWidget(self.info)
        self.setLayout(self.box)

        # audio only (without any video out, without window, i.e. some background audio)
        self.player = vlc.MediaPlayer(vlc.Instance()) if self.options is None else vlc.MediaPlayer(vlc.Instance(self.options))

    def rm_sw(self):
        self.sw_label.hide()
        self.sw_timer.stop()

    def look_in_cache(self, filename, timestamp):
        for k in self.mediacache:
            if (k['fn'] == filename) and (k['ts'] == timestamp):
                return k['path']
        return None

    def getter(self, url, fpath):
        try:
            re = urllib.request.urlretrieve(url, fpath)
        except urllib.error.ContentTooShortError as err:
            print_n_log("Got truncated data: {} ({})".forma(err.msg, url))
        except urllib.error.HTTPError as err:
            print_n_log("Got HTTP error: {} {} ({})".format(err.code, err.reason, url))
        except urllib.error.URLError as err:
            print_n_log("Got URL error: {} ({})".format(err.reason, url))

    def squeeze_threads_out(self):
        for t in self.threads:
            if not t['thr'].isAlive():
                t['thr'].handled = True
        self.threads = [t for t in self.threads if not t['thr'].handled]   # remove finished threads

    def in_progress(self, url):
        for t in self.threads:
            if t['thr'].isAlive():
                if t['url'] == url:
                    return True
        return False

    def is_it_localmedia(self, rid, sid, category, url, timestamp, retrieve = True):
        filename = os.path.basename(url)
        cached = self.look_in_cache(filename, timestamp)
        if cached is not None:
            return (True, cached)

        if len(self.threads) > 0:   # squeeze threads out by the way
            self.threads = [t for t in self.threads if t['thr'].isAlive()]
        if self.in_progress(url):
            print_n_log("Retrieving", url, "in progress..")
            return (False, None)

        ldir = MEDIA_DIR + str(rid)
        fpath = "{}/{:02d}-{}-{}-{}".format(ldir, sid, category, timestamp, filename)
        if os.path.isfile(fpath):
            self.mediacache.append(dict(fn=filename, ts=timestamp, path=fpath))
            return (True, fpath)
        else:
            if retrieve:
                if not os.path.isdir(ldir):
                    try:
                        os.makedirs(ldir, exist_ok=True)
                    except OSError as e:
                        print_n_log(e)
                        return (False, None)
                print_n_log("Retrieve", url, "as", fpath)
                t = threading.Thread(target=self.getter, args=(url, fpath))
                t.start()
                self.threads.append(dict(thr=t, url=url))
        return (False, None)

    def check_all_media(self, data, callback):
        for m in data:
            url = m.get('url', None)
            rid = m.get('rid', None)
            sid = m.get('sid', None)
            cat = m.get('category', None)
            ts = m.get('timestamp', None)
            hsum = m.get('hash', None)
            if all(v is not None for v in (rid, sid, cat, url, ts, hsum)):
                if not callback(rid, sid, cat, url, ts, hsum):
                    return False
            else:
                print_n_log("Not enough attributes (url/rid/sid/cat/ts) in:", m)
                return False
        return True

    def is_it_actual(self, lfile, hsum, ts):
        if not os.path.isfile(lfile):
            return False
        try:
            lsum = hashlib.md5(open(lfile,'rb').read()).hexdigest()
        except Exception as e:
            print_n_log("Got hashlib exception:", e)
            return False
        if hsum != lsum:
            print_n_log("hash error:", hsum, lsum)
            return False
        else:
            return True

    def local_or_retrieve(self, rid, sid, cat, url, ts, hsum):
        its_local, localfile = self.is_it_localmedia(rid, sid, cat, url, ts)
        if its_local:
            if not self.is_it_actual(localfile, hsum, ts):
                try:
                    os.remove(localfile)
                    self.is_it_localmedia(rid, sid, cat, url, ts)
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        print_n_log("IO error:", e)
                        return False
        return True

    def only_localmedia(self, rid, sid, cat, url, ts, hsum):
        its_local, localfile = self.is_it_localmedia(rid, sid, cat, url, ts, retrieve = False)
        if its_local:
            if self.is_it_actual(localfile, hsum, ts):
                return True
        return False

    def savemedia(self, data):
        sync = 0
        while sync < 3:
            sync += 1
            start_tm = time.time()
            again = "" if sync == 1 else "again"
            print_n_log("Syncing {}...".format(again))
            if not self.check_all_media(data, self.local_or_retrieve):
                continue
            for t in self.threads:
                t['thr'].join()
            if self.check_all_media(data, self.only_localmedia):
                print_n_log("Elapsed synchronization time:", (time.time() - start_tm))
                self.synced = True
                return self.synced
        print_n_log("Synchronization failed")
        self.synced = False
        return self.synced

    def is_synced(self):
        return self.synced

    def playnsave(self, rid, sid, category, url, timestamp):
#    vlc http://dl6.mp3party.net/download/7952427 --vout dummy --sout "#duplicate{dst=std{access=file,mux=raw,dst=OUT.mp3},dst=display" --sout-all
        if (not isinstance(rid, int)) or (not isinstance(sid, int)):
            print_n_log("RouteID and StopID must be INT:", ris, sid)
            return
        its_local, localfile = self.is_it_localmedia(rid, sid, category, url, timestamp)
        item = localfile if its_local else url
        self.playfile(dict(file=item), True if its_local else None)

    def playfile(self, media, cached=None):
        if self.player.is_playing():
            print_n_log("Stop playing")
            self.player.stop()
        sfx = "" if self.options is None else ", options: "+self.options
        pfx = "" if cached is None else "(cached)"
        print_n_log("Play" + pfx + ": " + media['file'] + sfx)
        self.player.set_mrl(media['file']) if self.options is None else self.player.set_mrl(media['file'], self.options)
        self.player.play()
        i = 0
        while (not self.player.is_playing()) and (i < 6):  # wait for start upto 3sec
            time.sleep(0.5)
            i += 1


    def setlabel(self, txt, tag, align, lag = None):
        lab = QLabel(txt, self.info)
        lab.setAlignment(align)
        lab.setStyleSheet(stop_css[tag]['style'])
        lab.setGeometry(stop_css[tag]['geom']['x'], stop_css[tag]['geom']['y'], stop_css[tag]['geom']['w'], stop_css[tag]['geom']['h'])
        lab.setWordWrap(True)
#        f = QFont(BASE_FF)
#        f.setStretch(110) #QFont.SemiExpanded)
#        f.setWeight(800) #QFont.Black)
#        f.setLetterSpacing(QFont.PercentageSpacing, 110)
#        lab.setFont(f)
        lag_lab = None
        if lag is not None:
            lag_lab = QLabel(str(lag)+" хв", self.info)
            lag_lab.setAlignment(Qt.AlignVCenter|Qt.AlignRight)
            lag_lab.setStyleSheet(stop_css[tag]['lag']['style'])
            lag_lab.setGeometry(stop_css[tag]['lag']['geom']['x'], stop_css[tag]['lag']['geom']['y'], stop_css[tag]['lag']['geom']['w'], stop_css[tag]['lag']['geom']['h'])
        return dict(lab=lab, lag=lag_lab)

    def change_display(self, active, inactive):
        for t in self.elems[active]:
            self.elems[active][t]['lab'].show()
            ll = self.elems[active][t].get('lag', None)
            if ll is not None:
                ll.show()
        for t in self.elems[inactive]:
            self.elems[inactive][t]['lab'].hide()
            ll = self.elems[inactive][t].get('lag', None)
            if ll is not None:
                ll.hide()

    def display_stop(self, stop, elem):
        (name, eta) = ('', 0) if stop is None else (stop.get('name', None), stop.get('lag', None))
        if name is not None:
            lab = elem.get('lab', None)
            if lab is not None:
                lab.setText(name.upper())
        if eta is not None:
            lag = elem.get('lag', None)
            if lag is not None:
                eta_txt = '' if name == '' else str(round((eta+0.1)/60))+" хв"
                lag.setText(eta_txt)

    def set_stops(self, tag, stops):
        ina = 'after' if tag == 'at' else 'at'
        if tag == 'at':
            self.display_stop(stops['s1'], self.elems[tag]['up'])
            self.display_stop(stops['s2'], self.elems[tag]['br'])
        elif tag == 'after':
            self.display_stop(stops['s2'], self.elems[tag]['s1'])
            self.display_stop(stops['s3'], self.elems[tag]['s2'])
            self.display_stop(stops['s4'], self.elems[tag]['s3'])
        self.change_display(tag, ina)
        self.info.setStyleSheet(self.bgs[tag])
        self.info.update()

    def set_title(self, text):
        self.route['lab'].setText(text)

    def set_bg(self, tag):
        if tag in self.bgs:
            print_n_log("Set background:", BASE_DIR+self.bgs[tag])
            self.info.setStyleSheet("background-image:url("+BASE_DIR+self.bgs[tag]+");")

class Mqtt:
    def __init__(self, broker, mac, ip, topics):
        self.broker = broker
        self.mac = mac
        self.ip = ip
        self.topics = topics
        self.mqtt = paho.mqtt.client.Client(self.mac, clean_session=False)
        self.mqtt.on_message = self.on_message
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_publish = self.on_publish
        self.mqtt.on_subscribe = self.on_subscribe
        self.mqtt.on_log = self.on_log
        self.mqtt.on_disconnect = self.on_disconnect
        self.skip_logging = MQTT_SKIP_LOGGING
        self.status = STATUS_NA
        self.temperature = STATUS_NA
        self.connected = False
        self.subscribed = False
        self.registered = False
        self.alarm = dict(c=threading.Event(), s=threading.Event(), r=threading.Event())
        self.message_id = 0;
        self.connect()

    def is_connected(self):
        return self.connected
    def is_subscribed(self):
        return self.subscribed
    def is_registered(self):
        return self.registered

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
            self.register()
            self.subscribe()
            station.set_state('connected')

    def register(self, delay = None):
        if delay is not None:
            self.alarm['r'].wait(timeout=delay)
        if self.registered:
            return
        print_n_log("Registering ...")
        data = json.dumps(dict(
            message_id = self.message_id,
            timestamp = int(time.time()),
            type = MQTT_TYPE_REG_REQ,
            mac = self.mac,
            ip = self.ip,
            status = self.status,
            hw_version = HW_VERSION,
            sw_version = PROGNAME+"-"+SW_VERSION,
        ))
        self.mqtt.publish("t_bkts", data)

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

    def pub_status(self):
        data = json.dumps(dict(
            type = MQTT_TYPE_STATUS_RESP,
            mac = self.mac,
            message_id = self.message_id,
            timestamp = int(time.time()),
            status = self.status,
            sw_version = PROGNAME+"-"+SW_VERSION,
            temp = self.temperature,
        ))
        self.mqtt.publish("t_bkts", data)

    def set_status(self, n, status):
        if status is STATUS_NA:
            return
        print("set_status of {}th bit to".format(n), status)
        if self.status is STATUS_NA:
            self.status = 0
        else:
            self.status &= ~(1<<n)
#        print(self.status, status, n, (status<<n))
        self.status |= status<<n  # Nth bit
#        print(self.status)
        self.pub_status()
        print_n_log("STATUS({}) is published".format(self.status))

    def stop_mesg(self, data, prop, warn = None, prfx = None):
        stop = data.get(prop, None)
        if stop is None:
            if warn is not None:
                print_n_log("Message w/o", prop, "property")
            return None
        sid = stop.get('stop_id', None)
        if sid is None:
            if warn is not None:
                print_n_log("Message w/o stop_id:", stop)
            return None
        when = "now" if prfx is None else prfx
        na_url = stop.get(when + '_audio_url', None)
        url = URL_PREFIX + na_url if na_url is not None else None
        if warn:
            print_n_log("return:", dict(sid=sid, rid=stop.get('route_id', None), name=stop.get('ukr', None), lag=stop.get('eta', None), url = url, ts=stop.get(when+'_audio_dttm', None)))
        return dict(sid=sid,
            rid=stop.get('route_id', None),
            name=stop.get('ukr', None),
            lag=stop.get('eta', None),
            url = url,
            ts=stop.get(when + '_audio_dttm', None))

    def on_message(self, mac, data, msg):
#        print_n_log("Got message on", msg.topic, str(msg.payload)) # raw output
        if msg.topic != "t_informer":
            return
#        print_n_log("Got message on", msg.topic, msg.payload.decode("utf-8"))
        print_n_log("Got some message on", msg.topic)
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except:
            print_n_log("JSON: cannot decode this message:", msg.payload.decode("utf-8"))
            return
        mesg_t = data.get('type', None)
        if mesg_t is None:
            print_n_log("Got untyped message")
            return
#        if mesg_t is MQTT_TYPE_REG_REQ: # do nothing
#            print_n_log("Got someone's REG request")
#            return
        if mesg_t is MQTT_TYPE_REG_RESP:
            if self.mac == data.get('mac', None):
                status = data.get('success', None)
                if status is not None:
                    if isinstance(status, int):
                        if status is MQTT_STATUS_OK: # ??? undocumented
                            print_n_log("Registered")
                            self.registered = True
                            station.set_state('registered')
                            self.alarm['r'].set()
                        else:
                            print_n_log("Registration failed: status is", status)
                    else:
                        print_n_log("Registration failed: got untyped status", status)
                else:
                    print_n_log("Registration failed: haven't got any status:", data)
        elif mesg_t is MQTT_TYPE_ROUTE:
            route_info = data.get('route_info', None)
            if route_info is None:
                print_n_log('Got message of type ROUTE_INFO without "route_info" field')
                return
            name = route_info.get('name', None)
            if name is None:    # Mandatory field
                print_n_log('Got message of type ROUTE_INFO without "name" in route_info"')
            else:
                print_n_log('Set TITLE as "{}"'.format(name))
                station.set_title(str(name))
        elif mesg_t is MQTT_TYPE_STATUS_REQ:  # broadcast
            self.pub_status()
            print_n_log("We just published our STATUS({})".format(self.status))
        elif mesg_t is MQTT_TYPE_STATUS_RESP: # do nothing
            print_n_log("Got someone's STATUS response")
        elif mesg_t is MQTT_TYPE_STOP:
            stop1 = self.stop_mesg(data, 'curr_stop_info', warn = True)
            stop2 = self.stop_mesg(data, 'next1_stop_info')
            if stop1 is None:
                print_n_log("Got message w/o 'curr_stop_info/stop_id'")
            else:
                station.set_template('at', dict(s1=stop1, s2=stop2))
                print_n_log("Set stop AT")
        elif mesg_t is MQTT_TYPE_START:
            stop1 = self.stop_mesg(data, 'curr_stop_info', warn = True, prfx = "future")
            stop2 = self.stop_mesg(data, 'next1_stop_info')
            stop3 = self.stop_mesg(data, 'next2_stop_info')
            stop4 = self.stop_mesg(data, 'next3_stop_info')
            if stop1 is None:
                print_n_log("Got message w/o 'curr_stop_info/stop_id'")
            else:
                station.set_template('after', dict(s1=stop1, s2=stop2, s3=stop3, s4=stop4))
                print_n_log("Set stop AFTER")
        elif mesg_t is MQTT_TYPE_MESG: # do nothing
            print_n_log("Got message, type MESG: do nothing")
        elif mesg_t is MQTT_TYPE_MODE: # do nothing
            print_n_log("Got message, type MODE: do nothing")
        elif mesg_t is MQTT_TYPE_SYNC:
            sync_data = data.get('data', None)
            if sync_data is None:
                print_n_log('Got message of type SYNC without "data" field')
                return
            station.set_sync(sync_data)
        else:
            print_n_log("Got unknown message type:", mesg_t, "(do nothing)")

    def on_log(self, mac, data, level, string):
        what = string.split()
        if len(what) == 2:
            for k in self.skip_logging:
                if (what[1] == k): # skip logging
                    return
#        print_n_log("Logged:", string)

    def on_disconnect(self, mac, userdata, rc):
        self.connected = False
        self.subscribed = False
        self.registered = False
        print_n_log("Disconnected:", rc)
        station.set_state('disconnected')

    def close(self):
        self.mqtt.disconnect()
        self.mqtt.loop_stop()
        station.set_state('disconnected')


class UDPLogger(socketserver.BaseRequestHandler):
    global hw_status
    def handle(self):
        self.data = self.request[0].strip().decode("utf-8")
        print_n_log("Got {} bytes from syslog".format(len(self.data)))
        lp, rp = self.data.split("] ")
        data = rp.split()
        if len(data) == 4:  # HDMI HPD State 0x1
            if (data[0] == "HDMI") and (data[2] == "State"):
                try:
                    state = int(data[3], 16)
                except Exception:
                    return
                hw_status.set_hdmi(1 if state != 1 else 0)

def start_hdmi_logger():
    hdmi_logger = socketserver.UDPServer((UDP_LOGGER_HOST, UDP_LOGGER_PORT), UDPLogger)
    hdmi_logger.serve_forever()

def chk_hdmi():
#with open(HDMI_LOG, 'rb') as fh:
#    for line in fh:
#        pass
#    last = line
#print(last)
    try:
        last = subprocess.check_output(['tail', '-1', HDMI_LOG]).decode("utf-8")
        if last[-1:] == '\n':
            last = last[:-1]
        lp, rp = last.split("] ")
        data = rp.split()
        if len(data) == 4:  # HDMI HPD State 0x1
            if (data[0] == "HDMI") and (data[2] == "State"):
                try:
                    state = int(data[3], 16)
                except Exception:
                    return
                hw_status.set_hdmi(1 if state != 1 else 0)
    except: pass


def starter():
    global mqtt, station, player, hw_status
    if mqtt is None:
        return
    if not mqtt.is_connected():
        print_n_log("Reconnect in " + str(MQTT_RECONNECT_TIME) + "sec ...")
        mqtt.connect(MQTT_RECONNECT_TIME)
    elif not mqtt.is_subscribed():
        print_n_log("Resubscribe in " + str(MQTT_RESUBSCRIBE_TIME) + "sec ...")
        mqtt.subscribe(MQTT_RESUBSCRIBE_TIME)
    elif not mqtt.is_registered():
        print_n_log("Reregister in " + str(MQTT_REREGISTER_TIME) + "sec ...")
        mqtt.register(MQTT_REREGISTER_TIME)
    else:
        state, title, template, stops, sync = station.attr()
        if state is not None:
           station.set_state(None)
           player.set_bg(state)

        if player.is_synced():
            if title is not None:
                station.set_title(None)
                player.set_title(title)
            if template is not None:
                station.set_template(None, None)
                player.set_stops(template, stops)
                stop = stops.get('s1', None)
                if stop is not None:
                    rid, sid, url, ts = stop.get('rid', None), stop.get('sid', None), stop.get('url', None), stop.get('ts', None)
                    if all(v is not None for v in (rid, sid, url, ts)):
                        player.playnsave(rid, sid, template, url, ts)
                    elif url is not None:
                        player.playfile(dict(file=url))
                else:
                    print_n_log("Silent stop:", stop)
        else:   # not synced
            if sync is not None:
                station.set_sync(None)
                player.savemedia(sync)

        # hw_status stuff
        if hw_status.is_changed():
            hdmi, audio, temp = hw_status.attr()
            mqtt.set_status(STATUS_HDMI_BIT, hdmi)
#            mqtt.set_status(STATUS_AUDIO_BIT, audio)
#            mqtt.set_status(STATUS_TEMP_BIT, temp)
            hw_status.clr_changed()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(geom['win']['g']['x'], geom['win']['g']['y'], geom['win']['g']['w'], geom['win']['g']['h'])
        self.setStyleSheet(BG_STYLE)
        self.cw = QStackedWidget()
        self.setCentralWidget(self.cw)
        stopby = Stopat(IMAGES, self, options = VLC_OPTIONS)
        self.cw.insertWidget(STOPAT_NDX, stopby)
        self.cw.setCurrentIndex(STOPAT_NDX)
    def getstack(self):
        return self.cw

def get_mac(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', str.encode(ifname[:15])))
    return ''.join(['%02x' % c for c in info[18:24]]).upper()

def get_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', str.encode(ifname[:15])))
    return socket.inet_ntoa(info[20:24])

#try:
#    so = ctypes.CDLL(find_library('X11'))
#except OSError:
#    so = ctypes.CDLL('libX11.so')
#try:
#    so.XInitThreads()
#except:
#    print("Oops, x11")

def run_mqtt():
    global mqtt
    mqtt = Mqtt(MQTT_BROKER, get_mac(IFACE), get_ip(IFACE), MQTT_TOPICS)

if __name__ == "__main__":
    with open(RCFILE, 'r') as rcfile:
        geom = json.load(rcfile)
        if geom is not None:
            init_css()
        else:
            print_n_log('Missed "' + key + '" in ' + RCFILE)
            sys.exit(-1)
    rcfile.close()

    global win
    syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_USER)
    app = QApplication(sys.argv)
    win = MainWindow()
    stack = win.getstack()
    player = stack.widget(STOPAT_NDX)
    station = Station()
    hw_status = HW_Status()
    chk_hdmi()
    win.show()

    timer = QTimer()
    timer.timeout.connect(starter)
    timer.start(1000)

    mqtt_thread = threading.Thread(target=run_mqtt)
    mqtt_thread.start()

    hdmi_logger_thread = threading.Thread(target=start_hdmi_logger)
    hdmi_logger_thread.start()

#    atexit.register(mqtt.close)
    sys.exit(app.exec_())

