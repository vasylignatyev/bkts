#!/usr/bin/python3
#coding=utf-8

import os
import sys
import time
import math
import json
import fcntl
import locale
import struct
import socket
import syslog
import os.path
import platform
import datetime
import threading
import paho.mqtt.client
from queue import Queue
from collections import OrderedDict
from time import localtime, strftime
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QHBoxLayout, QStatusBar, QLabel, QGridLayout, QScrollArea, QFrame, QDialog, QTabBar, QMessageBox, QSizePolicy, QStackedWidget
from PyQt5.QtCore import pyqtSlot, QTimer, QSize, QPoint, QMargins, Qt, QRect, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QMovie, QPen, QColor
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtMultimedia import QSound


PROGNAME = "driver-terminal"
SW_VERSION = "0.51"
HW_VERSION =  platform.machine() + "-" + platform.release().split("-")[-1]

# base
BASE_DIR = "/opt/telecard/"  # base folder

APP_GEOM = QRect(0, 0, 1024, 768)  # APP_GEOM = QRect(1500, 50, 1024, 768)
TAB_WIDTH = (215, 259, 259, 215, 67)
ICON_SIZE = QSize(55, 80)
NMPLACE = dict(point=QPoint(40, 11), size=QSize(23, 23), color="#84c36b")    # place for COUNT indicator

TAB_NAMES = OrderedDict(
    bort=dict(index=0, title="Борт",    tip="Панель виклику, датчики"),
    stop=dict(index=1, title="Зупинки", tip="Графік руху, затримки"),
    desc=dict(index=2, title="Маршрут", tip="Опис маршруту, загальна інформація"),
    gmap=dict(index=3, title="Карта",   tip="Гугл карта руху транспортного засобу"),
    mesg=dict(index=4, title="",        tip="Повідомлення")
)
TAB_NAMES.move_to_end('bort')
TAB_NAMES.move_to_end('stop')
TAB_NAMES.move_to_end('desc')
TAB_NAMES.move_to_end('gmap')
TAB_NAMES.move_to_end('mesg')


# colors/fonts/styles
SBAR_COLOR = dict(bg="white", lag="#d62727", lead="#8ac349")
STOP_COLOR = dict(red="#d62727", green="#8ac349", blue="#0966ae", gray="#818181")
WH_COLOR = ["#f7f3e6", "#efebdd", "#ececec"]
BG_STYLE = "background-color:#e9e6e4;"
FG_STYLE = "color:#444;"
FFAMILY = "font-family:arial,sans-serif;"  # font family
SPRFX = FFAMILY + "font-weight:bold;"
TAB_STYLE = "background-color:white;"
SBAR_ELEM_STYLE = FG_STYLE + SPRFX + "font-size:26px;"
APP_STYLE = "QStatusBar::item { border:0px solid black;}"
SBAR_STYLE = "QStatusBar { background:" + SBAR_COLOR['bg'] + ";}"
TABBAR_STYLE = "background-color: #4c9d86;"
TABWIDGET_STYLE = ("QTabBar::tab {" + BG_STYLE + FG_STYLE + SPRFX +
    "border-top-left-radius:10px; border-top-right-radius:10px;"
    "margin:9px 0 0 9px; height:70px; font-size:27px;}"
    "QTabBar::tab:selected {background-color: #fff;}"
    "QTabWidget::tab-bar {/*left:20px;*/width:9999px;}"
)

SW_LABEL_STYLE = "font-size:18px; color:black;"
MAIN_STYLE = dict(bg="background:qlineargradient(x1:0 y1:0, x2:1 y2:0, stop:0 #56b2b1, stop:1 #aed468);",
    btn="border-radius:20px; background:rgba(0,74,57,0.5); color:white; font-size:27px; font-weight:bold;",
    cnt=SPRFX + "font-size:105px;", col1="color:#77fffe;",
    col2="color:#c8ff89;", col3="color:#ff8989;")
NMSG_STYLE = dict(date="border-top-left-radius:5px; border-bottom-left-radius:5px; font-size:26px; font-weight:bold; margin:3px 3px 3px 0;" + FG_STYLE,
    title="border-top-right-radius:5px; font-size:30px; margin:3px 0 0 3px;" + FG_STYLE,
    mesg="border-bottom-right-radius:5px; font-size:23px; margin:0 0 3px 3px;" + FG_STYLE)
NMSG_COLOR = dict(date=(WH_COLOR[1], "#72bd79"), title=(WH_COLOR[0], "#d6efbb"), mesg=(WH_COLOR[0], "#d6efbb"))
MESG_POPUP_STYLE = dict(dlg="border-radius:12px; background-color:#fffbed;",
    title=SPRFX+"font-size:24px; qproperty-alignment:AlignTop; qproperty-wordWrap:true;",
    body=FFAMILY+"font-size:30px; qproperty-alignment:AlignTop; qproperty-wordWrap:true;",
    date=FFAMILY+"font-size:20px; qproperty-alignment:AlignJustify;",
    btn_ok="QPushButton {"+
        SPRFX+"font-size:26px; border-radius:5px; background:#4c9d5d; color:#fff;"
    "}"
    "QPushButton:pressed {"
        "background:#2c7d3d; border-left:2px solid white; border-top:2px solid white; border-style:outset;"
    "}",
    btn_all="QPushButton {"+
        SPRFX+"font-size:26px; border-radius:5px; background:#d8d8d8; color:#2c2c2c;"
    "}"
    "QPushButton:pressed {"
        "background:#b8b8b8; border-left:2px solid white; border-top:2px solid white; border-style:outset;"
    "}",
)
TRANSPARENT_BG = "background:transparent;"

BORT_STYLE = "background:qlineargradient(x1:0 y1:0, x2:1 y2:0, stop:0 #a1d1d1, stop:1 #cfe2ab); background-repeat:no-repeat; background-position:center;"
BORT_BTN_STYLE_BASE="border-radius:5px; color:" + WH_COLOR[0] + "; font-size:19px; font-weight:bold; margin-bottom:9px;"
BORT_BTN_STYLE = dict(
    bg_gr="QPushButton {"+
        BORT_BTN_STYLE_BASE+
        "background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #55b271, stop:1 #168b58);"
    "}"
    "QPushButton:pressed {"+
        BORT_BTN_STYLE_BASE+
        "background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #168b58, stop:1 #55b271);"
        "border-left:2px solid white; border-top:2px solid white; border-style:outset;"
    "}",
    bg_rd="QPushButton {"+
        BORT_BTN_STYLE_BASE+
        "background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #c87858, stop:1 #c03232);"
    "}"
    "QPushButton:pressed {"+
        BORT_BTN_STYLE_BASE+
        "background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:1 #c87858, stop:0 #c03232);"
        "border-left:2px solid white; border-top:2px solid white; border-style:outset;"
    "}",
    )
STOP_STYLE = dict(name=SPRFX + "font-size:26px;", delay=SPRFX + "font-size:36px;")
DESC_STYLE = dict(item=SPRFX + "font-size:24px;" + FG_STYLE, desc=FFAMILY + "font-size:24px;" + FG_STYLE)
REGMSG_STYLE = FFAMILY+"font-size:120px; qproperty-alignment:AlignTop; qproperty-wordWrap:true; color:white;"


# images/media
IMAGE_DIR = BASE_DIR + "images/"  # image folder
TAB_ICO_PRFX = "ico50x70-"
TAB_ICO_SFFX = dict(selected="_a.png", unselected="_p.png")
SBAR_ICO = dict(logo=IMAGE_DIR+"logo00.png", clock=IMAGE_DIR+"ico-time0.png")
STOP_ICO = dict(top=IMAGE_DIR+"a2.png", between=IMAGE_DIR+"b2.png", bottom=IMAGE_DIR+"c2.png", bort=IMAGE_DIR+"bus_g0.png")
RT_SEP = IMAGE_DIR + "rt-sep1.png"
BORT_ICO = dict(prfx=IMAGE_DIR+"ico-vh-btn", bort=IMAGE_DIR+"bus07.png")
REGWIN = dict(ico=IMAGE_DIR+"card03.jpg", text="Очікування<br>реєстрації") #Зареєструйтесь,<br>будь ласка!")
SBAR_HEIGHT = 48
SBAR_MARGINS = dict(driver=QMargins(30, 0, 45, 0), route=QMargins(40, 0, 55, 0),
    clock=QMargins(10, 2, 0, 2), delay=QMargins(10, 0, 75, 0), time=QMargins(15, 0, 40, 0),
    logo=QMargins(0, 0, 0, 0))
NEW_MESG_BEEP = IMAGE_DIR + "beep2.wav"
BEEP = IMAGE_DIR + "beep1.wav"


# misc settings
TAB_NDX = 0 # work mode
REG_NDX = 1 # wait mode

DEFAULT_TAB = 0
STAT_TAB = 0  # 0 - Статуси
STOP_TAB = 1  # 1 - Зупинки
DESC_TAB = 2  # 2 - Опис
GMAP_TAB = 3  # 3 - Карта
MESG_TAB = 4  # 4 - Повідомлення

PANE_PAD = 9  # pane paddings
ROUTE_SH = (32, 35)  # tab route: stretches
STOP_SH = (1, 4, 2, 2)  # tab stop: stretches, vertical spacing
STOP_VS = 2
GREY_LAG = -100  # lag minimum

BORT_BTN = ("Розпочати рейс", "Тривога", "Викликати оператора")

# 11 sensors
SENSORS = 11
SENSOR_STATE = [-2]*SENSORS # default states: -1 unknown
SENSOR_ICO = (  # sensor icons
    dict(ico=IMAGE_DIR+'modem.png',           pos=QPoint(620, 70),  ds=QPoint(13, 6)),
    dict(ico=IMAGE_DIR+'gps.png',             pos=QPoint(830, 54),  ds=QPoint(-3, 23)),
    dict(ico=IMAGE_DIR+'speaker.png',         pos=QPoint(143, 176), ds=QPoint(10, 0)),
    dict(ico=IMAGE_DIR+'info-screen.png',     pos=QPoint(310, 176)),
    dict(ico=IMAGE_DIR+'speaker.png',         pos=QPoint(625, 176), ds=QPoint(10, 0)),
    dict(ico=IMAGE_DIR+'ikts.png',            pos=QPoint(824, 176), ds=QPoint(10, 0)),
    dict(ico=IMAGE_DIR+'mobile-terminal.png', pos=QPoint(150, 268), ds=QPoint(5, 0)),
    dict(ico=IMAGE_DIR+'validator-new.png',   pos=QPoint(300, 268)),
    dict(ico=IMAGE_DIR+'validator-new.png',   pos=QPoint(450, 268)),
    dict(ico=IMAGE_DIR+'validator-new.png',   pos=QPoint(600, 268)),
    dict(ico=IMAGE_DIR+'bkts.png',            pos=QPoint(790, 265)),
)

MAX_MESSAGES = 20  # notetab: max messages
MESSAGE_FILE = BASE_DIR + "messages.json"
READ_MESG   = 0
UNREAD_MESG = 1

## misc
IFACE = "eth0"
SW_TIMEOUT = 2

## mqtt
MQTT_BROKER = "localhost"
MQTT_RTOPIC = [("t_driver", 1)]
MQTT_WTOPIC = "t_bkts"
MQTT_RECONNECT_TIME = 60
MQTT_REREGISTER_TIME = 60
MQTT_RESUBSCRIBE_TIME = 60

MQTT_TYPE_STATUS     = 1
MQTT_TYPE_REFUNDMODE = 40   # Mode: refund (what the heck)
MQTT_TYPE_WORKMODE   = 41   # Mode: work
MQTT_TYPE_REGMODE    = 42   # Mode: registration
MQTT_TYPE_WAITMODE   = 43   # Mode: wait
MQTT_TYPE_CHKMODE    = 44   # Mode: check
MQTT_TYPE_MODES = (MQTT_TYPE_REFUNDMODE, MQTT_TYPE_WORKMODE, MQTT_TYPE_REGMODE, MQTT_TYPE_WAITMODE, MQTT_TYPE_CHKMODE)
MQTT_TYPE_STATUSBAR  = 50
MQTT_TYPE_REG_REQ    = 200
MQTT_TYPE_REG_RESP   = 200
#MQTT_TYPE_ROUTE      = 201
#MQTT_TYPE_STOP       = 220  # at stop
#MQTT_TYPE_START      = 221  # after
MQTT_TYPE_MESSAGE    = 230
MQTT_TYPE_ROUTE_DESC = 240
MQTT_TYPE_EVENT      = 250
MQTT_TYPE_GPS_INFO   = 310
MQTT_TYPE_STARTLEG   = 320 # ???
MQTT_TYPE_SCHEDULE   = 330 # [dict(name="", schedule=-1000, lag=-1000)] *9)
MQTT_TYPE_EQUIPMENT  = 340
MQTT_STATUS_OK        = 0
MQTT_STATUS_ERR       = 1
MQTT_STATUS_UNAVAIL   = 2
MQTT_STATUS_FAULT     = 3
MQTT_STATUS_COLLISION = 7

MQTT_MODE_RANGE = range(MQTT_TYPE_REFUNDMODE, MQTT_TYPE_CHKMODE + 1)

MQTT_SKIP_LOGGING       = ("PINGREQ", "PINGRESP")

# Queue element types
QTYPE_MODE       = 1    # mqtt -> qt
QTYPE_ROUTE      = 2
QTYPE_GPS_INFO   = 3
QTYPE_STATUSBAR  = 4
QTYPE_SCHEDULE   = 5
QTYPE_ROUTE_DESC = 6
QTYPE_EQUIPMENT  = 7
QTYPE_QT_MESSAGE = 8
QTYPE_MQTT_MESSAGE = 20 # qt -> mqtt
QTYPE_EVENT        = 21

QTYPE_WIN_RANGE = range(QTYPE_GPS_INFO, QTYPE_QT_MESSAGE + 1)
QTYPE_MQTT_RANGE = range(QTYPE_MQTT_MESSAGE, QTYPE_EVENT + 1)

GPS_TRACKING = False

### data
win = None
mqtt = None
share = None
share_lock = threading.RLock()
mqtt_reregister_time = 1

### complementary funcs

def fmt_datetime():
    return strftime("[%Y-%m-%d %H:%M:%S]", localtime())

def print_n_log(*args):
    print(fmt_datetime(), *args)
    s = '['+PROGNAME.upper()+'] '
    s += "".join(" "+str(a) for a in args)
    syslog.syslog(s)

class Share(Queue):
    def put(self, itype, item):
        with share_lock:
            super(Share, self).put(dict(type=itype, item=item))
        timer.timeout.emit()

class Label05(QLabel):
    def __init__(self, parent, status, align):
        QLabel.__init__(self, parent, alignment=align)
        self.status = status

    def paintEvent(self, ev):
        if self.status in range(-1,2): # -2: hide
            painter = QPainter(self)
            painter.setOpacity(1 if self.status is 1 else 0.5)
            painter.drawPixmap(QPoint(0, 0), self.pixmap())
            painter.end()

    def setStatus(self, status):
        self.status = status
        if self.status is -2:
            self.hide()
        else:
            self.show()

html = '''
<html><head></head><body>
<script src="http://maps.googleapis.com/maps/api/js?libraries=geometry"></script>
<script>
        var stop0 = new google.maps.LatLng(50.400812, 30.651314);
//        var center0 = new google.maps.LatLng(50.4055, 30.654);
        var center0 = stop0;
        var stops = [ [ // forward
{ lat:50.400812, lng:30.651314, title:"ст. м. Харківська (кінцева)", delay:"0 min"},
{ lat:50.402266, lng:30.651657, title:"Ринок (на вимогу)",   delay:"1 min"},
{ lat:50.406364, lng:30.649954, title:"вул. Кошиця",         delay:"2 min"},
{ lat:50.410461, lng:30.647461, title:"вул. Олійника",       delay:"3 min"},
{ lat:50.414490, lng:30.644903, title:"вул. Тростянецька",   delay:"4 min"},
{ lat:50.416416, lng:30.643942, title:"Магазин (на вимогу)", delay:"5 min"},
{ lat:50.419909, lng:30.641861, title:"вул. Російська",      delay:"6 min"},
{ lat:50.424359, lng:30.644092, title:"вул. Новодарницька",  delay:"7 min"},
{ lat:50.423042, lng:30.644088, title:"ш. Харківське",       delay:"8 min"},
], [    // reverse
{ lat:50.423042, lng:30.644088, title:"ш. Харківське",       delay:"9 min"},
{ lat:50.422324, lng:30.641159, title:"вул. Ревуцького",     delay:"10 min"},
{ lat:50.419878, lng:30.641198, title:"вул. Російська",      delay:"11 min"},
{ lat:50.415848, lng:30.643302, title:"Озеро Сонячне",       delay:"12 min"},
{ lat:50.412012, lng:30.645662, title:"вул. Анни Ахматової", delay:"13 min"},
{ lat:50.410364, lng:30.646690, title:"вул. Олійника",       delay:"14 min"},
{ lat:50.406275, lng:30.649104, title:"вул. Кошиця",         delay:"15 min"},
{ lat:50.403116, lng:30.651132, title:"ст. м. Харківська",   delay:"16 min"},
{ lat:50.400812, lng:30.651314, title:"ст. м. Харківська (кінцева)", delay:"17 min"},
]]

        var directions = new google.maps.DirectionsService();
        var bounds;
        var map;

        function map_stops(stop, len, icol, ecol) {
            var erender = new google.maps.DirectionsRenderer({
                suppressMarkers: true,
                polylineOptions: {
                    strokeColor: ecol,
                    strokeWeight: 7
                },
                map: map
            });
            var irender = new google.maps.DirectionsRenderer({
                suppressMarkers: true,
                polylineOptions: {
                    strokeColor: icol,
                    strokeWeight: 4
                },
                map: map
            });
            bounds = new google.maps.LatLngBounds();
            var request = {
                origin: { lat:stop[0].lat, lng:stop[0].lng},
                destination: { lat:stop[len-1].lat, lng:stop[len-1].lng},
                travelMode: google.maps.TravelMode.DRIVING,
                waypoints: []
            }
            var info = new google.maps.InfoWindow();
            for (i = 0; i < len; i++) {
                var marker = new google.maps.Marker({
                    position: { lat:stop[i].lat, lng:stop[i].lng},
                    title: stop[i].title,
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        strokeWeight: 2.7,
                        strokeOpacity: 0.8,
                        fillColor: "#fff",
                        fillOpacity: 1,
                        scale: 4.7
                    },
                    map: map
                });
                bounds.extend(marker.position);
                (function(m, s) {
                    google.maps.event.addListener(marker, "click", function (e) {
                        info.setContent(s.title + ", " + s.delay);
                        info.open(map, m);
                    });
                })(marker, stop[i]);
            }
            for (i = 1; i < len - 1; i++) {
                request.waypoints.push({
                    location: { lat:stop[i].lat, lng:stop[i].lng},
                    stopover: true
                });
            }
            directions.route(request, function(result, status) {
                if (status == google.maps.DirectionsStatus.OK) {
                    erender.setDirections(result);
                    irender.setDirections(result);
                }
            });
        }

        var bus;
        var defZoomLevel = 17;
        function moveBus(lat, lng) {
            var pos = new google.maps.LatLng(lat, lng);
            if (pos.equals(stop0)) {
                map.setCenter(center0);
                map.setZoom(defZoomLevel);
            }
            if (!map.getBounds().contains(pos)) {
                map.panTo({lat:pos.lat(), lng:pos.lng()});
            }
            bus.setPosition(pos);
        };

        window.onload = function() {
            map = new google.maps.Map(document.getElementById("drv-map"), {
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                zoom: defZoomLevel,
            });
            map_stops(stops[0], stops[0].length, "#00b3fd", "#1f7cb6");
            map_stops(stops[1], stops[1].length, "#ff9e00", "#ac7413");
            google.maps.event.addListenerOnce(map, 'bounds_changed', function() {
                map.setZoom(defZoomLevel);
                map.setCenter(center0);
            });
            bus = new google.maps.Marker({
                position: { lat:stops[0][0].lat, lng:stops[0][0].lng},
                title: 'Bus #7218',
                icon: {
                    url:"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAbCAYAAABiFp9rAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4QgIDAgAJctyxQAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAAE+ElEQVRIx7WWf0zUZRzHX8/3vnccyN0B8lOkEAV/jASxmOSQX6UUkqbmLHM5U8zGajbbqlWrPzJq003TaaitJaQzGxN/DGuKxlTUQYoURmoISAnHr7sDjrv73rc/kJ9yaG69n/+ez+fzvD8/n+cReMKyJDh8AVbMjcHomwHaFFQRAcLYp6BaEGoDOM/Saj3Jj+dvDdiMAuGRaEVyDCbT5zqdedy6pzrUtQnX6+LD8UGPHwB2Oq7coXtv5bRJ+Zf9cDoCu+jsfJ+DZbUPJoqPhCt1iA3PfShruzMPLb9cvzihOxgHKqB6cEmgQxRV+txdfijxccWhP6buLsnrP+t+oj6BJDYs3D816Ka+5oMaHXa8+C/Q0zt98wzHHy1RdnXXsVXER7r7yYZH9EZWYWrUBXtpblsEDh4NOkjbEdBw5laSnt3HV/ZvSwOh5czfGDnebCrNbQt/ZBIAB5TmtoVHBrQYRc78jYOpS4uDIMNk/HV71S2nW3FhHGbojbu5Aa/i4/jfbkRvtSErCui9UAPH40iIw/ZsNu10IQ2rogar2JQeQLtjLS3Wm32py3n+m22LLnm/NdccOLToioJIySL+XDmBYwUhy6iFe/h1+VJacQ/Wf/u5QPPbRxJ7yD+xRpA5O5wo3wJ1y9leegdTCfBpHhGf5DHtYTImSaiKQgmdyAObXijinVQf6qyvyEQEZL42658eHOhgiD+AuRWd0YBzy2fU2Hs9z9ylCkz7D/LYKPXSrpzVZit0hjwjI7zmrZt9rRGVyFHOUPV63GtzacKCxhNRvg51VCIV9+uzqpoKKxZmSKgicu5kDPxPSIvBF0VMlEEY0dLhqaUVBdHwO942m+eImpvReWTS4o0Qxj4iDVpPem3t6KYkkDyW1273WF2CjBD+Mrjv0IsFCBhNT1XB6URSPdx0Oh1ul2t4tw5DL1ZUd5MEWNssWMeakXMnKS8qoGKkLCmR1ltXKFuSTZMn+1YLFgQWCeGs3nEx1H/Ua1kCWcb9ZAK2+Jl0jZQHB9EbPp3uieH0eCL66mJYMDirJRSlqPBqsBPNkEG7h+QkOu12NIFRpMTO4emR8uITTAgOIn3nHqKiJ2NFGTFrGuQDVUF2FKVIZt/P5bXrs7dbbFXXjd6EDtV7aRXNhlycFgvapERaJ4RhH5ZWDeqxEkIVBZGzmnpGdKbVRkPt3cgn2Fdc3heF0rvzxe9jF5/KqZZRcA0ZOGEw4LLa0G7+mBupKViGeeyDO24mhqrfMIWG4BwZTXZBrBHFvm34e7Q+u6xkTentBVNtIf0Xq6qC8EMBVKzIjNbGBhQkVLrQ4Bo4T/xU69u8YF9aOF8fTR0kWp0OkhSIJJ/4+6OS2hATIcLz0z0mVBB1Zlqi8jKn4HZl4VJa+K50RPFeTp6Hj+6La5vO3IgNU8JGXrIPhEBz7Y6mcebW1Gi6HO9xoOyXwUwORXX9bSKDK3ddjVtl1JtvJkX3GO7rJM9PuPrlqYD6pfszZmBuf5Mfzl988HdrdXogXvqt3t5dYQXLLjQvSXCYcKFHvbf6LPuWjL2oUtf56uGkkO7ucQ047O/y7Wnzw/3r0uKg9CrkZJ2StR0x2VNthhdm/NU5e6Jb4zPOrQfo7pLsFY2ScrRmkqn4uq/V5fSrJf94xoDtQ38gARbNgSPlkLNgA6pmEUjRIPT3ym4H958I5Qj5J3cN6HrAv9if6YkC6xivAAAAAElFTkSuQmCC",
                    anchor: new google.maps.Point(13, 14)
                },
                optimized: false,
                zIndex:999,
                map: map
            });
        }
</script>
<div id="drv-map" style="width: 100%; height: 100%;"></div>
</body>
</html>
'''

class BortTab():
    def __init__(self, tab):
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(PANE_PAD, PANE_PAD, PANE_PAD, 0)
        self.icons = [None]*SENSORS
        self.states = [None]*SENSORS
        self.status = SENSOR_STATE

        for i, v in enumerate(BORT_BTN):
            b = QPushButton(" " + v)
            b.setFixedSize(320, 80)
            b.setStyleSheet(BORT_BTN_STYLE['bg_rd'] if i % 2 else BORT_BTN_STYLE['bg_gr'])
            b.setIcon(QIcon(BORT_ICO['prfx'] + str(i + 1) + ".png"))
            b.setIconSize(QSize(28, 28))
            if i is 0:
                align = Qt.AlignLeft
            elif i is len(BORT_BTN) - 1:
                align = Qt.AlignRight
            else:
                align = Qt.AlignHCenter
            b.clicked.connect(lambda e, i=i: self.send_event(e, i))
            self.grid.addWidget(b, 0, i, alignment=align)

        self.bort = QWidget()
        self.bort.setStyleSheet(BORT_STYLE + "background-image:url(" + BORT_ICO['bort'] + ");")
        for i, v in enumerate(SENSOR_ICO):
            self.init_sensors(i, v)
        self.grid.addWidget(self.bort, 1, 0, 1, 3)
        tab.setLayout(self.grid)

    def update(self, dev):
        for d in dev:
            tid, state = d.get('type'), d.get('state')
            if tid in range(0, SENSORS):
                self.sensor(tid, state)

    def send_event(self, ev, ev_id):
        QSound.play(BEEP)
        share.put(QTYPE_EVENT, ev_id)

    def init_sensors(self, i, ico):
        s = self.status[i]
        PAD = (40, 130)
        self.icons[i] = Label05(self.bort, s, Qt.AlignTop|Qt.AlignLeft)
        self.icons[i].setStyleSheet(TRANSPARENT_BG)
        lico = QPixmap(ico['ico'])
        self.icons[i].setPixmap(lico)
        self.icons[i].move(ico['pos'])

        self.states[i] = QLabel(self.bort, alignment=Qt.AlignTop|Qt.AlignLeft)
        self.states[i].setStyleSheet(TRANSPARENT_BG)
        sico = QPixmap(IMAGE_DIR + "sensor-" + ("ok" if s is 1 else "no") + ".png")
        self.states[i].setPixmap(sico)
        ds = ico.get('ds')
        dx = 0 if ds is None else ico['ds'].x()
        dy = 0 if ds is None else ico['ds'].y()
        self.states[i].move(QPoint(ico['pos'].x() + lico.width() - sico.width() / 2 + dx, ico['pos'].y() - sico.height() / 2 + dy))
        self.sensor(i)

    def sensor(self, i, state = None):
        if state is not None:
            self.status[i] = state
        s = self.status[i]
        self.icons[i].setStatus(s)
        if s < -1:
            self.icons[i].hide()
        else:
            self.icons[i].show()
        self.icons[i].update()
        self.states[i].setPixmap(QPixmap(IMAGE_DIR + "sensor-" + ("ok" if s is 1 else "no") + ".png"))
        if s < 0:
            self.states[i].hide()
        else:
            self.states[i].show()


class StopTab():
    def __init__(self, tab, data = None):
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content = QWidget()
        self.grid = QGridLayout()
        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setHorizontalSpacing(0)
        self.grid.setVerticalSpacing(STOP_VS)
        for i, v in enumerate(STOP_SH):
            self.grid.setColumnStretch(i, v)
        content.setLayout(self.grid)
        scroll.setWidget(content);
        layout.addWidget(scroll)
        tab.setLayout(layout)
        self.update(data)

    def update(self, data):
        if data is None:
            return
        while self.grid.count():
            self.grid.takeAt(0).widget().deleteLater()
        self.fill_line(0, data[0], STOP_ICO['top'])
        for i, v in enumerate(data[1:-1]):
            self.fill_line(i + 1, v, STOP_ICO['between'])
        l = len(data) - 1
        self.fill_line(l, data[l], STOP_ICO['bottom'])

    def fill_line(self, i, v, ico):
        stopname = v.get('name')
        if stopname is None:
            return
        if not isinstance(stopname, str):
            return
        schedule = v.get('schedule')
        if schedule is None:
            return
        if not isinstance(schedule, int):
            return
        lag = v.get('lag')
        if lag is None:
            return
        if not isinstance(lag, int):
            return
        lmg = QLabel()
        lmg.setPixmap(QPixmap(ico))
        col = self.fill_elem(lmg, i, 0)
        ttl = QLabel(stopname)
        col = self.fill_elem(ttl, i, col, align=Qt.AlignLeft, style=STOP_STYLE['name'])

        if schedule == 0:
            dl1 = QLabel()
            dl1.setPixmap(QPixmap(STOP_ICO['bort']))
            fc = None
        elif schedule < GREY_LAG:
            dl1 = QLabel('--')
            fc = STOP_COLOR['gray']
        else:
            dl1 = QLabel(str(schedule) + 'хв')
            fc = STOP_COLOR['red'] if schedule < 0 else STOP_COLOR['blue']
        col = self.fill_elem(dl1, i, col, fc=fc, style=STOP_STYLE['delay'])

        (ql, fc) = ('--', STOP_COLOR['gray']) if lag < GREY_LAG else (
            str(lag) + 'хв', STOP_COLOR['green'] if lag is 0 else (
                STOP_COLOR['red'] if lag < 0 else STOP_COLOR['blue']))
        dl2 = QLabel(ql)
        col = self.fill_elem(dl2, i, col, fc=fc, style=STOP_STYLE['delay'])

    def fill_elem(self, item, row, col, align=Qt.AlignHCenter, fc=None, style=""):
        fg = FG_STYLE if fc is None else "color:" + fc + ";"
        item.setAlignment(align | Qt.AlignVCenter)
        item.setStyleSheet(style + fg + BG_STYLE)
        item.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.grid.addWidget(item, row, col)
        return (col + 1)


class DescTab():
    def __init__(self, tab, data = None):
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content = QWidget()
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(PANE_PAD, PANE_PAD, PANE_PAD, 0)
        for i, v in enumerate(ROUTE_SH):
            self.grid.setColumnStretch(i, v)
        content.setLayout(self.grid)
        scroll.setWidget(content);
        layout.addWidget(scroll)
        tab.setLayout(layout)
        self.update(data)

    def update(self, data):
        if data is not None:
            while self.grid.count():
                self.grid.takeAt(0).widget().deleteLater()
            for i, v in enumerate(data[0:-1]):
                self.fill_line(i * 2, v)
            l = len(data) - 1
            self.fill_line(l * 2, data[l], last=True)
 
    def fill_line(self, i, v, last=False):
        if not isinstance(v, dict):
            return
        if (not 'item' in v) or (not 'desc' in v):
            return
        padt = PANE_PAD if i is 0 else 1
        padb = PANE_PAD if last is True else 1
        pad = "padding-top:" + str(padt) + ";padding-bottom:" + str(padb) + ";"
        item = QLabel(v['item'])
        item.setStyleSheet(DESC_STYLE['item'] + BG_STYLE + pad + "padding-left:" + str(APP_GEOM.width() / 5 + 10) + ";")
        self.grid.addWidget(item, i, 0)
        desc = QLabel(v['desc'])
        desc.setStyleSheet(DESC_STYLE['desc'] + BG_STYLE + pad)
        self.grid.addWidget(desc, i, 1)
        if last is False:
            dl = QLabel()
            dl.setPixmap(QPixmap(RT_SEP))
            dl.setStyleSheet(BG_STYLE)
            dl.setAlignment(Qt.AlignCenter);
            self.grid.addWidget(dl, i + 1, 0, 1, 2)


class GmapTab():
    def __init__(self, tab):
        self.webmap = QWebView()
        self.webmap.setHtml(html)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.webmap)
        tab.setLayout(layout)
    def update(self, data):
        self.webmap.page().mainFrame().evaluateJavaScript("moveBus(" + str(data['lat'])  + "," + str(data['lon']) + ")")


class MesgTab():
    def __init__(self, tab, tabbar):
        self.tabbar = tabbar
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(PANE_PAD, PANE_PAD, PANE_PAD, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content = QWidget()
        content.setContentsMargins(0, 0, 0, 0)
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.archive = []
        self.load_messages()
        self.update()
        content.setLayout(self.grid)
        scroll.setWidget(content);
        layout.addWidget(scroll)
        tab.setLayout(layout)

    def update(self):
        lm = len(self.archive)
        if lm is 0:
            return
        if lm > MAX_MESSAGES:
            self.archive.pop(0)
        while self.grid.count():
            self.grid.takeAt(0).widget().deleteLater()
        for i, m in enumerate(self.archive[::-1]):
            self.fill_line(i, m)
        empty = QWidget()
        empty.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.grid.addWidget(empty)
        self.tabbar.update()
        self.save_messages()

    def fill_line(self, i, m):
        h = 130;
        j = 2 * i
        l1 = self.fill_elem(m, QSize(192, h), 'date', 'center')
        self.grid.addWidget(l1[0], j, 0, 2, -1)
        l2 = self.fill_elem(m, QSize(800, h / 3), 'title')
        self.grid.addWidget(l2[0], j, 1)
        l3 = self.fill_elem(m, QSize(800, h - h / 3), 'mesg')
        self.grid.addWidget(l3[0], j + 1, 1)
        if m['status'] is UNREAD_MESG:
            el = (l1, l2, l3)
            for l, t in el:
                l.mousePressEvent = lambda ev: self.mesg_uncheck(ev, i, el)

    def fill_elem(self, m, sz, tag, align=None):
        txt = m[tag]
        if align is not None:
            txt = '<p align=' + align + '>' + str(txt) + '</p>'
        l = QLabel(txt)
        l.setStyleSheet(NMSG_STYLE[tag] + "background:" + NMSG_COLOR[tag][m['status']] + ";")
        l.setFixedSize(sz)
        l.setWordWrap(True)
        return (l, tag)

    def mesg_uncheck(self, ev, i, el):
        ndx = len(self.archive) - 1 - i
        if self.archive[ndx]['status'] == UNREAD_MESG: # mark as read if its's unread
            self.archive[ndx]['status'] = READ_MESG
            for l, t in el:
                l.setStyleSheet(NMSG_STYLE[t] + "background:" + NMSG_COLOR[t][0] + ";")
                l.mousePressEvent = None
            QSound.play(BEEP)
            self.tabbar.update()
            share.put(QTYPE_MQTT_MESSAGE, self.archive[ndx]['mesg_id'])
            self.save_messages()

    def save_messages(self):
        print_n_log("Save messages to", MESSAGE_FILE)
        try:
            with open(MESSAGE_FILE, 'w') as f:
                json.dump(self.archive, f, ensure_ascii=False)
        except IOError as e:
            print_n_log(e)

    def load_messages(self):
        print_n_log("Load messages from", MESSAGE_FILE)
        try:
            with open(MESSAGE_FILE, 'r') as f:
                try:
                    self.archive = json.load(f)
                except Exception as e:
                    print_n_log(e)
        except IOError as e:
            print_n_log(e)

def local_exec():
    global mqtt, share, win, mqtt_reregister_time
    if mqtt is None:
        return
    if not mqtt.is_connected():
        print_n_log("Reconnect in " + str(MQTT_RECONNECT_TIME) + "sec ...")
        mqtt.connect(MQTT_RECONNECT_TIME)
    elif not mqtt.is_subscribed():
        print_n_log("Resubscribe in " + str(MQTT_RESUBSCRIBE_TIME) + "sec ...")
        mqtt.subscribe(MQTT_RESUBSCRIBE_TIME)
    elif not mqtt.is_registered():
        print_n_log("Reregister in " + str(mqtt_reregister_time) + "sec ...")
        mqtt.register(mqtt_reregister_time)
        if mqtt_reregister_time < MQTT_REREGISTER_TIME:
            mqtt_reregister_time *= 2
        if mqtt_reregister_time > MQTT_REREGISTER_TIME:
            mqtt_reregister_time = MQTT_REREGISTER_TIME
    else:
        while not share.empty():
            elem = share.get()
            if elem['type'] is QTYPE_MODE:
                if elem['item'] in MQTT_MODE_RANGE:
                    win.set_mode(elem['item'])
                else:
                    print_n_log("Unknown mode:", elem['item'])
            elif elem['type'] in QTYPE_WIN_RANGE:
                win.data_update(elem)
            elif elem['type'] in QTYPE_MQTT_RANGE:
                mqtt.data_update(elem)
            else:
                print_n_log("Unknown element type", elem['type'])


####################################################################################

class Mqtt:
    def __init__(self, broker, mac, topics):
        self.broker = broker
        self.mac = mac
        self.topics = topics
        self.mqtt = paho.mqtt.client.Client(self.mac, clean_session=False)
        self.mqtt.on_message = self.on_message
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_publish = self.on_publish
        self.mqtt.on_subscribe = self.on_subscribe
        self.mqtt.on_log = self.on_log
        self.mqtt.on_disconnect = self.on_disconnect
        self.skip_logging = MQTT_SKIP_LOGGING
        self.status = MQTT_STATUS_OK
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

    def register(self, delay = None):
        if delay is not None:
            self.alarm['r'].wait(timeout=delay)
        if self.registered:
            return
        print_n_log("Registering ...")
        self.publish(dict(
            type = MQTT_TYPE_REG_REQ,
            status = self.status,
            hw_version = HW_VERSION,
            sw_version = PROGNAME+"-"+SW_VERSION,
        ))

    def subscribe(self, delay = None):
        if delay is not None:
            self.alarm['s'].wait(timeout=delay)
        if self.subscribed:
            return
        print_n_log("Subscribing to topics", self.topics, "...")
        self.mqtt.subscribe(self.topics)

    def on_subscribe(self, mac, data, mid, granted_qos):
        print_n_log("Subscribed (mid={}, qos={})".format(mid, granted_qos))
        self.subscribed = True
        self.alarm['s'].set()

    def publish(self, data, external_mid = None):
        mesg = data
        mesg['mac'] = self.mac  # mandatory fields
        if external_mid is None:
            mesg['message_id'] = self.message_id
            self.message_id += 1
        else:
            mesg['message_id'] = external_mid
        mesg['timestamp'] = int(time.time())
        json_data = json.dumps(mesg)
        (re, local_mid) = self.mqtt.publish(MQTT_WTOPIC, json_data)
        print_n_log("Publish to {} (mid {}): {}".format(MQTT_WTOPIC, local_mid, json_data))

    def data_update(self, elem):
        if elem['type'] is QTYPE_MQTT_MESSAGE:
            self.publish(dict(type=MQTT_TYPE_MESSAGE, mesg_id=elem['item']))
        elif elem['type'] is QTYPE_EVENT:
            self.publish(dict(type=MQTT_TYPE_EVENT, event_id=elem['item']))

    def on_publish(self, mac, data, local_mid):
        print_n_log("Published (mid {})".format(local_mid))

    def pub_status(self, external_mid):
        self.publish(dict(
            type = MQTT_TYPE_STATUS,
            status = self.status,
            sw_version = PROGNAME+"-"+SW_VERSION,
#            temp = self.temperature,
        ), external_mid)

    def schk(self, v):
        if v is not None:
            if not isinstance(v, str):
                v = None
        return v
    def ichk(self, v):
        if v is not None:
            if not isinstance(v, int):
                v = None
        return v
    def fchk(self, v):
        if v is not None:
            if not isinstance(v, float):
                v = None
        return v
    def lchk(self, v):
        if v is not None:
            if not isinstance(v, list):
                v = None
        return v

    def on_message(self, client, data, msg):
#        print_n_log("Got message on", msg.topic, str(msg.payload)) # raw output
        if msg.topic != "t_driver":
            return
#        print_n_log("Got message on", msg.topic, msg.payload.decode("utf-8"))
        print_n_log("Got some message on", msg.topic)
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except:
            print_n_log("JSON: cannot decode this message:", msg.payload.decode("utf-8"))
            return
        mac = data.get('mac')
        if self.mac == mac:
            mesg_t = self.ichk(data.get('type'))
            if mesg_t is None:
                print_n_log("Got untyped message: {} ({})".format(mesg_t, data.get('type')))
                return
            if mesg_t == MQTT_TYPE_REG_RESP:
                status = self.ichk(data.get('success'))
                if status is not None:
                    if status is MQTT_STATUS_OK: # ??? undocumented
                        print_n_log("Registered")
                        self.registered = True
                        self.alarm['r'].set()
                        route = self.schk(data.get('route'))
                        if route is not None:
                            share.put(QTYPE_ROUTE, route)
                else:
                    error = self.schk(data.get('error'))
                    desc = "" if error is None else "("+error+")"
                    print_n_log("Registration failed: status is {} {}".format(status, desc))
            elif mesg_t == MQTT_TYPE_STATUS:
                print_n_log("Status is requested")
                self.pub_status(data.get('message_id'))
            elif mesg_t in MQTT_TYPE_MODES:
                print_n_log("Switch to {}th mode".format(mesg_t))
                share.put(QTYPE_MODE, mesg_t)
            elif mesg_t == MQTT_TYPE_STATUSBAR:
                guid=self.schk(data.get('route_guid'))
                route=self.schk(data.get('route_name'))
                driver=self.schk(data.get('driver_name'))
                delay=self.ichk(data.get('delta'))
                share.put(QTYPE_STATUSBAR, dict(guid=guid, route=route, driver=driver, delay=delay))
                print_n_log('Message STATUSBAR: route_guid={}, route_name="{}", driver_name="{}", delta={}'.format(guid, route, driver, delay))
            elif mesg_t == MQTT_TYPE_GPS_INFO:
                lat=self.fchk(data.get('latitude'))
                lon=self.fchk(data.get('longitude'))
                share.put(QTYPE_GPS_INFO, dict(lat=lat, lon=lon))
                if GPS_TRACKING:
                    print_n_log("Message GPS INFO: lat={}, lon={}".format(lat, lon))
            elif mesg_t == MQTT_TYPE_ROUTE_DESC:
                data = self.lchk(data.get('desc'))
                if data is not None:
                    share.put(QTYPE_ROUTE_DESC, data)
                    print_n_log("Message ROUTE DESCRIPTION:", data)
            elif mesg_t == MQTT_TYPE_STARTLEG: # do nothing
                print_n_log("Got message, type STARTLEG: do nothing")
            elif mesg_t == MQTT_TYPE_EQUIPMENT:
                data = self.lchk(data.get('device'))
                if data is not None:
                    share.put(QTYPE_EQUIPMENT, data)
                    print_n_log("Message EQUIPMENT:", data)
            elif mesg_t == MQTT_TYPE_SCHEDULE:
                data = self.lchk(data.get('schedule'))
                if data is not None:
                    share.put(QTYPE_SCHEDULE, data)
                    print_n_log("Message SCHEDULE:", data)
            elif mesg_t == MQTT_TYPE_MESSAGE:
                ts = self.ichk(data.get('timestamp'))
                title = self.schk(data.get('title'))
                mesg = self.schk(data.get('mesg'))
                mesg_id = self.ichk(data.get('mesg_id'))
                share.put(QTYPE_QT_MESSAGE, dict(timestamp=ts, title=title, body=mesg, mesg_id=mesg_id))
                print_n_log('Message type MESG: timestamp={}, title="{}", mesg="{}", mesg_id={}'.format(ts, title, mesg, mesg_id))
            else:
                print_n_log("Unknown message type:", mesg_t, "(so, do nothing)")
        else:
            if mac is None:
                print_n_log("Was that broadcast? - I do know nothing!")
            else:
                print_n_log("I'm a little confused, senator: \"{}\" != \"{}\"".format(self.mac, mac))

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

    def close(self):
        self.mqtt.disconnect()
        self.mqtt.loop_stop()


class MesgPopup(QWidget):
    def __init__(self, parent=None, tw=None):
        self.tw = tw
        QWidget.__init__(self, parent, Qt.FramelessWindowHint)
        DIALOG_SZ = QSize(520, 340)
        TL_RECT = QRect(0,  28, DIALOG_SZ.width(), 75)
        MS_RECT = QRect(0,  78, DIALOG_SZ.width(), 175)
        DT_RECT = QRect(0, 205, DIALOG_SZ.width(), 50)
        OK_RECT = QRect( 45, 255, 105, 60)
        RT_RECT = QRect(175, 255, 300, 60)
        OK_TEXT = "OK"
        RT_TEXT = "Всі повідомлення"
        self.setGeometry(APP_GEOM.x() + (APP_GEOM.width() - DIALOG_SZ.width())/2, APP_GEOM.y() + (APP_GEOM.height() - DIALOG_SZ.height())/2, DIALOG_SZ.width(), DIALOG_SZ.height())
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.info = QLabel()
        self.info.setStyleSheet(MESG_POPUP_STYLE['dlg'])
        self.tl = QLabel(self.info)
        self.tl.setGeometry(TL_RECT)
        self.tl.setStyleSheet(MESG_POPUP_STYLE['title'])
        self.ms = QLabel(self.info)
        self.ms.setGeometry(MS_RECT)
        self.ms.setStyleSheet(MESG_POPUP_STYLE['body'])
        self.dt = QLabel(self.info)
        self.dt.setGeometry(DT_RECT)
        self.dt.setStyleSheet(MESG_POPUP_STYLE['date'])
        self.ok = QPushButton(OK_TEXT, self.info)
        self.ok.setGeometry(OK_RECT)
        self.ok.setStyleSheet(MESG_POPUP_STYLE['btn_ok'])
        self.ok.setDefault(True)
        self.ok.clicked.connect(self.beep_n_hide)
        self.rt = QPushButton(RT_TEXT, self.info)
        self.rt.setGeometry(RT_RECT)
        self.rt.setStyleSheet(MESG_POPUP_STYLE['btn_all'])
        self.rt.setCheckable(True)
        self.rt.setAutoDefault(False)
        self.rt.clicked.connect(self.go_to_mesg_tab)
        self.box = QHBoxLayout()
        self.box.setSpacing(0)
        self.box.setContentsMargins(0, 0, 0, 0)
        self.box.addWidget(self.info)
        self.setLayout(self.box)

    def beep_n_hide(self):
        QSound.play(BEEP)
        self.hide()

    def new_mesg(self, mesg):
        self.tl.setText("<p align='center'>%s</p>" % mesg['title'].upper())
        self.ms.setText("<p align='center'>%s</p>" % mesg['body'])
        self.dt.setText("<p align='center'>%s</p>" % mesg['date'])
        self.show()
        QSound.play(NEW_MESG_BEEP)

    def go_to_mesg_tab(self):
        self.hide()
        QSound.play(BEEP)
        self.tw.setCurrentIndex(MESG_TAB)


class StatusBar(QStatusBar):
    def __init__(self):
        super(StatusBar, self).__init__()
        self.setStyleSheet(SBAR_STYLE)
        self.setFixedHeight(SBAR_HEIGHT)

        self.driver = QLabel()
        self.driver.setContentsMargins(SBAR_MARGINS['driver'])
        self.driver.setStyleSheet(SBAR_ELEM_STYLE)
        self.driver.setFixedWidth(300)
        self.addWidget(self.driver)
        self.driver.hide()
        self.driver_name = None

        self.route = QLabel()
        self.route.setContentsMargins(SBAR_MARGINS['route'])
        self.route.setStyleSheet(SBAR_ELEM_STYLE)
        self.route.setFixedWidth(180)
        self.addWidget(self.route)
        self.route.hide()
        self.route_name = None

        self.clock = QLabel()
        self.clock.setPixmap(QPixmap(SBAR_ICO['clock']))
        self.clock.setContentsMargins(SBAR_MARGINS['clock'])
        self.addWidget(self.clock)
        self.clock.hide()

        self.delay = QLabel()
        self.delay.setContentsMargins(SBAR_MARGINS['delay'])
        self.delay.setStyleSheet(SBAR_ELEM_STYLE)
        self.addWidget(self.delay)
        self.delay.hide()
        self.delay_value = None

        self.tm = QLabel()
        self.tm.setStyleSheet(SBAR_ELEM_STYLE)
        self.tm.setContentsMargins(SBAR_MARGINS['time'])
        self.set_time()
        self.addWidget(self.tm)

        self.timer = QTimer()
        self.timer.timeout.connect(self.set_time)
        self.timer.start(1000)

        self.logo = QLabel()
        self.logo.setPixmap(QPixmap(SBAR_ICO['logo']))
        self.logo.setContentsMargins(SBAR_MARGINS['logo'])
        self.addPermanentWidget(self.logo)

    def set_time(self):
        self.tm.setText(strftime("%H:%M", localtime()))

    def set_work_mode(self):
        self.driver.setText("" if self.driver_name is None else self.driver_name)
        self.driver.show()
        self.route.setText("" if self.route_name is None else self.route_name)
        self.route.show()
        self.clock.show()
        if self.delay_value is None:
            self.delay.setText("")
        else:
            self.set_delay()
        self.delay.show()

    def set_wait_mode(self):
        self.driver.hide()
        self.driver_name = None
        self.route.hide()
        self.route_name = None
        self.delay.hide()
        self.delay_value = None
        self.clock.hide()

    def set_route(self, value):
        self.route.setText(value)

    def set_driver(self, value):
        self.driver.setText(value)

    def set_delay(self, dly = None):
        if dly is not None:
            if isinstance(dly, int):
                self.delay_value = dly
        if self.delay_value is not None:
            self.delay.setText(str(self.delay_value) + 'хв')
            self.delay.setStyleSheet(SBAR_ELEM_STYLE + "color:" + (SBAR_COLOR['lag'] if self.delay_value < 0 else SBAR_COLOR['lead']) + ";")


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        sz = super(TabBar, self).tabSizeHint(index)
        size = QSize(TAB_WIDTH[index], sz.height())
        return size

    def set_messages_ref(self, messages):
        self.messages = messages

    def paintEvent(self, e):
        for index in range(self.count()):
            QTabBar.paintEvent(self, e)
            if index == MESG_TAB:
                new = sum(m['status'] == UNREAD_MESG for m in self.messages)
                if new > 0:
                    painter = QPainter()
                    painter.begin(self)
                    rect = self.tabRect(index)
                    r = self.tabRect(index)
                    r.setSize(NMPLACE['size'])
                    r.translate(NMPLACE['point'])
                    painter.setBrush(QColor(NMPLACE['color']))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(r)
                    painter.setPen(QPen(QColor(Qt.white)))
                    txt = str(new) if new < 100 else ">9"
                    painter.drawText(r, Qt.AlignCenter, txt)
                    painter.end()


class TabWidget(QTabWidget):
    def __init__(self, data):
        super(TabWidget, self).__init__()
        self.tb = TabBar()
        self.tb.setExpanding(True)
        self.setTabBar(self.tb)
        self.setDocumentMode(True)
        self.data = data

        for d in self.data:
            self.setIconSize(ICON_SIZE)
            t = self.data[d]
            i = t['index']
            w = QWidget()
            w.setStyleSheet(TAB_STYLE)
            t['icons'] = {}
            for sffx in TAB_ICO_SFFX:
                fname = IMAGE_DIR + TAB_ICO_PRFX + d + TAB_ICO_SFFX[sffx]
                t['icons'][sffx] = QIcon(fname) if os.path.isfile(fname) else None
            ico = t['icons']['unselected' if i is not DEFAULT_TAB else 'selected']
            if ico is None:
                self.insertTab(i, w, t['title'])
            else:
                self.insertTab(i, w, ico, t['title'] + '   ')
            self.setTabToolTip(i, t['tip'])
            self.data[d]['tab'] = w

        self.bort_tab = BortTab(self.data['bort']['tab'])
        self.stop_tab = StopTab(self.data['stop']['tab'])
        self.desc_tab = DescTab(self.data['desc']['tab'])
        self.gmap_tab = GmapTab(self.data['gmap']['tab'])
        self.mesg_tab = MesgTab(self.data['mesg']['tab'], self.tb)
        self.tb.set_messages_ref(self.mesg_tab.archive)

        self.setStyleSheet(TABWIDGET_STYLE)
        self.tb.setStyleSheet(TABBAR_STYLE);
        self.currentChanged.connect(lambda i: self.change_tabico(i))
        self.active_tab = DEFAULT_TAB
        self.setCurrentIndex(self.active_tab)

    def change_tabico(self, ind):
        for d in self.data:
            t = TAB_NAMES[d]
            state = t['icons']['selected' if t['index'] is ind else 'unselected']
            if state is not None:
                self.setTabIcon(t['index'], state)
        self.active_tab = ind


class RegWidget(QDialog):
    def __init__(self, mesg=None):
        super(RegWidget, self).__init__(None, Qt.FramelessWindowHint)
        DIALOG_RECT = QRect(APP_GEOM.x(), APP_GEOM.y(), APP_GEOM.width(), APP_GEOM.height() - SBAR_HEIGHT)
        MS_RECT = QRect(0, 288, DIALOG_RECT.width(), 400)
        self.setStyleSheet("background-image:url(" + REGWIN['ico'] + ");")
        self.setWindowModality(Qt.WindowModal)
        self.setGeometry(DIALOG_RECT)
        self.setFixedSize(self.size())
        if mesg is not None:
            ms = QLabel("<p align='center'>" + mesg + "</p>", self)
            ms.setStyleSheet(REGMSG_STYLE)
            ms.setAttribute(Qt.WA_TranslucentBackground)
            ms.setGeometry(MS_RECT)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(APP_GEOM)
        self.sb = StatusBar()
        self.cw = QStackedWidget()
        self.tab = TabWidget(TAB_NAMES)
        self.cw.insertWidget(TAB_NDX, self.tab)
        self.reg = RegWidget(REGWIN['text'])
        self.cw.insertWidget(REG_NDX, self.reg)
        self.cw.setCurrentIndex(REG_NDX)
        self.setCentralWidget(self.cw)
        self.setStatusBar(self.sb)
        self.mesg_popup = MesgPopup(tw = self.tab)
        self.sw_label = QLabel(PROGNAME+"-"+SW_VERSION, self.sb)
        self.sw_label.setStyleSheet(SW_LABEL_STYLE)
        self.sw_label.setGeometry(APP_GEOM.width()/2-90, 9, 180, 29)
        QTimer.singleShot(SW_TIMEOUT*1000, self.sw_label.hide)

    def set_mode(self, mode):
        if mode is MQTT_TYPE_WORKMODE:
            self.cw.setCurrentIndex(TAB_NDX)
            self.sb.set_work_mode()
        elif mode is MQTT_TYPE_WAITMODE:
            self.cw.setCurrentIndex(REG_NDX)
            self.sb.set_wait_mode()
        elif mode is MQTT_TYPE_REGMODE:
            self.cw.setCurrentIndex(REG_NDX)
            self.sb.set_wait_mode()
        elif mode is MQTT_TYPE_REFUNDMODE:
            print_n_log("REFUND_MODE is not implemented")
        elif mode is MQTT_TYPE_CHKMODE:
            print_n_log("CHK_MODE is not implemented")

    def statusbar_update(self, sb):
        v = sb.get("driver")
        if v is not None:
            self.sb.set_driver(v)
        v = sb.get("route")
        if v is not None:
            self.sb.set_route(v)
        v = sb.get("delay")
        if v is not None:
            self.sb.set_delay(v)

    def mesg_append(self, mesg):
        self.tab.mesg_tab.archive.append(mesg)
        self.tab.mesg_tab.update()
        self.mesg_popup.new_mesg(dict(title=mesg['title'], body=mesg['mesg'], date=mesg['date']))

    def data_update(self, elem):
        if elem['type'] is QTYPE_GPS_INFO:
            if self.tab.active_tab == GMAP_TAB:
                self.tab.gmap_tab.update(elem['item'])
        elif elem['type'] is QTYPE_STATUSBAR:
            if elem['item'] is not None:
                self.statusbar_update(elem['item'])
        elif elem['type'] is QTYPE_SCHEDULE:
            self.tab.stop_tab.update(elem['item'])
        elif elem['type'] is QTYPE_ROUTE_DESC:
            self.tab.desc_tab.update(elem['item'])
        elif elem['type'] is QTYPE_EQUIPMENT:
            self.tab.bort_tab.update(elem['item'])
        elif elem['type'] is QTYPE_QT_MESSAGE:
            dt = datetime.datetime.fromtimestamp(elem['item']['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
            self.mesg_append(dict(timestamp=elem['item']['timestamp'], status=UNREAD_MESG,
                date=dt, title=elem['item']['title'], mesg=elem['item']['body'], mesg_id=elem['item']['mesg_id']))

def get_mac(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', str.encode(ifname[:15])))
    return ''.join(['%02x' % c for c in info[18:24]]).upper()

def run_mqtt():
    global mqtt
    mqtt = Mqtt(MQTT_BROKER, get_mac(IFACE), MQTT_RTOPIC)


if __name__ == "__main__":
    syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_USER)
#    locale.setlocale(locale.LC_TIME, "uk_UA.utf8")
    share = Share()
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    win = MainWindow()
    win.show()
    timer = QTimer()
    timer.timeout.connect(local_exec)
    timer.start(1000)
    mqtt_thread = threading.Thread(target=run_mqtt)
    mqtt_thread.start()
    sys.exit(app.exec_())

