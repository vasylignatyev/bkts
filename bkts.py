#!/usr/bin/python3
import paho.mqtt.client as mqtt
import time
import datetime
import os

#import pytz
import requests
import json
import threading
from collections import namedtuple
import sqlite3
import math
from uuid import getnode as get_mac


def main():
    print("Start main!")
    app = App()


class MyError(Exception):
    def __init__(self, _error: object)->object:
        #print("Inside MyError")
        #print(_error)
        self.message = _error.get('error')
        self.code = _error.get('code')

    def __str__(self):
        return repr(self.message)


class App(threading.Thread):
    #def __init__(self, q, loop_time = 1.0/60):
    def __init__(self):
        #self.q = q
        #self.timeout = loop_time
        super(App, self).__init__()

        #threading.Thread.__init__(self)


        #Constants

        self.DATABASE='/opt/telecard/bkts.db'
        self.DRIVER_JSON= '/opt/telecard/driver.json'
        self.ROUTE_JSON= '/opt/telecard/route.json'
        self.VEHICLE_JSON= '/opt/telecard/vehicle.json'
        self.SESSION_JSON= '/opt/telecard/session.json'
        self.TRACE_JSON= '/opt/telecard/trace.json'
        self.POINTS_JSON= '/opt/telecard/points.json'
        self.SCHEDULE_JSON= '/opt/telecard/schedule.json'

        self.token = None
        self.routeName = None
        self.route_id = None
        self.routeGuid = None
        self.driverId = None
        self.driverName = None
        self.vehicle_id = None
        self._db = None
        self._errorMessages = None
        self._cursor = None


        self._driver_on_route = False
        self._driver_exist = False
        self._driver_on_vehicle = False

        self._sw_version="1.0.0"
        self._hw_version="RASPBERRY PI 3 MODEL B",
        self._mac = hex(get_mac())[2:14]
        self._mac = self._mac.upper()

        print("my MAC is: {}".format(self._mac))

        self._actual_route_info = False
        self.vehicle_type_ukr = None
        self.route_dict_eng = None
        self._message_id = 1
        self.vehicle_type_short = None

        #GPS BLOCK
        self._gps_array=None
        self._gps_idx=0
        self.latitude = 0.0
        self.longitude = 0.0
        #stop_distance = 0.000547559129223524
        #self.stop_distance = 0.000000299820999996023854551154978576
        self.stop_distance = 0.0000002

        self.validator_dict = {}
        self.ikts_dict = {}

        self._last_deviation = 0

        self.current_point_name = None
        self.current_point_id = None
        self.current_schedule_id = None
        self.current_schedule_time = None
        self.current_weekday = datetime.datetime.now().isoweekday()
        self.last_point_id = None
        self.last_point_name = None

        self.arrival_time = None

        self._equipment_list = None

        self._direction = 1
        self._round = 1
        self.new_search = True

        self.rate = None
        self.name = None

        self.vehicle_type_ukr = None
        self.vehicle_type_eng = None

        #self._tz = pytz.timezone('Europe/Kiev')
        self._dst = time.daylight and time.localtime().tm_isdst > 0
        self._utc_offset = - (time.altzone if self._dst else time.timezone)

        self._local_exec_cnt = 0

        self.db_init()

        print("delete service files")
        try:
            os.remove(self.DRIVER_JSON)
        except Exception as e:
            print("Can`t delete {}".format(self.DRIVER_JSON))
        try:
            os.remove(self.VEHICLE_JSON)
        except Exception as e:
            print("Can`t delete {}".format(self.VEHICLE_JSON))

        self.start()

    def dist(self, long1, lat1, long2, lat2):
        x = long1 - long2
        y = lat1 - lat2
        return math.pow(x, 2) + math.pow(y, 2)

    def db_init(self):
        print("db_init")
        #UDF DECLARATION
        #self._db.create_function("dist", 4, self.dist)

        self.db().execute("DROP TABLE IF EXISTS point")
        #Create point
        sql = "CREATE TABLE IF NOT EXISTS point " \
              "(`id` INTEGER," \
              "`name` TEXT," \
              "`order` INTEGER," \
              "`direction` INTEGER," \
              "`type` INTEGER," \
              "`entrance` INTEGER," \
              "`radius` INTEGER," \
              "`latitude` REAL," \
              "`longitude` REAL," \
              "`now_audio_url` TEXT," \
              "`now_audio_dttm` INTEGER," \
              "`now_video_url` TEXT," \
              "`now_video_dttm` INTEGER," \
              "`future_video_url` TEXT," \
              "`future_video_dttm` INTEGER," \
              "`future_audio_url` TEXT," \
              "`future_audio_dttm` INTEGER," \
              "PRIMARY KEY(`id`,`direction`))"
        self.db().execute(sql)

        sql = "CREATE TABLE IF NOT EXISTS point " \
              "(`id` INTEGER primary key," \
              "`name` TEXT,`order` INTEGER," \
              "`direction` INTEGER," \
              "`type` INTEGER," \
              "`entrance` INTEGER," \
              "`radius` INTEGER," \
              "`latitude` REAL," \
              "`longitude` REAL," \
              "`now_audio_url` TEXT," \
              "`now_audio_dttm` INTEGER," \
              "`now_video_url` TEXT," \
              "`now_video_dttm` INTEGER," \
              "`future_video_url` TEXT," \
              "`future_video_dttm` INTEGER," \
              "`future_audio_url` TEXT," \
              "`future_audio_dttm` INTEGER," \
              "PRIMARY KEY(`id`))"              #"PRIMARY KEY(`id`,`direction`))"
        self.db().execute(sql)

        #Create leg table
        self.db().execute("DROP TABLE IF EXISTS leg")
        sql = 'CREATE TABLE IF NOT EXISTS `leg` '\
              '(`schedule_id` INTEGER primary key,'\
              '`name` TEXT,'\
              '`stime` TEXT,'\
              '`period` INTEGER,'\
              '`variation` INTEGER)'
        self.db().execute(sql)

        self.db().execute("DROP TABLE IF EXISTS schedule")
        #Create schedule
        sql = "CREATE TABLE IF NOT EXISTS schedule ("\
              "`id` INTEGER primary key,"\
              "`station_id` INTEGER,"\
              "`direction` INTEGER,"\
              "`round` INTEGER,"\
              "`date` INTEGER,"\
              "`time` TEXT)"
        self.db().execute(sql)

        # self._db.execute("DROP TABLE IF EXISTS message")
        # CREATE message
        sql = "CREATE TABLE IF NOT EXISTS message " \
              "(`id` INTEGER primary key," \
              "`title` TEXT," \
              "`text` TEXT," \
              "`new` INTEGER DEFAULT 1," \
              "`created_at` INTEGER)"
        self.db().execute(sql)

        # CREATE equipment
        self._db.execute("DROP TABLE IF EXISTS equipment")
        sql = "CREATE TABLE IF NOT EXISTS equipment " \
              "(`mac` TEXT primary key," \
              "`serial_number` TEXT," \
              "`type` INTEGER," \
              "`i_vehicle` INTEGER DEFAULT 0," \
              "`last_status` INTEGER DEFAULT -1," \
              "`cnt` INTEGER DEFAULT 0)"
        self.db().execute(sql)

        self.db().commit()

        #DISCONNECT
        self.db().close()
        self._db = None

    def db(self):
        if self._db is None:
            print("connect to database")
            self._db = sqlite3.connect(self.DATABASE, check_same_thread=False, timeout=10)
            self._db.create_function("dist", 4, self.dist)
            self._db.create_function("t_diff", 2, self.t_diff)
        return self._db

    def db_exec(self, sql):
        try:
            return self.db().execute(sql)
        except sqlite3.Error as e:
            print("DB ERROR: " + str(e))
            print(sql)
            raise MyError(self.getError('db_error'))


    # Error`s Dictionary
    def getError(self, name):
        if self._errorMessages is None:
            self._errorMessages = dict(
                deny=dict(
                    error=dict(
                        eng="Denied",
                        ukr="Отказано"
                    ),
                    code=1
                ),
                composted=dict(
                    error=dict(
                        eng="Already composted",
                        ukr="Вже компостований"
                    ),
                    code=1
                ),
                inaccessible=dict(
                    error=dict(
                        eng="Server is not available",
                        ukr="Сервер не доступний"
                    ),
                    code=2
                ),
                notAuth=dict(
                    error=dict(
                        eng="Not Authorized",
                        ukr="Не авторизований"
                        # ukr = "Не авторизований"
                    ),  # ensure_ascii=False
                    code=6
                ),
                conflict=dict(
                    error=dict(
                        eng="Conflict",
                        ukr="Конфлікт"
                    ),
                    code=7
                ),
                codeError=dict(
                    error=dict(
                        eng="Wrong code",
                        ukr="Невірний код"
                    ),
                    code=8
                ),
                db_error=dict(
                    error=dict(
                        eng="Database error",
                        ukr="Помилка бази даних"
                    ),
                    code=50
                ),
                type_error=dict(
                    error=dict(
                        eng="Wrong message Type",
                        ukr="Неправильний тип повідомлення"
                    ),
                    code=50
                ),
                unknown=dict(
                    error=dict(
                        eng="Unknown error",
                        ukr="Невідома помилка"
                    ),
                    code=-1
                ),
            )
        error_message = self._errorMessages.get(name,
            dict(
                error=dict(
                    eng="Unknown error name '{}'".format(name),
                    ukr="Невідома назва помилки '{}'".format(name),
                )
            ))
        return error_message
    #
    def get_vehicle_type_short(self, route_prefix):
        if self.vehicle_type_short is None:
            self.vehicle_type_short = dict (
                AAA="А",
                AAB="Тр",
                AAC="Т",
                ABA="М",
                ABB="МТ",
                ABC="Е",
                ACA="Ф",
            )
        return self.vehicle_type_short.get(route_prefix[0:3], "№")

    def get_vehicle_type_ukr(self, route_prefix):
        if self.vehicle_type_ukr is None:
            self.vehicle_type_ukr = dict (
                AAA="Автобус №",
                AAB="Тролейбус №",
                AAC="Трамвай №",
                ABA="Метро №",
                ABB="маршрутне таксі №",
                ABC="міська електричка №",
                ACA="фунікулер №",
            )
        return self.vehicle_type_ukr.get(route_prefix[0:3], "№")

    def get_vehicle_type_eng(self, route_prefix):
        if self.vehicle_type_eng is None:
            self.vehicle_type_eng = dict (
                AAA="Bus #",
                AAB="Trolleybus #",
                AAC="Tram #",
                ABA="Metro ",
                ABB="Shuttle taxi #",
                ABC="City train #",
                ACA="Funicular #",
            )
        return self.vehicle_type_eng.get(route_prefix[0:3], "№")

    def get_messages(self):
        print("get_messages")
        if self.driverId is None:
            return False

        sql = "SELECT MAX(`id`) FROM message"
        c = self.db_exec(sql)
        row = c.fetchone()
        last_message_id = 0 if row[0] is None else row[0]
        c.close()

        url = 'http://st.atelecom.biz/mob/v1/message/{}/{}'.format( self.driverId, last_message_id)
        print("url: {}  {}".format(url, self.get_auth_header() ))
        r = requests.get(url, headers=self.get_auth_header())
        if r.status_code == requests.codes.ok:
            print(r)
            response = r.json()
            print(response)
            insert = "INSERT OR IGNORE INTO message (`id`,`title`,`text`,`created_at`) VALUES (?,?,?,?)"

            print("last_message_id {}".format(last_message_id))
            for message in response:
                print(message)
                m_id = int(message.get('id'))
                title = message.get('title')
                text = message.get('text')
                created_at = int(message.get('created_at'))
                self.db().execute(insert,(m_id,title,text,created_at))


                payload = dict(
                    type=230,
                    title=title,
                    created_at=created_at,
                    mesg=text,
                    mesg_id=m_id,
                )
                self.to_driver(payload)

            self.db().commit()

    def send_new_messages_to_driver(self):
        sql = "SELECT `id`,`title`,`text`,`created_at` ORDER BY time(`created_at`) DESC"
        for row in self.db_exec(sql):
            (id, title, text, created_at) = row
            payload = dict(
                type=230,
                title=title,
                mesg=text,
                mesg_id=id
            )
            self.to_driver(payload)
        return True

    def on_message_viewed(self, payload_dict):
        print("on_message_viewed")
        print(payload_dict)
        try:
            if(payload_dict['mesg_id']) is not None:
                sql = "UPDATE message SET new=0 WHERE id ={mesg_id}".format(mesg_id=payload_dict['mesg_id'])
                print(sql)
                self.db_exec(sql)
        except KeyError as e:
            print(e)

    # @staticmethod
    def t_diff(self, ts1, ts2, unsigned=True):
        t1 = datetime.datetime.strptime(ts1, '%H:%M:%S').time()
        t2 = datetime.datetime.strptime(ts2, '%H:%M:%S').time()
        td1 = datetime.timedelta(hours=t1.hour, minutes=t1.minute, seconds=t1.second)
        td2 = datetime.timedelta(hours=t2.hour, minutes=t2.minute, seconds=t2.second)
        delta = td1 - td2
        total_sec = delta.total_seconds()
        if unsigned and total_sec < 0:
            total_sec = total_sec * (-1)
        return int(total_sec)

    def send_route_info(self):
        print("_______________________ send_route_info ______________________________")

        route_info = [
            dict(item="Початок", desc="УЛ. ИЦКАХА РАБИНА"),
            dict(item="Кінець", desc="ПЛ. ТИРАСПОЛЬСКАЯ"),
            dict(item="Вартість", desc="3.0 грн"),
            dict(item="Відстань", desc="7.97 км"),
            dict(item="Інтервал", desc="5 мин"),
            dict(item="Робочі дні", desc="Пн Вт Ср Чт Пт Сб Вс"),
            dict(item="Робочі години", desc="05:24 - 22:58"),
            dict(item="Компанія", desc='	КП "ОГЭТ"'),
            dict(item="Телефон", desc="(048) 724 62 57"),
            dict(item="Оновлення", desc="	05-11-2017")
        ]

        payload = dict (
            type=240,
            desc= route_info,
        )
        self.to_driver(payload)

    def get_route_info(self, driver_id):
        if self._actual_route_info:
            print("Route Information is up to date")
            #return True
        print("Route Information needs to be updated")
        url = 'http://st.atelecom.biz/mob/v1/front/staff/route?id={}'.format(driver_id)
        print(url)
        r = requests.get(url, headers=self.get_auth_header())
        if r.status_code == 200:
            response = r.json()

            points = response.get('points', None)
            print("Points count: {}".format(str(len(points))))

            with open(self.POINTS_JSON, 'w') as outfile:
                json.dump(points, outfile)
            outfile.close()

            schedule = response.get('schedule', None)
            print("schedule count: {}".format(str(len(schedule))))

            with open(self.SCHEDULE_JSON, 'w') as outfile:
                json.dump(schedule, outfile)
            outfile.close()

        else:
            return False

        sql = "DELETE FROM point"
        print(sql)
        self.db_exec(sql)
        for point in points:
            fields = '`,`'.join(map(str, point.keys()))
            values = '\',\''.join(map(str, point.values())).replace('\'None\'', 'NULL', 10)
            sql = "INSERT OR IGNORE INTO point (`{}`) VALUES (\'{}\')".format(fields, values)
            #print(sql)
            self.db_exec(sql)

        sql = "DELETE FROM schedule"
        print(sql)
        self.db_exec(sql)
        for item in schedule:
            fields = '`,`'.join(map(str, item.keys()))
            values = '\',\''.join(map(str, item.values())).replace('\'None\'', 'NULL', 10)
            sql = "insert into schedule (`{}`) values (\'{}\')".format(fields, values)
            self.db_exec(sql)
        self.db_exec("UPDATE schedule SET `time` = time(substr('00000'||`time`, -5, 5))")
        self.db().commit()

        self.init_schedule_table()

    def get_auth_header(self):
        if self.token is None:
            raise MyError(self.getError('notAuth'))
        return dict(AUTHORIZATION='Bearer {}'.format(self.token))

    def search_point(self, point_name):
        print("search_point {}".format(point_name))
        self.new_search = False

        dt = datetime.datetime.now()
        time_now = dt.strftime("%H:%M")
        # self.current_weekday = dt.isoweekday()

        print("Now time: {}, weekday: {}".format(time_now, self.current_weekday))

        sql = "SELECT s.round " \
              "FROM schedule s " \
              "INNER JOIN point p  ON s.station_id = p.id AND s.`direction`= p.`direction` " \
              "WHERE p.`name` = '{p_name}' AND s.`date`={wd} AND p.`type`=1  AND s.`direction`={dir} " \
              "ORDER BY t_diff(time(s.time), time('{time}')) LIMIT 1"
        sql = sql.format(dir=self._direction, time=time_now, wd=self.current_weekday, p_name=point_name)
        print(sql)

        cursor = self.db_exec(sql)
        row = cursor.fetchone()
        print(row)
        self._round = row[0]

        self.init_leg_table()

    def init_leg_table(self):
        print("init_leg_table round: {}, weekday: {}, direction: {}".format(self._round,self.current_weekday,self._direction))
        sql="DELETE FROM `leg`"
        self.db_exec(sql)

        dt = datetime.datetime.now()
        time_now = dt.time()

        print(time_now.strftime('%H:%M:%S'))

        sql = "SELECT s.`id`,p.`name`,s.time,p.`id` " \
              "FROM schedule s " \
              "INNER JOIN point p  ON s.station_id = p.id AND s.`direction`= p.`direction` " \
              "WHERE s.round={r} AND s.`date`={wd} AND s.`direction`={dir} AND p.`type`=1 " \
              "ORDER BY s.time"
        sql = sql.format(r=self._round, wd=self.current_weekday, dir=self._direction)
        cursor = self.db_exec(sql)

        insert = "INSERT INTO leg (`schedule_id`,`name`,`stime`,`variation`,`period`) " \
                 "VALUES ({s_id},'{name}','{stime}',{var}, {period})"
        first_time = None
        for row in cursor:
            if row is not None:
                if first_time is None:
                    first_time = row[2]
                    # sql = insert.format(s_id=row[0],name=row[1],stime=row[2],period=0,var=self.t_diff(row[2],time_now.strftime('%H:%M:%S'), False))
                    sql = insert.format(s_id=row[3],name=row[1],stime=row[2],period=0,var=-2000)
                else:
                    # sql = insert.format(s_id=row[0],name=row[1],stime=row[2], period=self.t_diff(row[2], first_time), var=self.t_diff(row[2],time_now.strftime('%H:%M:%S'), False))
                    sql = insert.format(s_id=row[3],name=row[1],stime=row[2], period=self.t_diff(row[2], first_time), var=-2000)
                self.db_exec(sql)
        cursor.close()
        self.db().commit()

        self.update_schedule_table()

        '''
        sql = "SELECT * FROM leg ORDER BY time(stime)"
        cursor = self.db_exec(sql)
        for row in cursor:
            print(row)
        '''

    def update_schedule_table(self):
        print("++++++++++++++++++++ update_schedule_table +++++++++++++++++++++++++")

        sql = "SELECT `name`,`period`,`variation` FROM leg ORDER BY time(stime)"
        cursor = self.db_exec(sql)

        self._last_deviation = 0

        schedule = []
        for row in cursor:
            # schedule.append(dict(zip(('name', 'schedule', 'lag'), row)))
            if row[2] >= -1000:
                self._last_deviation = (-1) * int(row[2] / 60)

            schedule.append(dict(
                name=row[0],
                schedule=int(row[1]/60) if row[1]>0 else row[1],
                lag=int(row[2]) if row[2] < -1000 else self._last_deviation,
            ))

            print(row)
        cursor.close()
        if len(schedule) == 0:
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(sql)
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            return False
        else:
            print(schedule)
        payload = dict(
            type=330,
            schedule=schedule
        )
        self.to_driver(payload)
        self.set_driver_status_bar()

    def init_schedule_table(self):
        print("++++++++++++++++++++ init_schedule_table +++++++++++++++++++++++++")
        '''
        sql = "SELECT p.`name`, -1001, -1001 " \
              "from point p " \
              "WHERE p.`direction`={direction} AND p.`type`=1 " \
              "ORDER BY p.order".format(round=3, wd=1, direction=1)
        '''

        sql = "SELECT `name`, -1001, -1001 FROM `point` " \
              "WHERE `direction`=1 AND `type`=1 ORDER BY `order`"

        cursor = self.db_exec(sql)
        schedule = []
        for row in cursor:
            schedule.append(dict(zip(('name', 'schedule', 'lag'), row)))
        cursor.close()
        print(schedule)
        payload = dict(
            type=330,
            schedule=schedule
        )
        self.to_driver(payload)


    def change_le_table_on_stop(self, shedule_id):
        pass

    # MQTT Callbacks
    #Informer Registration CallBack
    def on_start_leg(self, req_dict):
        print("on_start_leg")

        self._direction = 1
        self._gps_idx = 0

        self.new_search = True
        self. search_point('ст. м. Харківська')

        req_dict['round'] = self._round
        req_dict['direction'] = self._direction

        #search for last stop on route

        sql = "SELECT p.name, p.id " \
              "FROM schedule s " \
              "INNER JOIN point p  ON s.station_id = p.id AND s.`direction`= p.`direction` " \
              "WHERE s.round={r} AND s.`date`={wd} AND s.`direction`={dir} AND p.`type`=1 " \
              "ORDER BY s.time DESC LIMIT 1"
        sql = sql.format(r=self._round, wd=self.current_weekday, dir=self._direction)
        row = self.db_exec(sql).fetchone()
        print(row)
        if row is None:
            print("Empty Table")
            return False

        self.last_point_name = row[0]
        self.last_point_id = row[1]

        self.to_ikts(req_dict)
        self.to_driver(req_dict)

        #Clear leg list
        headers = dict(AUTHORIZATION='Bearer {}'.format(self.token))
        payload = dict(
            vehicle_id=self.vehicle_id,
        )
        # Send request
        url = 'http://st.atelecom.biz/mob/v1/repayment'
        print( "SENDING DELETE REQUEST TO '{}'".format(url) )
        print("Payload: '{}'".format(str(payload)))
        print("Header: '{}'".format(str(headers)))
        r = requests.delete(url, headers=headers, json=payload)
        print(r)

    def on_gps_coordinates(self, reqDict):
        print("Call for: on_gps_coordinates")
        args = ('latitude', 'longitude')
        error = ""
        try:
            for arg in args:
                vars(self)[arg] = reqDict[arg]
        except KeyError as e:
            print(e)
            error += " Required attribute: '{}'.".format(arg)

        if len(error) > 0:
            print(error)
            return False

        lat = float(reqDict['latitude'])
        lon = float(reqDict['longitude'])
        if self._direction is None or self._round is None:
            return False
        sql = "SELECT p.`name`, p.`id`, s.id, s.`time` FROM schedule s "\
              "INNER JOIN point p ON s.station_id = p.id AND s.`direction`= p.`direction` "\
              "WHERE p.`type`=1 AND s.`direction`={dir} AND s.`round`={r} AND dist({lat}, {lon}, `latitude` ,`longitude`) < {dist}"
        sql = sql.format(lat=lat, lon=lon, dist=self.stop_distance, dir=self._direction, r=self._round)
        # print(sql)
        cursor = self.db_exec(sql)
        station = cursor.fetchone()
        # print(station)
        if type(station).__name__ == "tuple" and station[0] is not None:
            if self.current_point_name is None:
                (self.current_point_name, self.current_point_id, self.current_schedule_id, self.current_schedule_time) = station
                print("Current s_id: {}, p_id {}, round: {} time: {}".format(str(self.current_schedule_id),str(self.current_point_id), str(self._round), str(self.current_schedule_time)))

                self.on_arrival()

                if self.new_search:
                    print("NEW SEARCH")
                    self.search_point(self.current_point_name)

                if station[1] == self.last_point_id:
                    self.change_direction()

        else:
            if self.current_point_name is not None:
                self.on_departure(self.current_point_name)
                self.current_point_name = None

    def change_direction(self):
        self._direction = 1 if self._direction == 2 else 2
        print("Change direction: '{}'".format(str(self._direction)))

        self.new_search = True

        req_dict = dict(
            type=120,
            round=self._round,
            direction=self._direction,
            timestamp=int(datetime.datetime.now().timestamp()),
        )
        self.to_ikts(req_dict)
        self.to_driver(req_dict)

    def check_ikts(self):
        #print("check_ikts")
        if self.ikts_dict is not None:
            print(self.ikts_dict)
            for mac in self.ikts_dict:
                #print(self.ikts_dict[mac])
                if mac is not None:
                    #print(ikts)
                    if self.ikts_dict[mac]['cnt'] > 0:
                        print("IKTS: {} is not in order".format(mac))

                    self.ikts_dict[mac]['cnt'] = self.ikts_dict[mac]['cnt'] + 1
                    payload = dict(
                            type=202,
                            timestamp=int(datetime.datetime.now().timestamp()),
                            mac=mac,
                    )
                    self.to_ikts(payload)

    def check_validators(self):
        print("check_validators")
        if self.validator_dict is not None:
            #print(type(self.validator_dict))
            for mac in self.validator_dict:
                print(self.validator_dict[mac])
                if mac is not None:
                    if self.validator_dict[mac]['cnt'] > 0:
                        print("VALIDATOR: {} is not in order".format(mac))
                        pass

                    self.validator_dict[mac]['cnt'] = self.validator_dict[mac]['cnt'] + 1
                    payload = dict(
                            type=1,
                            timestamp=int(datetime.datetime.now().timestamp()),
                            validator_id=mac,
                    )
                    self.to_validator(payload)

        payload=dict(
            type=340,
            message_id=self._message_id,
            timestamp=datetime.datetime.timestamp(),

        )

        pass
    def on_arrival(self):
        print("++++++++++++++++++++++ ARRIVAL ++++++++++++++++++++++++++++++++")
        print("Arrive to: '{}'".format(self.current_point_name))
        dt = datetime.datetime.now()
        self.arrival_time = dt.strftime('%H:%M:%S')
        print("arrival time: {}, schedule time: {}".format(self.arrival_time, self.current_schedule_time))
        difference = self.t_diff(self.arrival_time, self.current_schedule_time, False)
        print("Difference: {}".format(difference))

        stop_info = dict(
            type=20,
            ukr=self.current_point_name,
            eng="",
        )
        self.to_validator(stop_info)

        #Update LEG table
        sql = "UPDATE leg SET period = 0, variation={var} WHERE schedule_id={sid}"
        sql = sql.format(var=difference, sid=self.current_point_id)
        print(sql)
        self.db_exec(sql)

        sql = "SELECT time(`stime`) FROM leg WHERE schedule_id={sid}"
        #sql = sql.format(sid=self.current_schedule_id)
        sql = sql.format(sid=self.current_point_id)
        print(sql)
        cursor = self.db_exec(sql)
        row = cursor.fetchone()
        cursor.close()

        if row is not None:
            sql = "UPDATE leg SET `period`=-2000 WHERE time(stime) < '{cstime}'"
            sql = sql.format(cstime=row[0])
            #print(sql)
            self.db_exec(sql)

        sql = "SELECT time(`stime`), period, schedule_id FROM leg ORDER BY time(`stime`)"
        cursor = self.db_exec(sql)
        current_stop_time = None
        for row in cursor:
            if row[1] > -2000:
                if current_stop_time is None:
                    current_stop_time = row[0]
                else:
                    if current_stop_time is not None:
                        sql = "UPDATE leg SET period = t_diff('{cst}', time(`stime`)) WHERE schedule_id = {sid}"
                        sql = sql.format(cst=current_stop_time, sid=row[2])
                        #print(sql)
                        self.db_exec(sql)
        self.db().commit()

        self.update_schedule_table()

        stop_info = dict(
            type=220,
            difference=difference,
            schedule_id=self.current_schedule_id,
            direction=self._direction,
            round=self._round,
        )

        #SERCH STOP  INFORMATION
        sql = "SELECT p.`name`," \
              "p.`id`," \
              "s.`id`,"\
              "s.`time`," \
              "t_diff(s.time,'{at}')," \
              "p.`now_audio_url`," \
              "p.`now_audio_dttm`," \
              "p.`now_video_url`," \
              "p.`now_video_dttm`, " \
              "p.`future_audio_url`," \
              "p.`future_audio_dttm`," \
              "p.`future_video_url`," \
              "p.`future_video_dttm`," \
              "p.`direction` " \
              "FROM schedule s " \
              "INNER JOIN point p  ON s.station_id = p.id AND s.`direction`= p.`direction` " \
              "WHERE s.`time` >= '{st}' AND s.`date`={wd} AND p.`type`=1  AND s.`direction`={dir} AND s.`round`={r} " \
              "ORDER BY s.time LIMIT 3"

        sql = sql.format(wd=self.current_weekday, dir=self._direction, r=self._round, st=self.current_schedule_time, at=self.arrival_time )
        print(sql)
        cursor = self.db_exec(sql)

        properties = ('curr_stop_info', 'next1_stop_info', 'next2_stop_info')
        for _property in properties:
            row = cursor.fetchone()
            print(row)
            if row is not None:
                if stop_info['schedule_id'] is None:
                    stop_info['schedule_id'] = row[2]
                stop_info[_property] = dict(
                    route_id=self.route_id,
                    stop_id=self.current_point_id,
                    ukr=row[0],
                    eta=row[4],
                    now_audio_url=row[5],
                    now_audio_dttm=row[6],
                    now_video_url=row[7],
                    now_video_dttm=row[8],
                    future_audio_url=row[9],
                    future_audio_dttm=row[10],
                    future_video_url=row[11],
                    future_video_dttm=row[12],
                    direction=row[13],
                )
            else:
                stop_info[_property] = dict(
                    route_id=self.route_id,
                    stop_id=self.current_point_id,
                    ukr="",
                    eta=0,
                )
        self.to_ikts(stop_info)
        # self.to_driver(stop_info)
        #self.to_itv(stop_info)

    def on_departure(self, station):
        print("Departure from: '{}'".format(station))
        # SERCH STOP  INFORMATION
        sql = "SELECT p.`name`,p.`id`,s.`id`,s.`time`, s.`time`," \
              "p.`now_audio_url`,p.`now_audio_dttm`,p.`now_video_url`,p.`now_video_dttm`, " \
              "p.`future_audio_url`,p.`future_audio_dttm`,p.`future_video_url`,p.`future_video_dttm`,p.`direction` "\
              "FROM `schedule` s " \
              "INNER JOIN `point` p  ON s.`station_id` = p.`id` AND s.`direction`= p.`direction` " \
              "WHERE s.`time` >= '{st}' AND s.`date`={wd} AND p.`type`=1 AND s.`direction`={dir} AND s.`round` = {r} " \
              "ORDER BY s.time LIMIT 4"

        sql = sql.format(wd=self.current_weekday, dir=self._direction, r=self._round, st=self.current_schedule_time)
        print(sql)

        cursor = self.db_exec(sql)

        stop_info = dict(
            type=221,
            round=self._round,
            direction=self._direction,
        )
        properties = ('curr_stop_info', 'next1_stop_info', 'next2_stop_info', 'next3_stop_info')
        current_stot_time = None

        next_stop_name = None
        i=0
        for _property in properties:
            i += 1
            row = cursor.fetchone()
            if row is not None:
                if current_stot_time is None:
                    current_stot_time = row[3]

                stop_info[_property] = dict(
                    route_id=self.route_id,
                    stop_id=self.current_point_id,
                    ukr=row[0],
                    eta=self.t_diff(row[3], current_stot_time),
                    now_audio_url=row[5],
                    now_audio_dttm=row[6],
                    now_video_url=row[7],
                    now_video_dttm=row[8],
                    future_audio_url=row[9],
                    future_audio_dttm=row[10],
                    future_video_url=row[11],
                    future_video_dttm=row[12],
                    direction=row[13],
                )
                if i == 2:
                    next_stop_name = row[0]
            else:
                stop_info[_property] = dict(
                    route_id=self.route_id,
                    stop_id=self.current_point_id,
                    ukr="",
                    eta=0,
                )
        self.to_ikts(stop_info)

        sql = "SELECT p.`name`,p.`id`,s.`id`,s.`time`, s.`time`," \
              "p.`now_audio_url`,p.`now_audio_dttm`,p.`now_video_url`,p.`now_video_dttm`, " \
              "p.`future_audio_url`,p.`future_audio_dttm`,p.`future_video_url`,p.`future_video_dttm`,p.`direction` "\
              "FROM `schedule` s " \
              "INNER JOIN `point` p  ON s.`station_id` = p.`id` AND s.`direction`= p.`direction` " \
              "WHERE s.`time` >= '{st}' AND s.`date`={wd} AND p.`type`=1 AND s.`direction`={dir} AND s.`round` = {r} " \
              "ORDER BY s.time LIMIT 3"

        sql = sql.format(wd=self.current_weekday, dir=self._direction, r=self._round, st=self.current_schedule_time)
        print(sql)

        cursor = self.db_exec(sql)

        stop_info = dict(
            type=221,
            round=self._round,
            direction=self._direction,
        )
        properties = ('curr_stop_info', 'next1_stop_info', 'next2_stop_info', 'next3_stop_info')
        current_stot_time = None

        next_stop_name = None
        i=0
        for _property in properties:
            i += 1
            row = cursor.fetchone()
            if row is not None:
                if current_stot_time is None:
                    current_stot_time = row[3]

                stop_info[_property] = dict(
                    route_id=self.route_id,
                    stop_id=self.current_point_id,
                    ukr=row[0],
                    eta=self.t_diff(row[3], current_stot_time),
                    now_audio_url=row[5],
                    now_audio_dttm=row[6],
                    now_video_url=row[7],
                    now_video_dttm=row[8],
                    future_audio_url=row[9],
                    future_audio_dttm=row[10],
                    future_video_url=row[11],
                    future_video_dttm=row[12],
                    direction=row[13],
                )
                if i == 2:
                    next_stop_name = row[0]
            else:
                stop_info[_property] = dict(
                    route_id=self.route_id,
                    stop_id=self.current_point_id,
                    ukr="",
                    eta=0,
                )
        # self.to_driver(stop_info)

        if next_stop_name is not None:
            stop_info = dict(
                type=21,
                ukr=next_stop_name,
                eng="",
            )
        self.to_validator(stop_info)

    def get_points(self):
        print("get_points")

    def informer_reg_cb(self, reqDict):
        print('informer_reg_cb')

        print(reqDict)

        error = ""
        args = ('mac', 'message_id', 'status', 'sw_version','hw_version', 'timestamp')
        try:
            for arg in args:
                vars(self)[arg] = reqDict[arg]
        except KeyError as e:
            error += " Required attribute: '{}'.".format(arg)

        if len(error) != 0:
            print(error)
            return False

        mac = reqDict.get('mac')
        message_id = reqDict.get('message_id')
        status = reqDict.get('status')
        sw_version = reqDict.get('sw_version')
        hw_version = reqDict.get('hw_version')
        timestamp = reqDict.get('timestamp')

        if mac.upper() == self._mac.upper():
            print("Driver terminal registration")
            reqDict['timestamp'] = int(time.time())
            reqDict['success'] = 0
            self.to_driver(reqDict)

            return True

        headers = dict(AUTHORIZATION='Bearer {}'.format(self._mac))
        payload = dict(
            sw_version=sw_version,
            status=hw_version,
            mac=mac,
        )
        payload = dict(
            device_mac_address=mac,
            device_serial_number=mac,
            code=200,
            staff_id=self.driverId,
            vehicle_id=self.vehicle_id,
            route_id=self.route_id,
            sw_version=sw_version,
            hw_version=hw_version,
            status=200,
            mac=mac,
            location= dict(
                lat=0,
                lng=0,
                timestamp=int(datetime.datetime.now().timestamp())
            )
        )  # Send request
        url = 'http://st.atelecom.biz/mob/v1/front/alarms/status'
        print( "Sending request to '{}'".format(url))
        print("Payload")
        print(payload)
        r = requests.post(url, json=payload, headers=self.get_auth_header())
        print('RESPONCE')
        print(r)
        if r.status_code == requests.codes.ok:
            response = r.json()
            print(response)
            reqDict['timestamp'] = int(time.time())
            reqDict['success'] = 0
            self.to_ikts(reqDict)
            # self.to_driver(reqDict)

            ikts=dict(
                mac=mac,
                status=status,
                sw_version = sw_version,
                hw_version = hw_version,
            )
            self.ikts_dict[mac] = ikts
        return False

    # Validator regisration event
    def on_validator_reg_cb(self, reqDict):
        print('on_validator_reg_cb')

        args = ('type', 'validator_id', 'message_id', 'status', 'sw_version', 'hw_version', 'timestamp')
        try:
            for arg in args:
                vars(self)[arg] = reqDict[arg]
        except KeyError as e:
            print("Required attribute: ", e)
            return False

        mac = reqDict.get('validator_id')

        validator = dict(
            type= reqDict.get('type'),
            mac= mac,
            status= reqDict.get('status'),
            sw_version= reqDict.get('sw_version'),
            hw_version= reqDict.get('hw_version'),
            last_status=reqDict.get('status'),
            in_order=True,
            cnt=0,
        )
        self.validator_dict[mac] = validator
        print(self.validator_dict)

        headers = dict(AUTHORIZATION='Bearer {}'.format(self.validator_id))
        payload = dict(
            hw_version=self.hw_version,
            sw_version=self.sw_version,
            status=self.status,
        )
        # Send request
        print('****************** Request Validator registartion ***********************')
        url='http://st.atelecom.biz/bkts/api/registration'
        r = requests.put(url, headers=headers, json=payload)
        print(url)

        print(payload)
        print("status_code: {}".format(str(r.status_code)))
        #if r.status_code == requests.codes.ok:
        if r.status_code == 200:
            result = dict(
                type=self.type,
                validator_id=self.validator_id,
                message_id=self.message_id,
                timestamp=datetime.datetime.now().timestamp(),
                success=0,
                route='',
                price=0,
            )
            self.to_validator(result)
        else:
            print("!!!!!!!!!!!!!!!!! Registration failed !!!!!!!!!!!!!!!!!!")
            print("PUT url: {}".format(url))
            print("heders: {}".format(str(headers)))
            print("payload: {}".format(str(payload)))
            print("Validator {validator_id} registration failed.".format(validator_id=self.validator_id))
            print("RESPONSE {}".format( str(r)))
            '''
            result = dict(
                type=self.type,
                validator_id=self.validator_id,
                message_id=self.message_id,
                timestamp=datetime.datetime.now().timestamp(),
                success=0,
                route='',
                price=0,
            )
            self.to_validator(result)
            '''

        if self._driver_on_route:
            self.goto_payment_mode()
        else:
            pass
            # self.goto_registration_mode()

    '''
    params: type, validator_id, message_id, driver_id
    Driver registration
    '''
    def on_get_status_cb(self, payloadOBJ):
        print("on_get_status_cb")
        print(payloadOBJ)

        current_validator_id = payloadOBJ.get("validator_id", None)
        if current_validator_id is not None:
            sql = "UPDATE `equipment` SET `cnt`=0 WHERE `mac`='{}'".format(current_validator_id)
            self.db_exec(sql)

    def on_status_responce(self, payloadOBJ):
        print("IKTS on_status_responce")
        print(payloadOBJ)
        current_ikts_mac = payloadOBJ.get("mac", None)
        if current_ikts_mac is not None:
            sql = "UPDATE `equipment` SET `cnt`=0 WHERE `mac`='{}'".format(current_ikts_mac)
            self.db_exec(sql)

    def conductorCB(self, payloadOBJ):
        print("Call for conductorCB")

    def controllerCB(self, payloadOBJ):
        print("Call for controllerCB")

    def check_driver_registration(self):
        print("check_driver_registration")

        self._driver_on_route = False

        if self.get_driver_saved_info() is True:
            if self.get_route_saved_info() is True:
                if self.get_vehicle_saved_info() is True:
                    if self.get_session_saved_info() is True:
                        self._driver_on_route = True

        if self._driver_on_route:
            # GET ROUTE AND SCHEDULE
            self.get_route_info(self.driverId)
            self.get_messages()
            # go to payment mode
            self.goto_payment_mode()

        else:
            self.goto_registration_mode()

    def get_session_saved_info(self):
        try:
            with open(self.SESSION_JSON, 'r') as infile:
                session = json.load(infile)
                infile.close()
        except Exception as e:
            print(e)
            return False
        try:
            self.token = session['token']
            return False if self.token is None else True
        except KeyError as e:
            print(e)
            return False

    def get_driver_saved_info(self):
        print("get_driver_saved_info")

        try:
            with open(self.DRIVER_JSON, 'r') as infile:
                driver = json.load(infile)
                infile.close()
        except Exception as e:
            print(e)
            return False
        try:
            self.driverId = ['id']
            self.driverName = driver['name']
        except KeyError as e:
            print(e)
            return False

    def get_route_saved_info(self):
        print("get_route_saved_info")
        try:
            with open(self.ROUTE_JSON, 'r') as infile:
                route = json.load(infile)
                infile.close()
        except Exception as e:
            print(e)
            return False
        try:
            self.route_id = route['id']

            self.routeName = route['name']
            print("Route Name {}".format(str(self.routeName)))

            self.routeGuid = route['guid']
            print("Route Guid: {}".format(str(self.routeGuid)))

            self.rate = route['rate']

            self.route_name = self.get_vehicle_type_ukr(self.routeGuid) + str(self.routeName)

            return True

        except KeyError as e:
            print(e)
            return False

    def get_vehicle_saved_info(self):
        try:
            with open(self.VEHICLE_JSON, 'r') as infile:
                vehicle = json.load(infile)
                infile.close()
        except Exception as e:
            print(e)
            return False
        try:
            self.vehicle_id = vehicle['id']
            if self.vehicle_id is None:
                return False
            print("Vehicle ID: " + str(self.vehicle_id))
            return True
        except KeyError as e:
            print(e)
            return False

    def goto_refound_mode(self):
        print("go_to_refound_mode")
        payload = dict(
            type=40,
            timestamp=int(datetime.datetime.now().timestamp()),
            ukr="",
            eng="",
            price=self.rate,
            route=self.routeGuid,
        )
        self.to_validator(payload)

    def goto_payment_mode(self):

        print("***************** goto_payment_mode ********************")
        payload = dict(
            type=41,
            timestamp=int(datetime.datetime.now().timestamp()),
            ukr="",
            eng="",
            price=self.rate,
            route=self.routeGuid,
        )
        self.to_validator(payload)
        self.to_driver(payload)

        self.set_driver_status_bar()
        self.send_route_info()

    def goto_registration_mode(self):
        print("goto_registration_mode")
        payload = dict(
            type=42,
            timestamp=int(datetime.datetime.now().timestamp()),
            ukr="реєстрація водія",
            eng="driver registration",
            price=self.rate,
            route=self.routeGuid,
        )
        self.to_validator(payload)

    def goto_waiting_mode(self):
        print("goto_waiting_mode")
        payload = dict(
            type=43,
            timestamp=int(datetime.datetime.now().timestamp()),
            ukr="",
            eng="",
            route=self.routeGuid,
        )
        self.to_validator(payload)

    def goto_check_mode(self):
        print("goto_waiting_mode")
        payload = dict(
            type=44,
            timestamp=int(datetime.datetime.now().timestamp()),
            ukr="",
            eng="",
            route=self.routeGuid,
        )
        self.to_validator(payload)

    def driver_registration(self, code, reqDict):
        print("*************** driver_registration *****************")
        payload = dict(
            code=code
        )
        url = 'http://st.atelecom.biz/mob/v1/auth'
        print("POST :" + url)
        print(payload)
        r = requests.post(url, json=payload)
        print("status: " + str(r.status_code))

        if r.status_code == 404:
            print("404")
            self._driver_exist = False
            raise MyError(self.getError('deny'))
        elif r.status_code == 200:
            self._driver_exist = True
            # to validator
            reqDict['price'] = self.rate
            reqDict['success'] = 0
            self.to_validator(reqDict)

            response = r.json()
            print(response)
            driver = response.get('model', None)
            route = response.get('route', None)
            vehicle = response.get('vehicle', None)
            try:
                print("OPEN: " + self.DRIVER_JSON)
                with open(self.DRIVER_JSON, 'w') as outfile:
                    json.dump(driver, outfile)
                outfile.close()
            except Exception as e:
                print(e)

            print("Compare ROUTE information")
            print(route)
            if route["id"] is not None:
                try:
                    print("OPEN: " + "self.ROUTEJSON")
                    with open(self.ROUTE_JSON, 'r') as infile:
                        old_route_info = json.load(infile)
                        old_updated_at = int(old_route_info.get("updated_at", None))
                        new_updated_at = int(route.get("updated_at", None))
                        if old_updated_at is not None and new_updated_at is not None:
                            self._actual_route_info = True if old_updated_at == new_updated_at else False
                        else:
                            self._actual_route_info = False
                    infile.close()
                    print("OPEN: " + "self.ROUTEJSON")
                    with open(self.ROUTE_JSON, 'w') as outfile:
                        print(route)
                        print("new_route_info updated_at:  {}".format(str(route.get("updated_at"))))
                        json.dump(route, outfile)
                    outfile.close()
                    self._driver_on_route = False
                except Exception as e:
                    print(e)
                    self._actual_route_info = False
            else:
                self._actual_route_info = False
                self._driver_on_route = False
                raise MyError(self.getError('deny'))

            # write vehicle info
            if vehicle.get("id", None) is not None:
                self._driver_on_vehicle = True
                try:
                    with open(self.VEHICLE_JSON, 'w') as outfile:
                        json.dump(vehicle, outfile)
                    outfile.close()
                    # print(vehicle)
                except Exception as e:
                    print(e)
                self._driver_on_route = True
            else:
                self._driver_on_vehicle = False
                try:
                    os.remove(self.VEHICLE_JSON)
                except Exception as e:
                    print(e)

                raise MyError(self.getError('deny'))

            self.token = response.get('token', None)
            # self._driver_on_route = True
            session = dict(
                code=code,
                token=self.token,
            )
            try:
                with open(self.SESSION_JSON, 'w') as outfile:
                    json.dump(session, outfile)
                outfile.close()
            except Exception as e:
                print(e)

            self.route_id = route.get('id', None)
            self.routeName = route.get('name', None)
            self.routeGuid = route.get('guid', None)
            self.rate = route.get('rate', None)

            self.driverId = driver.get('id', None)
            self.driverName = driver.get('name', None)

            self.route_name = self.get_vehicle_type_ukr(self.routeGuid) + str(self.name)
            self.vehicle_id = vehicle.get('id', None)

            print("Vehicle ID: " + str(self.vehicle_id))
            # GET ROUTE AND SCHEDULE
            self.get_route_info(self.driverId)
            # self.get_messages()

            self.get_equipment_list()
            self.validator_registration()
            # self.send_route_info()
            return True
        else:
            raise MyError(self.getError('inaccessible'))


    def get_equipment_list(self):
        '''
        BKTS:1, Validator:2, IKTS:4,

        [{'serial_number': '225.43', 'mac_address': 'EEF993E1BFDE', 'type': '1'},
        {'serial_number': '199.17', 'mac_address': '009977665512', 'type': '2'},
        {'serial_number': '104.156', 'mac_address': '8CDC97E570C2', 'type': '2'},
        {'serial_number': '897', 'mac_address': '769F14D78B4A', 'type': '4'},
        {'serial_number': '90-90', 'mac_address': '119977665512', 'type': '2'},
        {'type': '3'}]
        '''
        print("++++++++++++ get_equipment_list +++++++++++++++++++")

        if self.vehicle_id is None:
            return False

        url = 'http://st.atelecom.biz/mob/v1/front/equipments/index?vehicle={}'.format(self.vehicle_id)
        print(url)
        r = requests.get(url, headers=self.get_auth_header())
        print("status: " + str(r.status_code))
        if r.status_code == 200:
            self._equipment_list = r.json()
            print("+++++++++++++++++ QUIPMENT +++++++++++++++++++++++")
            print(self._equipment_list)
            insert="INSERT OR IGNORE INTO equipment (`mac`,`serial_number`,`type`) VALUES ('{mac}','{serial}','{type}')"
            for box in self._equipment_list:
                mac=box.get('mac_address')
                if mac is None:
                    continue
                sql = insert.format(
                    mac=box.get('mac_address'),
                    serial=box.get('serial_number'),
                    type=box.get('type'), )
                self.db_exec(sql)
            self.db().commit()

        self.send_equipment_list()

        return True

    def send_equipment_list(self):
        print("send_equipment_list")

        c = self.db().cursor()
        equipment = []

        sql = "SELECT 5,`last_status`,`mac` FROM equipment where type = 4"
        result = c.execute(sql)
        for row in result:
            (i, last_status, mac) = row
            equipment.append(dict(
                type=i,
                state=last_status,
                mac=mac,
            ))

        sql = "SELECT 7,`last_status`,`mac` FROM equipment where type = 1"
        result = c.execute(sql)
        for row in result:
            (i, last_status, mac) = row
            equipment.append(dict(
                type=i,
                state=last_status,
                mac=mac,
            ))

        sql = "SELECT 8,`last_status`,`mac` FROM equipment where type = 2"
        result = c.execute(sql)
        k = 0
        for row in result:
            (i, last_status, mac) = row
            equipment.append(dict(
                type=i + k,
                state=last_status,
                mac=mac,
            ))
            k += 1

        payload = dict(
            type=340,
            device=equipment
        )
        self.to_driver(payload)

    def set_driver_status_bar(self):
        print("++++++++++++++++++++++++++++++ set_driver_status_bar +++++++++++++++++++++++++++++++++++")
        self._message_id += 1
        payload = dict(
            type=50,
            timestamp=datetime.datetime.timestamp,
            message_id=self._message_id,
            route_guid = self.routeGuid,
            driver_name = self.driverName,
            route_name=self.get_vehicle_type_short(self.routeGuid) + str(self.routeName),
            delta=self._last_deviation
        )
        self.to_driver(payload)

    def send_equipment_status(self, status, mac ):
        payload = dict(
            device_mac_address=mac,
            device_serial_number=mac,
            code=status,
            staff_id=self.driverId,
            vehicle_id=self.vehicle_id,
            route_id=self.route_id,
            status=status,
            mac=mac,
            location=dict(
                lat=self.latitude,
                lng=self.longitude,
                timestamp=int(datetime.datetime.now().timestamp())
            )
        )
        # Send request
        url = 'http://st.atelecom.biz/mob/v1/front/alarms/status'
        print("Sending request to '{}'".format(url))
        print("Payload: {}".format(payload))
        r = requests.post(url, json=payload, headers=self.get_auth_header())
        print('RESPONCE: {}'.format(str(r)))

    def get_equipment_status(self):
        print("get_equipment_status")

        update = "UPDATE `equipment` SET `last_status` = {last_status}, `cnt`={cnt} WHERE `mac` = '{mac}'"

        update_equipment_status = False

        sql = "SELECT `mac`,`type`,`last_status`, `cnt` FROM `equipment`"
        for row in self.db_exec(sql):
            (mac, _type, last_status, cnt) = row
            if cnt > 0:
                if last_status != -1:
                    print("+++++++++++++++++++++++++++++++++  Send status update  ++++++++++++++++++++++++++++++++")
                    sql = update.format(last_status = -1, mac=mac, cnt = cnt+1)
                    self.db_exec(sql)
                    self.send_equipment_status(500, mac)
                    update_equipment_status = True
            else:
                print("+++++++++++++++++++++++++++++++++  Send status update  ++++++++++++++++++++++++++++++++")
                if last_status != 1:
                    sql = update.format(last_status=1, mac=mac, cnt = cnt+1)
                    self.db_exec(sql)
                    self.send_equipment_status(200, mac)
                    update_equipment_status = True

            if _type is 4:
                payload = dict(
                    type=202,
                    timestamp=int(datetime.datetime.now().timestamp()),
                    mac=mac,
                )
                self.to_ikts(payload)

        payload = dict(
            type=1,
            timestamp=int(datetime.datetime.now().timestamp()),
        )
        self.to_validator(payload)

        if update_equipment_status:
            self.send_equipment_list()

        return True

    '''
        self._message_id = self._message_id + 1
        if self._equipment_list is not None:
            for equipment in self._equipment_list:
                _type = int(equipment.get('type', 0))
                mac = equipment.get('mac_address', None)
                # print(equipment)
                if mac is not None:
                    if _type is 1:
                        # BKTS
                        pass
                    elif _type is 2:
                        # VALIDATOR
                        equipment['status'] = -1
                        cnt = equipment.get('cnt', 0)
                        if cnt > 0: # "not in order"
                            print("Validator {} not in order.".format(mac))
                            if equipment.get('prev_status') != 1:
                                print("+++++++++++++++++++++++++++++++++  Send status update  ++++++++++++++++++++++++++++++++")
                                self.send_equipment_status(500,mac)
                            equipment['prev_status'] = 1
                        else:
                            equipment['cnt'] = cnt + 1
                            if equipment.get('prev_status') != 0:
                                print("+++++++++++++++++++++++++++++++++  Send status update  ++++++++++++++++++++++++++++++++")
                                self.send_equipment_status(200, mac)
                            equipment['prev_status'] = 0

                    elif _type is 4:
                        equipment['status'] = -1
                        cnt = equipment.get('cnt', 0)
                        if cnt > 0:  # "not in order"
                            print("IKTS {} not in order.".format(mac))

                            if equipment.get('prev_status') != 1:
                                print("+++++++++++++++++++++++++++  Send status update  +++++++++++++++++++++++++++++")
                                self.send_equipment_status(500, mac)
                            equipment['prev_status'] = 1
                        else:
                            equipment['cnt'] = cnt + 1
                            if equipment.get('prev_status') != 0:
                                print("+++++++++++++++++++++++++++  Send status update  +++++++++++++++++++++++++++++")
                                self.send_equipment_status(200, mac)
                            equipment['prev_status'] = 0
                        payload = dict(
                            type=202,
                            timestamp=int(datetime.datetime.now().timestamp()),
                            mac=mac,
                        )
                        self.to_ikts(payload)
                    else:
                        print( "Unknown equipment type: {}".format(_type) )
            payload = dict(
                type=1,
                timestamp=int(datetime.datetime.now().timestamp()),
            )
            self.to_validator(payload)
    '''


    def validator_registration(self):
        print("validator_registration")
        print(self.validator_dict)
        for validator in self.validator_dict:
            print("VALIDATOR: {} registration".format(validator))
            # mac = validator.get('mac', None)
            mac = validator
            payload = dict(
                device_mac_address=mac,
                device_serial_number=mac,
                code=200,
                staff_id=self.driverId,
                vehicle_id=self.vehicle_id,
                route_id=self.route_id,
                sw_version=self.validator_dict[mac].get('sw_version', None),
                hw_version=self.validator_dict[mac].get('hw_version', None),
                status=200,
                mac=mac,
                location=dict(
                    lat=self.latitude,
                    lng=self.longitude,
                    timestamp=int(datetime.datetime.now().timestamp())
                )
            )
            # Send request
            url = 'http://st.atelecom.biz/mob/v1/front/alarms/status'
            print("Sending request to '{}'".format(url))
            print("Payload")
            print(payload)
            r = requests.post(url, json=payload, headers=self.get_auth_header())
            print('RESPONCE')
            print(r)
            self._driver_on_route = True
            return True

    def code_validation(self, code, reqDict):
        payload = dict(
            route=self.routeGuid,
            vehicle_id=self.vehicle_id,
            mac=self._mac
        )
        start_time = time.time()

        url = 'http://st.atelecom.biz/mob/v1/repayment/{}'.format(code)

        print("PUT:" + url)
        print("Payload")
        print(payload)
        r = requests.put(url, headers=self.get_auth_header(), json=payload)
        print("status: " + str(r.status_code))

        print("--- {} seconds ---".format(time.time() - start_time))

        # response = r.json()
        # print(response)
        if r.status_code == 409:
            try:
                r.raise_for_status()
            except Exception as e:
                print(e)
            raise MyError(self.getError('conflict'))
        elif r.status_code == 400:
                try:
                    r.raise_for_status()
                except Exception as e:
                    print(e)
                raise MyError(self.getError('conflict'))
        elif r.status_code == 201:
            reqDict['success'] = 0
            self.to_validator(reqDict)
            return True
        elif r.status_code == 200:  # composted
            raise MyError(self.getError('composted'))
        elif r.status_code == 404:  # not founf
            print("NOT FOUND")

            raise MyError(self.getError('codeError'))
        return False

    def send_xdr(self, code):
        print("send_xdr")
        payload = dict(
            tid=1,
            rate=self.rate,
            vehicle_id=self.vehicle_id,
            route_id=self.route_id,
            hex=code,
            time=int(datetime.datetime.now().timestamp())
        )
        url = 'http://st.atelecom.biz/mob/v1/front/portaone/payment'
        print(url)
        print(payload)
        r = requests.post(url, headers=self.get_auth_header(), json=payload)
        print(r)
        if (r.status_code == 200):
            pass

    '''
    QR validation function
    mosquitto_pub -d -h localhost -t t_bkts  -f qrVAlidation.json
    '''
    def qrValidationCB(self, reqDict):
        try:
            print("Call for qrValidationCB")
            # Required arguments
            args = ('type', 'validator_id', 'message_id', 'qr', 'timestamp')
            eng = ""
            for arg in args:
                if arg in reqDict:
                    vars(self)[arg] = reqDict[arg]
                else:
                    eng += " Required attribute: {}".format(arg) + "; "
            if len(eng) > 0: #Conflict
                print(eng)
                raise MyError(self.getError('conflict'))

            code = reqDict.pop('qr')
            code_len = len(code)
            print("Code: '{}',  length: {}".format(code, str(code_len)))
            #if code_len < 32:
            #    raise MyError(self.getError('codeError'))
            if (self._driver_on_route is False) or (code_len == 34):
                self.driver_registration(code, reqDict)
                reqDict['price'] = self.rate
                reqDict['ukr'] = self.get_vehicle_type_ukr(self.routeGuid) + str(self.routeName)
                reqDict['eng'] = self.get_vehicle_type_eng(self.routeGuid) + str(self.routeName)
                reqDict['route'] = self.routeGuid
                reqDict['success'] = 0
                self.to_validator(reqDict)
                # self.send_route_info()

                # Switch Driver terminal to Validation Mode(type:41)
                # vaidation_dict = dict()
                # vaidation_dict['type'] = 41
                # self.to_driver()
            else:
                if self.code_validation(code, reqDict):
                    pass
                    self.send_xdr(code)


        except MyError as e:
            reqDict['error'] = e.message
            reqDict['success'] = e.code
            self.to_validator(reqDict)

        routeDict = dict(
            type=201,
            message_id=self._message_id,
            route_info=dict(
                name=self.get_vehicle_type_ukr(self.routeGuid) + str(self.routeName),
                short=self.get_vehicle_type_short(self.routeGuid) + str(self.routeName),
            ),
            equipments=self._equipment_list,
        )
        print(routeDict)
        self.to_ikts(routeDict)
        self.to_driver(routeDict)

        self.goto_payment_mode()
        return

    '''
    NFC validation function
    mosquitto_pub -d -h localhost -t t_bkts  -f qrVAlidation.json
    '''

    def nfcValidationCB(self, reqDict):
        print("Call for nfcValidationCB")
        try:
            # Required arguments
            args = ('type', 'validator_id', 'message_id', 'qr', 'timestamp')

            param_error = False
            eng = ""
            for arg in args:
                if (arg in reqDict):
                    vars(self)[arg] = reqDict[arg]
                else:
                    param_error = True
                    eng += "Required attribute: {}".format(arg) + "; "
            if param_error:
                print(eng)
                raise MyError(self.getError('conflict'))

            code = reqDict.pop('qr')
            code_len = len(code)
            print("Code: '{}',  length: {}".format(code, str(code_len)))

            if self._driver_on_route is False:
                self.driver_registration(code, reqDict)
                reqDict['price'] = self.rate
                reqDict['ukr'] = self.get_vehicle_type_ukr(self.routeGuid) + str(self.routeName)
                reqDict['eng'] = self.get_vehicle_type_eng(self.routeGuid) + str(self.routeName)
                reqDict['route'] = self.routeGuid
                reqDict['equipment'] = self._equipment_list
                routeDict = dict(
                    type=201,
                    message_id=self._message_id,
                    route_info=dict(
                        name=self.get_vehicle_type_ukr(self.routeGuid) + str(self.routeName),
                        short=self.get_vehicle_type_short(self.routeGuid) + str(self.routeName),
                    ),
                    equipments=self._equipment_list,
                )
                print(routeDict)
                self.to_ikts(routeDict)
                self.to_driver(routeDict)

                self.goto_payment_mode()
            else:
                if self.code_validation(code, reqDict):
                    self.send_xdr(code)
        except MyError as e:
            print(e)
            reqDict['error'] = e.message
            reqDict['success'] = e.code
            self.to_validator(reqDict)
        except Exception as e:
            reqDict['error'] = e
            reqDict['success'] = -1
            self.to_validator(reqDict)
        self._message_id += 1
        return

    def alarmCB(self, reqDict):
        print("alarmCB")
        payload = dict(
            device_mac_address = self._mac,
            code = 201,
            staff_id = self.driverId,
            vehicle_id = self.vehicle_id,
            route_id = self.route_id,
            location = dict(
                lat = self.latitude,
                lng = self.longitude,
                timestamp = datetime.datetime.now().timestamp()
            )
        )
        #curl -i -X POST -H "AUTHORIZATION: Bearer F9898736657462791FDCAE1143F404DF" -d '{"route_id": 23, "location": {"lng": 0.0, "timestamp": 1504245387, "lat": 0.0}, "staff_id": 122, "vehicle_id": 59, "device_mac_address": "b827eb3001c2"}' http://st.atelecom.biz/mob/v1/front/alarms/danger
        #print(payload)
        url = 'http://st.atelecom.biz/mob/v1/front/alarms/danger'
        print("url: {}".format(url))
        print(payload)
        r = requests.post(url, headers=self.get_auth_header(), json=payload)
        if (r.status_code == 200):
            response = r.json()
            print(response)
        #else:
            #print(r)

    def call_operator_cb(self, reqDict):
        print("call_operator_cb")
        payload = dict(
            device_mac_address=self._mac,
            code=201,
            staff_id=self.driverId,
            vehicle_id=self.vehicle_id,
            route_id=self.route_id,
            location = dict(
                lat = self.latitude,
                lng = self.longitude,
                timestamp = datetime.datetime.now().timestamp()
            )
        )
        #curl -i -X POST -H "AUTHORIZATION: Bearer F9898736657462791FDCAE1143F404DF" -d '{"route_id": 23, "location": {"lng": 0.0, "timestamp": 1504245387, "lat": 0.0}, "staff_id": 122, "vehicle_id": 59, "device_mac_address": "b827eb3001c2"}' http://st.atelecom.biz/mob/v1/front/alarms/danger
        #print(payload)
        url = 'http://st.atelecom.biz/mob/v1/front/alarms/call-me'
        r = requests.post(url, headers=self.get_auth_header(), json=payload)
        print("url {}".format(url))
        print(payload)
        if (r.status_code == 200):
            response = r.json()
            print(response)

    def on_connect(self, client, payload, flag, rc):
        print("connected OK" if rc == 0 else "Bad connnection = {}".format(rc))

    def on_informer(self, client, userdata, message):
        print("Message from Informer received")
        try:
            payload_dict = json.loads(message.payload.decode("utf-8"))
            print("payload: ")
            print(payload_dict)

            _type = int(payload_dict.get('type', None))

            if _type == 0:  # 'Registration'
                self.informer_reg_cb(payload_dict)
            elif _type == 1:  # 'Driver'):
                #self.driverCB(payload_dict)
                pass
            elif _type == 10:  # QrValidation
                #self.qrValidationCB(payload_dict)
                pass
            elif _type == 11:
                #self.nfcValidationCB(payload_dict)
                pass
            elif _type == 100:
                #self.alarmCB(payload_dict)
                pass
            else:
                print("Unknown informator request 'type': '", payload_dict['_type'], "'")
                return False
            return True

        except ValueError as e:
            print(message.payload)
            print(message.payload.decode("utf-8"))
            print("Error JSON format: ", e)
            return False
        except KeyError as e:
            print(e)
            return False
        except Exception as e:
            print(e)
            return False

    def on_message(self, client, userdata, message):
        #print("on_message: {}".format(message.payload.decode("utf-8")))
        try:
            payload_dict = json.loads(message.payload.decode("utf-8"))
            #print("payload: {}".format(payload_dict))
            #print(payload_dict)

            _type = int(payload_dict.get('type', None))

            if _type == 0:  # 'Registration'
                self.on_validator_reg_cb(payload_dict)
            elif _type == 1:  # ):
                self.on_get_status_cb(payload_dict)
            elif _type == 10:  # QrValidation
                self.qrValidationCB(payload_dict)
            elif _type == 11:
                self.nfcValidationCB(payload_dict)
            elif _type == 110:
                self.on_gps_coordinates(payload_dict)
            elif _type == 120:
                self.on_start_leg(payload_dict)
            elif _type == 200:
                print("Registartion From Informator")
                self.informer_reg_cb(payload_dict)
            elif _type == 202:
                self.on_status_responce(payload_dict)
            elif _type == 230:
                self.on_message_viewed(payload_dict)
            elif _type == 250:
                self.on_event_recieved(payload_dict)
            else:
                print("Unknown request type: '{}'".format(_type))
                return False
            return True

        except ValueError as e:
            print(message.payload)
            print(message.payload.decode("utf-8"))
            print("Error JSON format: ", e)
            return False
        except KeyError as e:
            print(e)
            return False
        except Exception as e:
            print(e)
            return False

    def on_event_recieved(self, payload):
        event_id = payload['event_id']
        print(payload)
        print("on_event_recieved type:{}".format(event_id))
        if event_id == 1:
            self.alarmCB(payload)
        if event_id == 2:
            self.call_operator_cb(payload)



    # Send message to Validator
    def to_validator(self, payload):
        print("to_validator")
        self._message_id += 1
        payload['timestamp'] = int((time.time())) + self._utc_offset
        print(payload)
        resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
        self.client.publish("t_validator", resultJSON)
        return True

    def to_ikts(self, payload):
        print("to_ikts")
        self._message_id += 1
        payload['timestamp'] = int((time.time())) + self._utc_offset
        payload['mac'] = "5EBDABF60273"

        print(payload)
        resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
        self.client.publish("t_informer", resultJSON)
        return

    def to_driver(self, payload):
        print("to_driver")
        self._message_id += 1
        payload['timestamp'] = int((time.time())) + self._utc_offset
        payload['mac'] = self._mac
        print(payload)
        resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
        # print(resultJSON)
        self.client.publish("t_driver", resultJSON)
        return

    def local_exec(self):
        pass
        # print("local_exec")
        # self.check_validators()
        # self.check_ikts()
        # self.emmulate_gps()


        self._local_exec_cnt += 1

        if self._local_exec_cnt % 10 == 0:
            if self.token is not None:
                pass
                self.get_messages()
        if self._local_exec_cnt % 60 == 0:
            if self.token is not None:
                self.get_equipment_status();


    def check_internet(self):
        response = os.system("ping -c 1 " + "google.com")
        # and then check the response...
        if response == 0:
            print("hostname, is up!")
        else:
            print("hostname, is down!")

    def bkts_registration(self):
        print("bkts_registration")

        payload = dict(
            device_mac_address=self._mac,
            device_serial_number=self._mac,
            code=200,
            staff_id=self.driverId,
            vehicle_id=self.vehicle_id,
            route_id=self.route_id,
            sw_version=self._sw_version,
            hw_version=self._hw_version,
            status=200,
            mac=self._mac,
            location=dict(
                lat=0,
                lng=0,
                timestamp=int(datetime.datetime.now().timestamp())
            )
        )
        # Send request
        url = 'http://st.atelecom.biz/mob/v1/front/alarms/status'
        print("Sending request to '{}'".format(url))
        print("Payload")
        print(payload)
        r = requests.post(url, json=payload, headers=self.get_auth_header())
        print('RESPONCE')
        print(r)

    def run(self):
        broker = "localhost"
        self.client = mqtt.Client("BKTS")  # create new instance
        self.client.on_connect = self.on_connect  # attach function to callback
        self.client.on_message = self.on_message  # attach function to callback

        print("Connection to broker ", broker)
        try:
            self.client.connect(broker)

        except Exception as e:
            print("Can't connect: ", e)
            exit(1)
        else:
            self.client.loop_start()
            self.client.subscribe("t_bkts")

            self.check_driver_registration()

            i = 0
            loop_flag = 1
            while loop_flag == 1:
                time.sleep(1)
                if self.token is not None:
                    self.local_exec()

            self.client.loop_stop()
            self.client.disconnect()

# *****************************************************************************************
if __name__ == "__main__": main()
