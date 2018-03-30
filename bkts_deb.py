#!/usr/bin/python3
'''
*************************** EQUPMENT ****************************
database: `equipment`
enppoint: mob/v1/front/equipments/index?vehicle=vehicle_id
function: get_equipment_list()
Types: BKTS:1, Validator:2, IKTS:4
Then: send_equipment_list
Equipment index:
        0:Modem
        1:GPS
        2:LSpeaker
        3:Display
        4:RSpeaker
        5:IKTS
        6:Mobile terminal
        7:BKTS
        8:Validator1
        9:Validator2
        10:Validator3
'''
import paho.mqtt.client as mqtt
import time
import datetime
import sys, os
import traceback
import urllib.request
import logging
import requests
import json
import threading
import sqlite3
import gps_emulator
from uuid import getnode as get_mac

def main():
    _script_dir = os.path.dirname(os.path.realpath(__file__)) + "/"

    logfile = _script_dir + 'bkts.log'

    try:
        if "debug" in sys.argv:
            logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                            level=logging.DEBUG)
            print("Debug is On...")
        elif "info" in sys.argv:
            logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                                level=logging.INFO)
            print("INFO is On...")
        else:
            logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                            level=logging.WARNING, filename=logfile)

        logging.debug("Start main!")
        App()
    except KeyboardInterrupt:
        logging.debug("Shutdown requested...exiting")
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(0)


class RegistrationError:
    def __init__(self):
        pass


class MyError(Exception):
    def __init__(self, _error: object)->object:
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

        self._script_dir = os.path.dirname(os.path.realpath(__file__)) + "/"

        # CONSTANTS
        self.VERSION = "1.0.0"
        self.HW_VERSION = "Rasberry Pi 3"

        self.LEGLIST_URL = 'mob/v1/leglist/{}'
        self.REPAYMENT_URL = 'mob/v1/multy_repayment/{}'
        self.COORDINATE_URL = "https://telecard.online:3000/coords"

        self.DATABASE = self._script_dir + 'bkts.db'
        self.ROUTE_JSON = self._script_dir + 'route.json'
        self.TRACE_JSON = self._script_dir + 'trace.json'
        self.DRIVER_JSON = self._script_dir + 'driver.json'
        self.VEHICLE_JSON = self._script_dir + 'vehicle.json'
        self.SESSION_JSON = self._script_dir + 'session.json'
        self.BKTS_DUMP = self._script_dir + 'bkts_dump.json'

        self.SCHEDULE_JSON = self._script_dir + 'schedule.json'
        self.POINTS_JSON = self._script_dir + 'points.json'

        # stop_distance = 0.000547559129223524
        # self.stop_distance  = 0.000000299820999996023854551154978576
        self.gps_emulator_run = False
        self.ARRIVAL_RADIUS   = 0.00000015
        self.DEPARTURE_RADIUS = 0.00000020

        self.current_mode = "REGISTRATION"

        self._leg_initialized = False
        self._db = None
        self._errorMessages = None
        self._cursor = None

        self._internet_status = True
        self._gps_status = True
        self._gps_cnt = 0
        self.transaction_cnt = 0

        self.last_duration = None
        self.last_code = None

        self._sw_version="1.0.7"
        self._hw_version="RASPBERRY PI 3 MODEL B",
        self._mac = hex(get_mac())[2:14]
        self._mac = self._mac.upper()

        logging.info("my MAC is: {}".format(self._mac))

        self._actual_route_info = False
        self.vehicle_type_ukr = None
        self.route_dict_eng = None
        self._message_id = 1
        self.vehicle_type_short = None

        self._trace_info = None;

        #GPS BLOCK
        self._gps_idx=0
        self.latitude = 0.0
        self.longitude = 0.0
        self.stop_distance = self.ARRIVAL_RADIUS

        self.validator_dict = {}
        self.ikts_dict = {}
        self._ikts_mac = "6629F1F17015"

        self._last_deviation = 0

        self._prev_order = None
        self._curr_order = None
        self._curr_point_name = None
        self._curr_point_id = None
        self._curr_schedule_id = None
        self._curr_schedule_time = None
        self._curr_weekday = datetime.datetime.now().isoweekday()
        self.last_point_id = None
        self.last_point_name = None

        self.arrival_time = None

        self._equipment_list = None

        self._trusted_updeted = False
        self._multipass_updeted = False

        self._direction = None
        self._curr_round = None
        self.new_search = True

        self.token = None

        self._driver_on_route = False
        self._driver_exist = False
        self._driver_on_vehicle = False
        self.driver_id = None
        self.driver_name = None
        self.driver_card_number = None

        self.vehicle_id = None

        self.route_name = None
        self.route_id = None
        self.route_guid = None
        self.route_rate = None
        self.route_desc = None
        self.route_interval = None
        self.route_working_hours = None
        self.route_updated_at = None

        self.vehicle_type_ukr = None
        self.vehicle_type_eng = None

        self._last_click_time = 0

        #self._tz = pytz.timezone('Europe/Kiev')
        self._dst = time.daylight and time.localtime().tm_isdst > 0
        self._utc_offset = - (time.altzone if self._dst else time.timezone)

        self._local_exec_cnt = 0

        self.do_send_equipment_status = False


        thread = threading.Thread(target=self.local_exec_in_thred, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

        self.start()

    def dist(self, long1, lat1, long2, lat2):
        x = long1 - long2
        y = lat1 - lat2
        return x*x + y*y

    def db_init(self):
        logging.info("db_init")
        #self._db.create_function("dist", 4, self.dist)
        try:
            self.db().execute("DROP TABLE IF EXISTS point")
            #Create point
            sql = "CREATE TABLE IF NOT EXISTS point " \
                  "(`id` INTEGER," \
                  "`name` TEXT," \
                  "`order` INTEGER," \
                  "`direction` INTEGER," \
                  "`type` INTEGER DEFAULT 1," \
                  "`entrance` INTEGER DEFAULT 1," \
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

            #Create leg table
            self.db().execute("DROP TABLE IF EXISTS leg")
            sql = 'CREATE TABLE IF NOT EXISTS `leg` '\
                  '(`id` INTEGER primary key,'\
                  '`name` TEXT,'\
                  '`stime` TEXT,'\
                  '`period` INTEGER,'\
                  '`variation` INTEGER,' \
                  '`order` INTEGER DEFAULT 1)'
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
            # self._db.execute("DROP TABLE IF EXISTS equipment")
            sql = "CREATE TABLE IF NOT EXISTS `equipment` " \
                  "(`mac` TEXT primary key," \
                  "`serial_number` TEXT," \
                  "`type` INTEGER," \
                  "`i_vehicle` INTEGER DEFAULT 0," \
                  "`last_status` INTEGER DEFAULT -1," \
                  "`cnt` INTEGER DEFAULT -1)"
            self.db().execute(sql)

            # CREATE deferred
            self._db.execute("DROP TABLE IF EXISTS deferred")
            sql = "CREATE TABLE IF NOT EXISTS deferred " \
                  "(`id` INTEGER PRIMARY KEY," \
                  "`route_guid` TEXT," \
                  "`vehicle_id` INTEGER," \
                  "`mac` TEXT," \
                  "`code` TEXT," \
                  "`t_counter` INTEGER," \
                  "`latitude` TEXT," \
                  "`longitude` TEXT," \
                  "`timestamp` INTEGER," \
                  "`type` INTEGER DEFAULT 0)"   # 0 - regular/trusted, 1 - multypass
            self.db().execute(sql)

            # CREATE multipass
            self._db.execute("DROP TABLE IF EXISTS multipass")
            sql = "CREATE TABLE IF NOT EXISTS multipass " \
                  "(`code` TEXT PRIMARY KEY)"
            self.db().execute(sql)

            # CREATE trusted
            self._db.execute("DROP TABLE IF EXISTS `trusted`")
            sql = "CREATE TABLE IF NOT EXISTS `trusted` " \
                  "(`code` TEXT PRIMARY KEY," \
                  "`quantity` INTEGER DEFAULT 0," \
                  "`amount` INTEGER DEFAULT 0)"
            self.db().execute(sql)

            # self._db.execute("DROP TABLE IF EXISTS `leglist`")
            sql = "CREATE TABLE IF NOT EXISTS `leglist` " \
                  "(`id` INTEGER PRIMARY KEY," \
                  " `code` TEXT," \
                  " `created_at` INTEGER)"
            self.db().execute(sql)

            self._db.execute("DROP TABLE IF EXISTS `refund`")
            sql = "CREATE TABLE IF NOT EXISTS `refund` " \
                  "(`id` INTEGER PRIMARY KEY," \
                  "`code` TEXT," \
                  "`vehicle_id` INTEGER," \
                  "`route_guid` TEXT,"\
                  "`created_at` INTEGER)"
            self.db().execute(sql)


            self.db().commit()

            #DISCONNECT
            self.db().close()
            self._db = None

        except sqlite3.Error as e:
            logging.error("DB ERROR: " + str(e))

    def db(self):
        if self._db is None:
            logging.debug("connect to database")
            self._db = sqlite3.connect(self.DATABASE, check_same_thread=False, timeout=10)
            # self._db = sqlite3.connect(self.DATABASE, timeout=10)
            self._db.isolation_level = None
            self._db.create_function("dist", 4, self.dist)
            self._db.create_function("t_diff", 2, self.t_diff)
        return self._db

    def db_exec(self, sql):
        try:
            return self.db().execute(sql)
        except sqlite3.Error as e:
            logging.error("DB ERROR: {}, sql: '{}'".format(str(e), sql))
            raise MyError(self.get_response('db_error'))

    def db_execute(self, sql, params):
        try:
            return self.db().execute(sql, params)
        except sqlite3.Error as e:
            logging.error("DB ERROR: {}, sql: '{}', params: {}".format(str(e), sql, str(params)))
            raise MyError(self.get_response('db_error'))

    def db_executemany(self, sql, params):
        try:
            return self.db().executemany(sql, params)
        except sqlite3.Error as e:
            logging.error("DB ERROR: {}, sql: '{}', params: {}".format(str(e), sql, str(params[0])))
            raise MyError(self.get_response('db_error'))

    # Error`s Dictionary
    def get_response(self, name):
        if self._errorMessages is None:
            self._errorMessages = dict(
                success=dict(
                    error=dict(
                        eng=None,
                        ukr=None
                    ),
                    code=0
                ),
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
                        ukr="Невідома помилка",
                    ),
                    code=-1
                ),
                not_found=dict(
                    error=dict(
                        eng="Not Found",
                        ukr="Не знайдено",
                    ),
                    code=404
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
        if not route_prefix:
            return "''"

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
        if not route_prefix:
            return "''"

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
        if not route_prefix:
            return "''"

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

        '''
        if self.internet_status is False:
            return False
        '''

        logging.debug("get_messages")
        if self.driver_id is None:
            return False

        sql = "SELECT MAX(`id`) FROM message"
        c = self.db_exec(sql)
        row = c.fetchone()
        last_message_id = 0 if row[0] is None else row[0]
        c.close()

        url = 'mob/v1/message/{}/{}'.format(self.driver_id, last_message_id)
        r = self.to_atelecom("GET", url, None)
        if not r:
            logging.debug("Can not recieve new messages")
            return False
        if r.status_code == requests.codes.ok:
            response = r.json()
            insert = "INSERT OR IGNORE INTO message (`id`,`title`,`text`,`created_at`) VALUES (?,?,?,?)"
            for message in response:
                logging.debug(message)
                m_id = int(message.get('id'))
                title = message.get('title')
                text = message.get('text')
                created_at = int(message.get('created_at'))
                self.db_execute(insert,(m_id,title,text,created_at))

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
        logging.debug("on_message_viewed")
        logging.debug(str(payload_dict))
        try:
            if(payload_dict['mesg_id']) is not None:
                sql = "UPDATE message SET new=0 WHERE id ={mesg_id}".format(mesg_id=payload_dict['mesg_id'])
                self.db_exec(sql)
        except KeyError as e:
            logging.error(str(e))

    # @staticmethod
    def t_diff(self, ts1, ts2, unsigned=True):
        if ts1 is None or ts2 is None:
            return -200000
        t1 = datetime.datetime.strptime(ts1, '%H:%M:%S').time()
        t2 = datetime.datetime.strptime(ts2, '%H:%M:%S').time()
        td1 = datetime.timedelta(hours=t1.hour, minutes=t1.minute, seconds=t1.second)
        td2 = datetime.timedelta(hours=t2.hour, minutes=t2.minute, seconds=t2.second)
        delta = td1 - td2
        total_sec = delta.total_seconds()
        if unsigned and total_sec < 0:
            total_sec = total_sec * (-1)
        return int(total_sec)

    def send_route_info(self, route_dict):
        logging.debug("send_route_info {}". format(str(route_dict)))

        route_info = []
        try:
            route_info.append( {"item": "Маршрут", "desc": route_dict.get('description', "Unknown") } )
            route_info.append( {"item": "Вартість", "desc": "{} грн".format(str( route_dict.get('rate', 0)/100))})
            route_info.append( {"item": "Інтервал", "desc": route_dict.get('interval', "Unknown") } )
            route_info.append( {"item": "Компанія", "desc": route_dict.get('company_name',"Unknown")} )
            route_info.append( {"item": "Робочі години", "desc": route_dict.get('working_hours', "Unknown")} )
            route_info.append( {"item": "Оновлення", "desc": time.strftime("%Y-%m-%d %H:%M:%S",time.localtime( route_dict.get('updated_at',0)))} )
        except KeyError as e:
            logging.error("Key error in route_dict {}".format(str(e)))


        payload = dict (
            type=240,
            desc= route_info,
        )
        self.to_driver(payload)

    def get_route_info(self, driver_id):
        logging.debug("get_route_info")

        url = 'mob/v1/front/staff/route?id={}'.format(driver_id)
        r = self.to_atelecom("GET", url)
        if r and r.status_code == 200:
            response = r.json()

            try:
                points = response.get('points', None)
                logging.debug("Point count: {}".format(str(len(points))))

                schedule = response.get('schedule', None)
                logging.debug("Schedule count: {}".format(str(len(schedule))))
            except KeyError as e:
                logging.error("Key Error: {}".format(str(e)))
                return False
        else:
            logging.error("No route info. Response: {}".format(str(r)))
            return False

        try:
            logging.debug("WRITE: " + self.POINTS_JSON)
            with open(self.POINTS_JSON, 'w') as outfile:
                json.dump(points, outfile)
            outfile.close()

            logging.debug("WRITE: " + self.SCHEDULE_JSON)
            with open(self.SCHEDULE_JSON, 'w') as outfile:
                json.dump(schedule, outfile)
            outfile.close()
        except Exception as e:
            logging.error("File writing error {}".format(str(e)))
            sys.exit()

        sql = "DELETE FROM point"
        self.db_exec(sql)

        logging.debug("************************************************")
        '''
        '''
        url = 'mob/v1/front/routes/{}'.format(self.route_id)
        r = self.to_atelecom("GET", url)

        logging.debug("WRITE: " + self.TRACE_JSON)
        if r and r.status_code == 200:
            self._trace_info = r.json()
            with open(self.TRACE_JSON, 'w') as outfile:
                json.dump(self._trace_info, outfile)
            outfile.close()
            # print(response)

        sql = "INSERT OR IGNORE INTO point (`id`,`name`,`order`,`direction`,`radius`,`longitude`," \
              "`latitude`,`now_audio_url`,`now_audio_dttm`,`now_video_url`,`now_video_dttm`,`future_audio_url`," \
              "`future_audio_dttm`,`future_video_url`,`future_video_dttm`) VALUES (:id,:name,:order,:direction," \
              ":radius,:longitude,:latitude,:now_audio_url,:now_audio_dttm,:now_video_url,:now_video_dttm," \
              ":future_audio_url,:future_audio_dttm,:future_video_url,:future_video_dttm)"

        logging.debug("`id`,`name`,`order`,`direction`,`radius`,`lons`," \
              "`lat`,`now_audio_url`,`now_audio_dttm`,`now_video_url`,`now_video_dttm`,`future_audio_url`," \
              "`future_audio_dttm`,`future_video_url`,`future_video_dttm`")
        for point in points:
            # logging.debug(str(point))
            self.db_execute(sql, point)

        sql = "DELETE FROM schedule"
        self.db_exec(sql)

        sql = "INSERT OR IGNORE INTO schedule (`station_id`,`direction`,`round`,`date`,`time`) VALUES " \
              "(:station_id,:direction,:round,:date,time(substr('00000'||:time, -5, 5)))"
        # self.db_executemany(sql, schedule)
        self.db().commit()

        self.init_schedule_table()

        return points

    def send_trace_info(self):

        payload = {
            "type" : 380,
            "timestamp" : 0,
            "message_id" : self._message_id,
            "trace" : self._trace_info,
        }
        self.to_driver(payload)

    def get_auth_header(self):
        if self.token is None:
            logging.error("NOT AUTHORISED")
            return None
            # raise MyError(self.getError('notAuth'))
        else:
            return dict(AUTHORIZATION='Bearer {}'.format(self.token))

    def find_round_in_schedule(self, point_id):
        logging.info("search point id {}".format(point_id))
        self.new_search = False

        dt = datetime.datetime.now()
        time_now = dt.strftime("%H:%M")
        self._curr_weekday = dt.isoweekday()

        # logging.debug("Now time: {}, weekday: {}".format(time_now, self.current_weekday))

        sql = "SELECT `round` FROM `schedule` " \
              "WHERE `station_id`= :station_id AND `date`=:wd AND `direction`=:dir " \
              "ORDER BY t_diff(time(`time`),time(:time)) LIMIT 1"

        params = {
            "dir": self._direction,
            "time": time_now,
            "wd": self._curr_weekday,
            "station_id": point_id,
        }

        row = self.db_execute(sql,params).fetchone()
        if row is not None:
            logging.info("CURRENT ROUND: {}".format(str(row[0])))
            self._curr_round = row[0]
            return row[0]
        else:
            return None

        # self._leg_initialized = False
        # self.init_leg_table()

    def init_leg_table(self):
        if self._leg_initialized:
            return False
        self._leg_initialized = True

        logging.debug("init_leg_table round: {}, weekday: {}, direction: {}".format(self._curr_round, self._curr_weekday, self._direction))
        sql="DELETE FROM `leg`"
        self.db_exec(sql)

        dt = datetime.datetime.now()
        time_now = dt.time()

        sql = "SELECT s.`id`, p.`name`, s.time, p.`id`, p.`order` " \
              "FROM point p LEFT JOIN schedule s " \
              "ON s.`direction`=p.`direction` AND s.`station_id`=p.`id` AND s.`round`=:round AND s.`date`= :wd  " \
              "WHERE p.`direction`=:dir AND p.`type`=1 " \
              "ORDER BY p.`order`"
        params = {"round": self._curr_round, "wd": self._curr_weekday, "dir": self._direction}
        cursor = self.db_execute(sql, params)

        insert = "INSERT INTO leg (`id`,`name`,`stime`,`variation`,`period`,`order`) " \
                 "VALUES (:id,:name,:stime,:var,:period,:order)"

        first_time = None
        for row in cursor:
            # logging.debug(str(row))
            if row[2] is None:
                stime = 2000
            else:
                stime = row[2]

            if first_time is None and stime is not None:
                first_time = stime
                params = {
                    "id" : row[3],
                    "name" : row[1],
                    "stime" :  stime,
                    "period" : 0,
                    "var" : -2000,
                    "order": row[4],
                }
            else:
                params = {
                    "id" : row[3],
                    "name" : row[1],
                    "stime" :  stime,
                    "period" : self.t_diff(stime, first_time) if row[2] is not None else 2000,
                    "var" : -2000,
                    "order": row[4],
                }
                # logging.debug(str(params))
            self.db_execute(insert, params)
        cursor.close()
        self.db().commit()

        # self.update_schedule_table()

    def update_schedule_table(self):
        logging.info("update_schedule_table")
        self.init_leg_table()

        sql = "SELECT `name`,`period`,`variation`,`id`,`order` FROM leg ORDER BY `order`"
        cursor = self.db_exec(sql)

        self._last_deviation = 0

        schedule = []
        for row in cursor:
            # schedule.append(dict(zip(('name', 'schedule', 'lag'), row)))
            if row[2] >= -1000:
                self._last_deviation = (-1) * int(row[2] / 60)
            else:
                self._last_deviation = 0

            schedule.append(dict(
                name=row[0],
                # schedule=int(row[1]/60) if (row[1]>0)  else row[1],
                # schedule=int(row[1]/60) if ((row[1]>0) and (row[1] != 2000)) else row[1],
                schedule= -1000 if (row[1]>0)  else row[1],
                lag=int(row[2]) if row[2] < -1000 else self._last_deviation,
            ))
        cursor.close()
        if len(schedule) == 0:
            return False
        else:
            logging.info(str(schedule))
        payload = dict(
            type=330,
            schedule=schedule
        )
        self.to_driver(payload)
        self.set_driver_status_bar()

    def init_schedule_table(self):
        logging.debug("init_schedule_table")
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
        logging.debug(str(schedule))
        payload = dict(
            type=330,
            schedule=schedule
        )
        self.to_driver(payload)


    def change_le_table_on_stop(self, shedule_id):
        pass

    # MQTT Callbacks
    #Informer Registration CallBack
    def start_leg(self):
        logging.debug("start_leg")
        # Send request
        '''
        payload = dict(
            vehicle_id=self.vehicle_id,
        )
        url = 'mob/v1/repayment'
        r = self.to_atelecom('DELETE', url, payload)
        '''

    def on_gps_coordinates(self, reqDict):
        '''
        preset params self._prev_order = None, self._direction = 1
        Arrival: if self._prev_order is None:
            self._prev_order = self._current_order
        Arrival: if self._prev_order > self._current_order:
                    self.change_direction()

        :param reqDict:
        :return:
        '''
        self._gps_cnt = 0

        try:
            lat = float(reqDict['latitude'])
            lon = float(reqDict['longitude'])
        except KeyError as e:
            logging.error(str(e))
            return False

        # save coordinates
        (self.latitude, self.longitude) = (lat, lon)
        logging.debug("on_gps_coordinates lat: {}, lon: {}".format(str(lat), str(lon)))

        # Find direction
        '''
        if self._direction is None:
            sql = "SELECT `latitude`,`longitude`,`id`,`order` FROM `point` " \
                  "WHERE `type`=1 AND `direction`= :dir " \
                  "ORDER BY `order` LIMIT 1"
            logging.debug("Find first stop in derection 1")
            point = self.db_execute(sql, {"dir":1}).fetchone()
            # Are we here?
            if point is not None:
                distance = self.dist( lat, lon, point[0], point[1])
                logging.debug("distance: {}".format(str(distance)))
                if distance < self.ARRIVAL_RADIUS:
                    self._direction = 1
                    logging.debug("Find first stop in derection 2")
            point = self.db_execute(sql, {"dir":2}).fetchone()
            # Are we here?
            if point is not None:
                distance = self.dist( lat, lon, point[0], point[1])
                logging.debug("distance: {}".format(str(distance)))
                if distance < self.ARRIVAL_RADIUS:
                    self._direction = 2
        '''

        #normalaise direction to 1 or 2
        self._direction = 1 if self._direction == 1 else 2
        logging.debug( "Direction: {}. Order {}".format(self._direction, self._curr_order) )

        # searching for where we are
        sql = "SELECT `id`,`name`,`order` FROM point " \
              "WHERE `type`=1 AND `direction`=:dir AND dist(:lat, :lon, `latitude` ,`longitude`) < :dist"
        params = {"dir":self._direction, "lat":lat, "lon":lon, "dist":self.stop_distance}

        row = None
        #row = self.db_execute(sql,params).fetchone()

        if row is not None:
            # We are near a stop
            logging.info("Near the Stop: {}".format(str(row)))
            (self._curr_point_id, point_name, self._curr_order) = row

            if self._prev_order is None:
                self._prev_order = self._curr_order
            elif self._curr_order < self._prev_order:
                self.change_direction()

            #serch round/leg
            if self._curr_round is None:
                self.find_round_in_schedule(self._curr_point_id)

            # Check for arrival
            if self._curr_point_name is None:
                self._curr_point_name = point_name
                logging.debug("Current s_id: {}, p_id {}, round: {} time: {}".format(str(self._curr_schedule_id), str(self._curr_point_id), str(self._curr_round), str(self._curr_schedule_time)))
                self.on_arrival()
        else:
            # Check for departure
            if self._curr_point_name is not None:
                self.on_departure(self._curr_point_name)
                self._curr_point_name = None

    def change_direction(self):
        logging.info("change_direction")
        self._direction = 1 if self._direction == 2 else 2
        # self._direction = None
        self._curr_round = None
        self._curr_point_name = None
        self.stop_distance = self.DEPARTURE_RADIUS
        self.new_search = True
        self._leg_initialized = False

        self.start_leg()

    def check_ikts(self):
        #logging.debug("check_ikts")
        if self.ikts_dict is not None:
            logging.debug(str(self.ikts_dict))
            for mac in self.ikts_dict:
                if mac is not None:
                    if self.ikts_dict[mac]['cnt'] > 0:
                        logging.warning("IKTS: {} is not in order".format(mac))

                    self.ikts_dict[mac]['cnt'] = self.ikts_dict[mac]['cnt'] + 1
                    payload = dict(
                            type=202,
                            timestamp=int(datetime.datetime.now().timestamp()),
                            mac=mac,
                    )
                    self.to_ikts(payload)

    def check_validators(self):
        logging.debug("check_validators")
        if self.validator_dict is not None:
            for mac in self.validator_dict:
                logging.debug(str(self.validator_dict[mac]))
                if mac is not None:
                    if self.validator_dict[mac]['cnt'] > 0:
                        logging.warning("VALIDATOR: {} is not in order".format(mac))
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

    def on_arrival(self):
        logging.info("Arrive to: '{}'".format(self._curr_point_name))

        if self._curr_round is not None:
            # Find Schedule detail information
            sql = "SELECT `id`, `time` FROM schedule " \
                  "WHERE `direction`= :dir AND `round`= :round AND `station_id`= :station_id AND `date`= :wd LIMIT 1"
            params = {
                "dir": self._direction,
                "round": self._curr_round,
                "station_id": self._curr_point_id,
                "wd": self._curr_weekday
            }
            row = self.db_execute(sql, params).fetchone()
            if row is not None:
                (self._curr_schedule_id, self._curr_schedule_time) = row

        dt = datetime.datetime.now()
        self.arrival_time = dt.strftime('%H:%M:%S')
        logging.info("arrival time: {}, schedule time: {}".format(self.arrival_time, self._curr_schedule_time))

        if self._curr_schedule_time is not None:
            variation = self.t_diff(self.arrival_time, self._curr_schedule_time, False)
        else:
            variation = 200000
            logging.info("Variation: {}".format(variation))

        stop_info = {"type": 20, "ukr": self._curr_point_name, "eng": ""}
        self.to_validator(stop_info)

        #Update LEG table
        logging.debug("Updating leg table 'order: {}'".format(self._curr_order))
        sql = "UPDATE leg SET period = 0, variation=:var WHERE `order`= :order"
        params = {"var": variation, "order": self._curr_order}
        self.db_execute(sql, params)

        sql = "UPDATE leg SET `period`=-2000 WHERE `order` < :order"
        self.db_execute(sql, {"order": self._curr_order})

        update = "UPDATE leg SET period = t_diff(time(:cst), time(`stime`)), variation= -2000 WHERE `order` > :order"
        params = { "cst": self._curr_schedule_time, "order": self._curr_order}
        self.db_execute(update, params)
        self.db().commit()

        self.update_schedule_table()
        # **************************************************
        stop_info = dict(
            type=220,
            difference=variation,
            schedule_id=self._curr_schedule_id,
            direction=self._direction,
            round=self._curr_round,
        )
        #SERCH STOP INFORMATION
        sql = "SELECT `name`, `id`, `now_audio_url`, `now_audio_dttm`, `now_video_url`, `now_video_dttm`, " \
              "`future_audio_url`, `future_audio_dttm`, `future_video_url`, `future_video_dttm` " \
              "FROM point WHERE `type`= 1 AND `order`>= :co AND `direction` = :dir ORDER BY `order` LIMIT 3"

        params = {"dir":self._direction, "co":self._curr_order}
        cursor = self.db_execute(sql, params)

        prev_schedule_time = None
        cnt = 0
        properties = ('curr_stop_info', 'next1_stop_info', 'next2_stop_info')
        for _property in properties:
            row = cursor.fetchone()
            if row is not None:
                cnt += 1
                sql = "SELECT `time` FROM `schedule` " \
                      "WHERE `station_id`= :sid AND `direction`= :dir AND `round`= :round LIMIT 1"
                params = { "sid": row[1], "dir": self._direction, "round": self._curr_round}

                schedule_row = self.db_execute(sql, params).fetchone()

                curr_schedule_time = schedule_row[0] if schedule_row is not None else None
                if prev_schedule_time is None:
                    prev_schedule_time = curr_schedule_time
                eta = self.t_diff(curr_schedule_time, prev_schedule_time, True)
                prev_schedule_time = curr_schedule_time

                stop_info[_property] = dict(
                    route_id=self.route_id,
                    stop_id=self._curr_point_id,
                    ukr=row[0],
                    eta=eta,
                    now_audio_url=row[2],
                    now_audio_dttm=row[3],
                    now_video_url=row[4],
                    now_video_dttm=row[5],
                    future_audio_url=row[6],
                    future_audio_dttm=row[7],
                    future_video_url=row[8],
                    future_video_dttm=row[9],
                    direction=self._direction,
                )
            else:
                stop_info[_property] = dict(
                    route_id=self.route_id,
                    stop_id=self._curr_point_id,
                    ukr="",
                    eta=0,
                )
                logging.debug(str(stop_info[_property]))
        self.to_ikts(stop_info)

        logging.debug("CNT = {}".format(cnt))
        if cnt < 2:
            self.change_direction()

    def on_departure(self, station):
        logging.info("Departure from: '{}'".format(station))
        self._curr_point_name = None

        stop_info = None
        next_stop_name = None

        self.stop_distance = self.ARRIVAL_RADIUS
        # SERCH STOP  INFORMATION
        if self._curr_order is not None:
            sql = "SELECT p.`name`,p.`id`,p.`now_audio_url`,p.`now_audio_dttm`,p.`now_video_url`,p.`now_video_dttm`," \
                  "p.`future_audio_url`,p.`future_audio_dttm`,p.`future_video_url`,p.`future_video_dttm` " \
                  "FROM `point` p " \
                  "WHERE p.`type`=1 AND p.`direction`= :dir AND p.`order`>= :current_oder " \
                  "ORDER BY p.`order` LIMIT 4"
            params = {
                "dir":self._direction,
                "current_oder":self._curr_order,
                "round":self._curr_round,
            }
            result = self.db_execute(sql, params).fetchall()

            sql = "SELECT `id`,`time` FROM `schedule` " \
                  "WHERE `time`>=:st AND `date`=:wd AND `direction`=:dir AND `round`=:round AND station_id=:station_id " \
                  "ORDER by `time` LIMIT 1"

            next_stop_name = None
            current_stot_time = None

            stop_info = dict(
                type=221,
                round=self._curr_round,
                direction=self._direction,
            )

            properties = ('curr_stop_info', 'next1_stop_info', 'next2_stop_info', 'next3_stop_info')
            i=0
            for row in result:
                logging.debug(sql)
                logging.debug(str(row[1]))
                params = {
                    "st":self._curr_schedule_time,
                    "wd":self._curr_weekday,
                    "dir":self._direction,
                    "round":self._curr_round,
                    "station_id":row[1]}

                station_row = self.db_execute(sql,params).fetchone()

                logging.debug(str(station_row))

                if station_row is not None and current_stot_time is None:
                    current_stot_time = station_row[1]

                _property = properties[i]
                i += 1

                if _property == "next1_stop_info":
                    next_stop_name = row[0]

                _stop_info = {}
                _stop_info["route_id"] = self.route_id
                _stop_info["stop_id"] = self._curr_point_id
                _stop_info["ukr"] = row[0]
                _stop_info["now_audio_url"] = row[2]
                _stop_info["now_audio_dttm"] = row[3]
                _stop_info["now_video_url"] = row[4]
                _stop_info["now_video_dttm"] = row[5]
                _stop_info["future_audio_url"] = row[6]
                _stop_info["future_audio_dttm"] = row[7]
                _stop_info["future_video_url"] = row[8]
                _stop_info["future_video_dttm"] = row[8]
                _stop_info["direction"] = self._direction
                if station_row is not None:
                    _stop_info["eta"] = self.t_diff(station_row[1], current_stot_time)

                stop_info[_property] = _stop_info

        result_len = len(result)
        logging.debug("LEN : {}".format(result_len))

        if stop_info is not None:
            self.to_ikts(stop_info)

        # self.to_driver(stop_info)
        logging.debug("next_stop_name: {}".format(str(next_stop_name)))
        if next_stop_name is not None:
            self.to_validator({"type":21,"ukr":next_stop_name,"eng":""})

    def get_points(self):
        logging.debug("get_points")

    def ikts_registration_cb(self, reqDict):
        logging.debug("ikts_registration_cb: '{}'".format(str(reqDict)))

        error = ""
        args = ('mac', 'message_id', 'status', 'sw_version','hw_version', 'timestamp')
        try:
            mac = reqDict['mac']
            # message_id = reqDict['message_id']
            status = reqDict['status']
            sw_version = reqDict['sw_version']
            hw_version = reqDict['hw_version']
            timestamp = reqDict['timestamp']
        except KeyError as e:
            logging.error("Required attribute: '{}'".format(str(e)))

        if mac.upper() == self._mac.upper():
            # Registration from Driver Terminal
            logging.info("Driver terminal registration")
            reqDict['timestamp'] = int(time.time())
            reqDict['success'] = 0
            self.to_driver(reqDict)
            # Send Equipment List
            # self.send_equipment_status()
            self.do_send_equipment_status = True

            if self._driver_on_route:
                self.goto_payment_mode()
            else:
                self.goto_registration_mode()

            return True

        self._ikts_mac = mac

        payload = dict(
            device_mac_address=self._ikts_mac,
            device_serial_number=self._ikts_mac,
            code=200,
            staff_id=self.driver_id,
            vehicle_id=self.vehicle_id,
            route_id=self.route_id,
            sw_version=sw_version,
            hw_version=hw_version,
            status=200,
            mac=self._ikts_mac,
            location=dict(
                lat=self.latitude,
                lng=self.longitude,
                timestamp=int(time.time())
            )
        )
        # Send request
        logging.info("IKTS registration request: {}".format(str(payload)))
        r = self.to_atelecom('POST', 'mob/v1/front/alarms/status', payload)
        if r:
            logging.info("Responce: {} text: {}".format(str(r), str(r.text)));

        # if r.status_code == requests.codes.ok:

        if True:
            '''
            response = r.json()
            logging.debug(str(response))
            '''
            reqDict['timestamp'] = int(time.time())
            reqDict['success'] = 0
            self.to_ikts(reqDict)

            ikts=dict(
                mac=self._ikts_mac,
                status=status,
                sw_version=sw_version,
                hw_version=hw_version,
            )
            self.ikts_dict[self._ikts_mac] = ikts
            return True
        return False

    # Validator regisration event
    def on_validator_reg_cb(self, reqDict):
        logging.info('on_validator_reg_cb')
        # Create validators dictionary
        try:
            validator = dict(
                type=reqDict['type'],
                mac=reqDict['validator_id'],
                status=reqDict['status'],
                sw_version=reqDict['sw_version'],
                hw_version=reqDict['hw_version'],
                last_status=reqDict['status'],
                in_order=True,
                cnt=0,
            )
        except KeyError as e:
            logging.error("While Vaidator registration, required key '{}'".format(str(e)))
            result = dict(
                timestamp=datetime.datetime.now().timestamp(),
                success=1,
                price=0,
            )
            self.to_validator(result)

        result = dict(
            type=reqDict['type'],
            validator_id=reqDict['validator_id'],
            message_id=reqDict['message_id'],
            timestamp=datetime.datetime.now().timestamp(),
            success=0,
            route='',
            price=0,
        )
        logging.info("Validator '{}' registration success".format(reqDict['validator_id']))
        self.to_validator(result)

        self.validator_dict[reqDict['validator_id']] = validator
        logging.debug("Validator dictionary: {}".format(str(self.validator_dict)))

        # Send validator registration request
        logging.debug('Request Validator registration')
        headers = dict(AUTHORIZATION='Bearer {}'.format(reqDict['validator_id']))
        payload = dict(
            hw_version= reqDict['hw_version'],
            sw_version= reqDict['sw_version'],
            status=reqDict['status'],
        )
        r = self.to_atelecom("PUT", "bkts/api/registration")

        if (r is not False) and (r.status_code == 200):
            pass
        else:
            logging.error("Validator {} registration failed.".format(self.validator_dict))

        if self._driver_on_route:
            self.goto_payment_mode()
        '''
        else:
            pass
            # self.goto_registration_mode()
        '''

    '''
    params: type, validator_id, message_id, driver_id
    Driver registration
    '''
    def on_validator_status_cb(self, payloadOBJ):
        logging.debug("on_validator_status_cb")
        # logging.debug(str(payloadOBJ))
        try:
            sql = "UPDATE `equipment` SET `cnt`=0 WHERE `mac`='{}'".format(payloadOBJ["validator_id"])
            self.db_exec(sql)
        except KeyError as e:
            logging.error("Key error: {}".format(str(e)))

    def on_ikts_status_cb(self, payloadOBJ):
        logging.debug("on_ikts_status_cb")
        logging.debug(str(payloadOBJ))
        self._ikts_mac = payloadOBJ.get("mac", None)
        if self._ikts_mac is not None:
            sql = "UPDATE `equipment` SET `cnt`=0 WHERE `mac`='{}'".format(self._ikts_mac)
            self.db_exec(sql)

    def conductorCB(self, payloadOBJ):
        logging.debug("Call for conductorCB")

    def controllerCB(self, payloadOBJ):
        logging.debug("Call for controllerCB")

    def check_driver_registration(self):
        logging.debug("check_driver_registration")

        # reset values
        self._driver_exist = self._driver_on_route = self._driver_on_vehicle = False

        if self.driver_registration() is True:
            self.goto_payment_mode()
            self._driver_on_route = True

        return True

        '''
        driver = self.get_driver_saved_info()
        if driver is False:
            self.goto_registration_mode()
            return False

        self._driver_exist = True
        response = self.driver_registration_by_code(self.driver_card_number)

        if response is False:
            self.goto_registration_mode()
            return False
        else:
            self.goto_payment_mode()
            self._driver_on_route = True
        '''


        '''
        route = self.get_route_saved_info()
        if route is False:
            return False

        vehicle = self.get_vehicle_saved_info()
        if vehicle is False:
            return False

        session = self.get_session_saved_info()
        if session is False:
            return False
        if self._driver_on_route:
            # GET ROUTE AND SCHEDULE
            # TODO Check, if it needed to receive route info again?
            self.get_route_info(self.driver_id)
            self.get_messages()
            # go to payment mode
            self.goto_payment_mode()

        else:
            self.goto_registration_mode()
        '''

    def get_session_saved_info(self):
        try:
            with open(self.SESSION_JSON, 'r') as infile:
                session = json.load(infile)
                infile.close()
        except Exception as e:
            logging.error(str(e))
            return False
        try:
            self.token = session['token']
            return False if self.token is None else True
        except KeyError as e:
            logging.error(str(e))
            return False

    def get_driver_saved_info(self):
        logging.debug("get_driver_saved_info")

        try:
            with open(self.DRIVER_JSON, 'r') as infile:
                driver = json.load(infile)
                infile.close()

            self.print_dict("driver saved", driver)
        except Exception as e:
            logging.error(str(e))
            return False

        try:
            self.driver_id = driver['id']
            self.driver_name = driver['name']
            self.driver_card_number = driver['card_number']
        except KeyError as e:
            logging.error("Key error: {}".format(str(e)))
            return False

        return True
    '''
    def get_route_saved_info(self):
        logging.debug("get_route_saved_info")
        try:
            with open(self.ROUTE_JSON, 'r') as infile:
                route = json.load(infile)
                infile.close()
                self.send_route_info(route)
        except Exception as e:
            logging.error(str(e))
            return False

        for key in route:
            logging.debug("Route '{}': '{}'".format(str(key), str(route[key])))

        if self.check_info(route, ('id', 'name',)) is False:
            return False

        self.route_id = route['id']
        self.route_name = route['name']

        self.route_rate = route.get('rate', 0)
        self.route_guid = route.get('guid', None)

        return True
    def get_vehicle_saved_info(self):
        logging.debug("get_vehicle_saved_info")
        try:
            with open(self.VEHICLE_JSON, 'r') as infile:
                vehicle = json.load(infile)
                infile.close()
        except Exception as e:
            logging.error(str(e))
            return False

        for key in vehicle:
            logging.debug("Vehicle '{}': '{}'".format(str(key), str(vehicle[key])))

        if self.check_info(vehicle, ('id',)) is False:
            return False

        self.vehicle_id = vehicle['id']
        logging.debug("Vehicle ID: " + str(self.vehicle_id))
        return True
    @staticmethod
    def check_info( info, keys):
        logging.debug("check_info")
        for key in keys:
            if key not in info:
                logging.error("check_info: False. Not found Key: '{}'".format(key))
                return False
        logging.debug("check_info: True")
        return True
    '''



    def goto_refund_mode(self):
        logging.info("go_to_refound_mode")
        self.current_mode="REFUND"
        payload = dict(
            type=40,
            timestamp=int(datetime.datetime.now().timestamp()),
            ukr="",
            eng="",
            price=self.route_rate,
            route=self.route_guid,
        )
        self.to_validator(payload)

    def goto_payment_mode(self):
        logging.info("goto_payment_mode")
        self.current_mode="PAYMENT"
        payload = dict(
            type=41,
            timestamp=int(datetime.datetime.now().timestamp()),
            ukr="",
            eng="",
            price=self.route_rate,
            route=self.route_guid,
        )
        self.to_validator(payload)
        self.to_driver(payload)

        self._driver_on_route = True

        self.set_driver_status_bar()
        # self.send_route_info()

    def goto_registration_mode(self):
        logging.info("goto_registration_mode")
        self.current_mode="REGISTRATION"
        payload = dict(
            type=42,
            timestamp=int(datetime.datetime.now().timestamp()),
            ukr="реєстрація водія",
            eng="driver registration",
        )
        self.to_validator(payload)
        self.to_driver(payload)
        self._driver_on_route = False

    def goto_waiting_mode(self):
        logging.info("goto_waiting_mode")
        self.current_mode="WAITING"
        payload = dict(
            type=43,
            timestamp=int(datetime.datetime.now().timestamp()),
            ukr="",
            eng="",
            route=self.route_guid,
        )
        self.to_validator(payload)

    def goto_check_mode(self):
        logging.info("goto_check_mode")
        self.current_mode="CHECK"
        payload = dict(
            type=44,
            timestamp=int(datetime.datetime.now().timestamp()),
            ukr="",
            eng="",
            route=self.route_guid,
        )
        self.to_validator(payload)

    def goto_current_mode(self):
        logging.info("goto_current_mode")
        if self.current_mode == "PAYMENT":
            self.goto_payment_mode()
        elif self.current_mode == "CHECK":
            self.goto_check_mode()
        elif self.current_mode == "REFUND":
            self.goto_refund_mode()
        elif self.current_mode == "WAITING":
            self.goto_waiting_mode()
        else:
            self.goto_registration_mode()

    def to_atl_thread(self, method, url, payload=None, callback=None, reqdict=None):
        logging.debug("to_atl_thread")

        thread = threading.Thread(target=callback, args=(method, url, payload, reqdict))
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution
        logging.info("thread.start")

    def to_atelecom(self, method, url, payload=None, req_dict=None):
        logging.debug("to_atelecom method:'{}',url:'{}',payload:'{}'.".format(str(method),str(url),str(payload)))
        '''
        if self._internet_status is False:
            logging.error("self._internet_status is False")
            return False
        '''
        url = "http://st.atelecom.biz/" + url
        headers = self.get_auth_header()
        msg = "header='{}', url='{}', payload='{}'".format(str(headers), url, str(payload))

        r = False
        try:
            if method == "POST":
                r = requests.post(url, json=payload, headers=headers)
            elif method == "GET":
                r = requests.get(url, json=payload, headers=headers)
            elif method == "PUT":
                r = requests.put(url, json=payload, headers=headers)
            elif method == "DELETE":
                r = requests.delete(url, json=payload, headers=headers)
            else:
                logging.error("Unknown method: {}".format(str(method)))

            logging.debug(msg)
            logging.debug("Return code: '{}'".format(str(r)))
            return r
        except Exception as e:
            logging.error("Connection ERROR:" + str(e))
            self.goto_payment_mode()
            return False

    def driver_logout(self):
        logging.info("driver_logout")
        self._driver_on_route = False
        self.driver_card_number = None

        logging.info("Remove '{}'".format(self.BKTS_DUMP))
        try:
            os.remove(self.BKTS_DUMP)
        except Exception as e:
            logging.info(str(e))

        self.clear_equipment_table()
        self.clear_local_leglist()
        self.clear_remote_leglist()

        self.goto_registration_mode()

    def driver_registration_by_code(self, code):
        logging.debug("driver_registration_by_code. Code: '{}'".format(str(code)))
        # reset values
        self._driver_exist = self._driver_on_route = self._driver_on_vehicle = False

        # Send request
        r = self.to_atelecom("POST", 'mob/v1/auth', {"code": code})
        # print(r)
        if not r:
            logging.error("Driver registration failed.")
            return self.get_response('deny')

        elif r.status_code == 404:
            logging.error("Driver registration denied.")
            return self.get_response('deny')

        elif r.status_code == 200:
            try:
                response = r.json()
            except:
                logging.error("JSON decode error: {}".format(r.text))
                sys.exit()

            try:
                driver = response['model']
                route = response['route']
                vehicle = response['vehicle']
                self.token = response['token']
            except KeyError as e:
                logging.error("Key error: {}".format(str(e)))
                return self.get_response('deny')
            # write down received information
            try:
                logging.debug("OPEN: " + self.DRIVER_JSON)
                with open(self.DRIVER_JSON, 'w') as outfile:
                    json.dump(driver, outfile)
                outfile.close()

            except Exception as e:
                logging.error(str(e))
                return False

            self.print_dict('route', route)
            self.print_dict('driver', driver)
            self.print_dict('vehicle', vehicle)

            if self.set_registration_vars(driver, route, vehicle) is False:
                return self.get_response('deny')

            self.get_route_info(self.driver_id)

            logging.info("Current token: '{}'".format(str(self.token)))
            return self.get_response("success")

    def driver_registration(self, reqDict = None):
        '''
        curl -i -X POST -d '{"code":"43E9DBA494E80"}' http://st.atelecom.biz/mob/v1/auth
        :param code:
        :param reqDict:
        :return:
        '''
        logging.info("driver_registration")

        # reset values
        self._driver_exist = self._driver_on_route = self._driver_on_vehicle = False
        
        code = False

        if reqDict is None:
            # Retrieve information from dump
            try:
                with open(self.BKTS_DUMP, 'r') as infile:
                    auth_info = json.load(infile)
                    infile.close()
            except Exception as e:
                logging.info("There are no previous auth information, so we will waite for driver card registration")
                return False
            try:
                code = auth_info['model']['card_number']
                logging.info("Driver card is '{}'".format(code))
            except KeyError as e:
                logging.error("No driver card number in saved auth info")
                return False
        else:
            # This is card registration! Lets try card number
            try:
                code = reqDict['qr']
            except KeyError as e:
                logging.error("Key {} required.".format(str(e)))
                raise MyError(self.get_response('conflict'))

        # Send request
        r = self.to_atelecom("POST", 'mob/v1/auth', {"code": code})
        if (not r) or (r.status_code == 404):
            logging.error("Driver registration failed.")
            if r:
                logging.error(str(r.text))
            if reqDict is None:
                return False
            else:
                raise MyError(self.get_response('deny'))

        elif r.status_code == 200:
            try:
                auth_info = r.json()
            except ValueError as e:
                logging.error("JSON decode error {}".format(str(e)))
                if reqDict is None:
                    return False
                else:
                    raise MyError(self.get_response('deny'))

            if self.set_registration_vars_new(auth_info) is False:
                logging.error("Driver registration error")
                if reqDict is None:
                    return False
                else:
                    raise MyError(self.get_response('deny'))

            logging.info("Current token: '{}'".format(str(self.token)))

            if reqDict is not None:
                reqDict['success'] = 0
                self.to_validator(reqDict)

            # write auth information
            try:
                with open(self.BKTS_DUMP, 'w') as outfile:
                    json.dump( auth_info, outfile)
                outfile.close()
            except Exception as e:
                logging.error(str(e))
                raise MyError(self.get_response('conflict'))

            self.goto_payment_mode()
            self._driver_on_route = True

            # GET ROUTE AND SCHEDULE
            self.get_route_info(self.driver_id)

            self.get_equipment_list()

            self.send_route_info(auth_info['route'])

            # self.validator_registration()

            logging.debug("Vehicle ID: " + str(self.vehicle_id))

    def print_dict(self, name, _dict):
        for key in _dict:
            logging.debug("{} '{}': '{}'".format(name, str(key), str(_dict[key])))

    def set_registration_vars_new(self, response):
        try:
            self.token = response['token']
            driver = response['model']
            staff_type = driver['type']
            vehicle = response['vehicle']
            route = response['route']

            self.driver_id = driver['id']
            self.driver_name = driver['name']
            self.driver_card_number = driver['card_number']

            self.route_id = route["id"]
            self.route_name = route['name']
            self.route_guid = route['guid']
            self.route_rate = route['rate']
            self.route_desc = route['description']
            self.route_interval = route['interval']
            self.route_working_hours = route['working_hours']
            self.route_updated_at = route['updated_at']

            self.vehicle_id = vehicle["id"]

        except KeyError as e:
            logging.error("Key error: {}".format(str(e)))
            return False

        # check staff_type: 1 - driver, 2 - conductor, 3 controller
        if staff_type != 1:
            self.driver_logout()
            logging.error( "Staff is not a driver: {}".format(str(driver)))
            return False

        self.send_route_info(route)

        self.print_dict('driver', driver)
        self.print_dict("route", route)
        self.print_dict("vehicle", vehicle)

        # write down received information
        try:
            logging.debug("WRITE: " + self.BKTS_DUMP)
            with open(self.BKTS_DUMP, 'w') as outfile:
                json.dump(response, outfile)
            outfile.close()

        except Exception as e:
            logging.error(str(e))
            return False

        return True

    def set_registration_vars(self, driver, route, vehicle):
        try:
            self.driver_id = driver['id']
            self.driver_name = driver['name']
            self.driver_card_number = driver['card_number']

            self.route_id = route["id"]
            self.route_name = route['name']
            self.route_guid = route['guid']
            self.route_rate = route['rate']
            self.route_desc = route['description']
            self.route_interval = route['interval']
            self.route_working_hours = route['working_hours']
            self.route_updated_at = route['updated_at']

            self.vehicle_id = vehicle["id"]

            return True

        except KeyError as e:
            logging.error("set_registration_vars, KeyError: {}".format(str(e)))
            return False

    def get_trusted(self):
        if self._trusted_updeted:
            return True
        logging.info("get_trusted")

        if not self.route_rate:
            logging.error("Rate is : {}".format(str(self.route_rate)))
            return False

        r = self.to_atelecom("GET", 'mob/v1/trusted', None)
        if not r:
            return False
        elif r.status_code == 200:
            trusted_list = r.json()

            sql = "DELETE FROM trusted"
            self.db_exec(sql)
            '''
            sql = "INSERT OR IGNORE INTO trusted (`code`,`quantity`,`amount`) VALUES (:code, :quantity, :amount)"
            logging.info("Trusted list: {}".format(str(trusted_list)))
            self.db_executemany(sql, trusted_list)
            '''

            sql = "INSERT OR IGNORE INTO trusted (`code`,`quantity`,`amount`) VALUES (:code, :quantity, :amount)"
            for trusted in trusted_list:
                trusted['quantity'] = trusted['quantity'] + int(trusted['amount'] / self.route_rate)
                logging.info("Trusted: {}".format(str(trusted)))
                self.db_execute(sql, trusted)

            self.db().commit()
            self._trusted_updeted = True

    def get_multypass(self):
        if self._multipass_updeted:
            return True
        logging.info("get_multypass")

        r = self.to_atelecom("GET", 'mob/v1/multipass', None)
        if not r:
            return False
        elif r.status_code == 200:
            multipass_list = r.json()

            sql = "DELETE FROM multipass"
            self.db_exec(sql)

            sql = "INSERT OR IGNORE INTO multipass (`code`) VALUES (:code)"
            logging.info("Multipass list: {}".format(str(multipass_list)))
            self.db_executemany(sql, multipass_list)

            self.db().commit()
            self._multipass_updeted = True
        else:
            logging.error(str(r))

    def get_equipment_list(self):
        '''
        BKTS:1, Validator: 2, IKTS: 4, MODEM: 11, GPS: 12

        [{'serial_number': '225.43', 'mac_address': 'EEF993E1BFDE', 'type': '1'},
        {'serial_number': '199.17', 'mac_address': '009977665512', 'type': '2'},
        {'serial_number': '104.156', 'mac_address': '8CDC97E570C2', 'type': '2'},
        {'serial_number': '897', 'mac_address': '769F14D78B4A', 'type': '4'},
        {'serial_number': '90-90', 'mac_address': '119977665512', 'type': '2'},
        {'type': '3'}]
        '''

        logging.debug("get_equipment_list")
        if self.vehicle_id is None:
            return False
        url = 'mob/v1/front/equipments/index?vehicle={}'.format(self.vehicle_id)
        r = self.to_atelecom("GET",url,None)
        if not r:
            logging.error("Equipment list empty")
            return False
        if r.status_code == 200:
            '''
            [{'serial_number': '225.43', 'type': '1', 'mac_address': 'EEF993E1BFDE'}, 
             {'serial_number': '104.156', 'type': '2', 'mac_address': '009977665513'}, 
             {'serial_number': '879654321', 'type': '2', 'mac_address': '009977665512'}, 
             {'serial_number': '342398', 'type': '2', 'mac_address': '009977665511'}]
            '''
            self._equipment_list = r.json()
            logging.info("EQUIPMENT {}".format(str(self._equipment_list)))
            insert="INSERT OR IGNORE INTO `equipment` (`mac`,`serial_number`,`type`) VALUES (:mac, :serial, :type)"
            for box in self._equipment_list:
                try:
                    self.db_execute(insert,{"mac":box["mac_address"],"serial":box["serial_number"],"type":box["type"]})
                except KeyError as e:
                    logging.error("Error while walking equipment.Key: {} in: {}".format(str(e),str(box)))
            self.db().commit()
        else:
            logging.error("While receiving equipment list. Rsponce: {}".format(str(r)))
            return False

        # self.send_equipment_status()
        self.do_send_equipment_status = True
        return True

    def send_equipment_status(self):
        '''
        0:Modem
        1:GPS
        2:LSpeaker
        3:Display
        4:RSpeaker
        5:IKTS
        6:Mobile terminal
        7:BKTS
        8:Validator1
        9:Validator2
        10:Validator3

        BKTS:1, Validator: 2, IKTS: 4, MODEM: 11, GPS: 12
        '''

        if self.do_send_equipment_status is False:
            return False

        self.do_send_equipment_status = False

        logging.debug("send_equipment_list")
        c = self.db().cursor()
        equipment = []
        # check for internet connection
        if self._internet_status is True:
            equipment.append( {"type": 0,"state": 1,"mac":self._mac} )
        else:
            equipment.append({"type": 0, "state": 0, "mac": self._mac})

        if self._gps_status is True:
            equipment.append( {"type": 1,"state": 1,"mac":self._mac} )
        else:
            equipment.append({"type": 1, "state": 0, "mac": self._mac})

        # select for IKTS
        sql = "SELECT 5,`last_status`,`mac` FROM `equipment` where type = 4"
        result = c.execute(sql)
        for row in result:
            (i, last_status, mac) = row
            equipment.append(dict(
                type=i,
                state=last_status,
                mac=mac,
            ))
        # select for BKTS
        sql = "SELECT 10,`last_status`,`mac` FROM `equipment` where type = 1"
        result = c.execute(sql)
        for row in result:
            (i, last_status, mac) = row
            equipment.append(dict(
                type=i,
                state=1,
                mac=mac,
            ))
        # select for validators
        sql = "SELECT 7,`last_status`,`mac` FROM `equipment` where type = 2 LIMIT 3"
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
        # sending to driver terminal
        payload = dict(
            type=340,
            device=equipment
        )
        self.to_driver(payload)
    '''
      {'mac': 'B827EB8C06A0', 
       'device': [
            {'state': 1, 'mac': 'B827EB8C06A0', 'type': 0}, 
            {'mac': 'EEF993E1BFDE', 'state': 1, 'type': 10}, 
            {'mac': '009977665513', 'state': 1, 'type': 7}, 
            {'mac': '009977665512', 'state': 0, 'type': 8}, 
            {'mac': '009977665511', 'state': 0, 'type': 9}], 
        'type': 340, 'timestamp': 1518891487}
      '''

    def set_driver_status_bar(self):
        logging.debug("set_driver_status_bar")
        self._message_id += 1
        payload = dict(
            type=50,
            timestamp=datetime.datetime.timestamp,
            message_id=self._message_id,
            route_guid = self.route_guid,
            driver_name = self.driver_name,
            route_name=self.get_vehicle_type_short(self.route_guid) + str(self.route_name),
            delta=self._last_deviation
        )
        self.to_driver(payload)

    def log_equipment_status(self, status, mac):
        payload = dict(
            device_mac_address=mac,
            device_serial_number=mac,
            code=status,
            staff_id=self.driver_id,
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
        self.to_atelecom("POST", "mob/v1/front/alarms/status", payload)

    def get_equipment_status(self):
        '''
        cnt default = -1,
        status default = -1,
        status: "NA": -2, "present but unknown": -1, "not in order": 0, "OK": 1;

        :return:
        '''
        logging.debug("get_equipment_status")

        timestamp = int(datetime.datetime.now().timestamp())

        update = "UPDATE `equipment` SET `last_status`= :last_status WHERE `mac` = :mac"
        update_equipment_status = False
        sql = "SELECT `mac`,`type`,`last_status`,`cnt` FROM `equipment`"
        for row in self.db_exec(sql):
            # logging.debug(row)
            (mac, _type, last_status, cnt) = row
            if cnt == 0:
                if last_status != 1:
                    logging.debug("Send status update")
                    logging.debug("MAC {} ONLINE".format(mac))
                    self.db_execute(update, {"last_status": 1, "mac": mac})
                    self.log_equipment_status(200, mac)
                    self.do_send_equipment_status = True
            elif cnt > 0:
                if last_status != 0:
                    logging.debug("Send status update")
                    logging.debug("MAC {} OFFLINE".format(mac))
                    self.db_execute(update, {"last_status": 0, "mac": mac})
                    self.log_equipment_status(500, mac)
                    self.do_send_equipment_status = True
            # increment counters
            sql = "UPDATE `equipment` SET `cnt`= `cnt` + 1 WHERE `cnt` BETWEEN 0 AND 1"

            if _type is 4: # 4 - IKTS
                payload = {
                    "type": 202,
                    "timestamp": timestamp,
                    "mac": mac,
                }
                self.to_ikts(payload)
        payload = {
            "type": 1,
            "timestamp": timestamp,
        }
        self.to_validator(payload)

        self.db_exec(sql)

        return True

    def bkts_registration(self):
        logging.info("bkts_registration")

        payload = dict(
            device_mac_address=self._mac,
            device_serial_number=self._mac,
            code=200,
            staff_id=self.driver_id,
            vehicle_id=self.vehicle_id,
            route_id=self.route_id,
            # sw_version=self.validator_dict[self._mac].get('sw_version', None),
            # hw_version=self.validator_dict[self._mac].get('hw_version', None),
            status=200,
            mac=self._mac,
            location=dict(
                lat=self.latitude,
                lng=self.longitude,
                timestamp=int(datetime.datetime.now().timestamp())
            )
        )
        # Send request
        self.to_atelecom("POST", "mob/v1/front/alarms/status", payload)

    def validator_registration(self):
        logging.debug("validator_registration: '{}'".format(str(self.validator_dict)))

        for validator in self.validator_dict:
            logging.debug("VALIDATOR: {} registration".format(validator))
            # mac = validator.get('mac', None)
            mac = validator
            payload = dict(
                device_mac_address=mac,
                device_serial_number=mac,
                code=200,
                staff_id=self.driver_id,
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
            self.to_atelecom("POST", "mob/v1/front/alarms/status", payload)
            # TODO: verify next string with _driver_on_route
            self._driver_on_route = True
            return True
    def clear_equipment_table(self):
        logging.debug("clear_equipment_table")

        sql = "DELETE FROM `equipment`"
        self.db_exec(sql)
        self.db().commit()


    def clear_local_leglist(self):
        logging.debug("clear_local_leglist")

        sql = "DELETE FROM `leglist`"
        # self.db_exec(sql)
        # sself.db().commit()

    def check_local_leglist(self, code):
        logging.debug("check_local_leglist")

        sql = "SELECT COUNT(`id`) FROM `leglist` WHERE code = ?"
        row = self.db_execute(sql,[code]).fetchone()

        return row[0]

    def write_to_local_leglist(self, code):
        logging.debug("write_to_local_leglist")
        sql = "INSERT OR IGNORE INTO `leglist` (`code`, `created_at`) VALUES (?,?)"
        self.db_execute(sql, (code,int(datetime.datetime.now().timestamp()) ))
        self.db().commit()

    def clear_remote_leglist(self):
        logging.debug("clear_remote_leglist")
        if self.vehicle_id:
            url = "mob/v1/leglist/{}".format(self.vehicle_id)
            r = self.to_atelecom('DELETE', url, None)
            if r.status_code == 200:
                try:
                    result = r.json()
                    logging.debug("Deleted '{}' entries.".format(result['count']))
                    logging.info(str(result))
                except KeyError as e:
                    logging.error("Key error for {}".format(str(e)))
                except Exception as e:
                    logging.error(str(e))
            else:
                logging.error("Error while clearing remote leglist.")

    def do_repayment(self, method, url, payload, reqDict, to_validator=True):
        code = reqDict.get('qr')
        logging.info("do_repayment for '{}'".format(code))
        try:
            start_time = time.time()
            r = self.to_atelecom(method, url, payload)
            self.last_duration = int((time.time() - start_time) * 100)

            logging.debug("Last duration: {} ms".format(self.last_duration))

            if r is False:
                logging.error("Error while connecting to serverError while connecting to server")
                raise MyError(self.get_response('inaccessible'))
            elif r.status_code == 409:
                logging.error("do_repayment: {}".format(r.text))
                try:
                    r.raise_for_status()
                except Exception as e:
                    logging.error(str(e))
                raise MyError(self.get_response('conflict'))
            elif r.status_code == 400:
                logging.error("do_repayment: PortaBilling Error {}".format(r.text))
                try:
                    r.raise_for_status()
                except Exception as e:
                    logging.error(str(e))
                raise MyError(self.get_response('conflict'))
            elif r.status_code == 201:
                raise MyError(self.get_response('success'))
            elif r.status_code == 200:  # composted
                raise MyError(self.get_response('composted'))
            elif r.status_code == 404:  # not founf
                logging.error("NOT FOUND")
                raise MyError(self.get_response('codeError'))
        except MyError as e:
            reqDict['error'] = e.message
            reqDict['success'] = e.code
            if to_validator:
                self.to_validator(reqDict)
                self.send_xdr( code, 0)
            else:
                logging.debug("Do not send to validator")

    def write_to_remote_leglist(self, method, url, payload, reqDict, to_validator = True):
        logging.debug("write_to_remote_leglist")
        try:
            r = self.to_atelecom(method, url, payload)
            logging.debug("write_to_leglist recieve response : " + str(r))

            if r is False:
                # Error while connecting to server
                raise MyError(self.get_response('inaccessible'))

            elif r.status_code == 201:
                # Send Success
                raise MyError(self.get_response('success'))

            elif r.status_code == 200:  # composted
                raise MyError(self.get_response('composted'))

            elif r.status_code == 404:
                logging.warning("NOT FOUND")
                raise MyError(self.get_response('not_found'))

            else:
                msg = "Response code: {}, text: '{}'".format(r.status_code, str(r.text))
                logging.error(msg)
                raise MyError(self.get_response('not_found'))


        except MyError as e:
            reqDict['error'] = e.message
            reqDict['success'] = e.code
            if to_validator:
                self.to_validator(reqDict)

    def code_repayment(self, code, reqDict):
        logging.info("code_repayment for {}".format(code))

        if not self._driver_on_route:
            return False

        elif self.driver_card_number and self.driver_card_number == code:
            logging.info("Driver card received")

            reqDict['success'] = 0
            self.to_validator(reqDict)

            self.goto_registration_mode()

            self.driver_logout()

            return False  # False is preventing for xdr recording

        if self.route_guid is None or self.vehicle_id is None:
            # Nothing to do.
            # TODO Send success to Failure
            self._driver_on_route = False
            self.goto_registration_mode()
            return False  # False is preventing for xdr recording

        payload = dict(
            route=self.route_guid,
            vehicle_id=self.vehicle_id,
            mac=self._mac,
        )

        # check in multipass
        sql = "SELECT `code` FROM `multipass` WHERE `code` = :code"
        row = self.db_execute(sql, {'code': code}).fetchone()

        if row:
            # The code present in multipass database
            logging.info("Code '{}' present in multipass".format(code))
            # check in local leglist
            if self.check_local_leglist(code) > 0:
                # already composted
                logging.info("Code '{}' already composted".format(code))
                raise MyError(self.get_response('composted'))
            else:
                # add to local leglist
                self.write_to_local_leglist(code)

            if self._internet_status is True:
                # Send code to server race_list
                url = self.LEGLIST_URL.format(code)
                reqDict["t_type"] = 1
                payload['t_type'] = 1
                self.to_atl_thread( "PUT", url, payload, self.write_to_remote_leglist, reqDict)
            else:
                # Writing to deferred trunsaction
                self.write_to_deferred(code, 1)
                # Send Success
                raise MyError(self.get_response('success'))
        else:
            # The Code is not in `multipass` database
            if self._internet_status is True:
                # do radius request
                logging.info("Send '{}' to Radius".format(code))
                url = self.REPAYMENT_URL.format(code)
                reqDict["t_type"] = 0
                payload['t_type'] = 0
                self.to_atl_thread( "PUT", url, payload, self.do_repayment, reqDict)
            else:
                # Check in `trusted` database
                sql = "SELECT `code` FROM `trusted` WHERE `code` = :code "
                row = self.db_execute(sql, {"code": code}).fetchone()
                if row:
                    # The Code is trusted
                    logging.info("Code '{}' present in trusted".format(code))

                    self.write_to_local_leglist(code)
                    # Writing to deferred trunsaction
                    self.write_to_deferred(code,0)
                    # Send Success
                    raise MyError(self.get_response('success'))
                    pass
                else:
                    raise MyError(self.get_response('deny'))
        return False

    def trusted_write_off(self, code):
        if not code:
            return False

        sql = "UPDATE `trusted` SET `quantity` = `quantity`-1 WHERE `code` = :code AND `quantity` > 0"
        self.db_execute(sql, {'code': code})

    def write_to_deferred(self, code, t_type):
        '''
        In case of impossibility of sending transaction, write it in table `deferred`
        :param code:
        :return:
        '''
        logging.debug("write_to_deferred code:{} type:{}".format(str(code), str(t_type)))

        timestamp = int(datetime.datetime.now().timestamp())
        sql = "INSERT  INTO `deferred` (`code`,`timestamp`,`mac`,`vehicle_id`,`route_guid`,`type`) " \
              "VALUES (:code, :timestamp, :mac, :vehicle_id, :route_guid, :t_type)"

        params = {"code": code, "timestamp": timestamp, "mac": self._mac, "vehicle_id": self.vehicle_id,
                  "route_guid": self.route_guid, 't_type': t_type}
        self.db_execute(sql, params)
        self.db().commit()

        return True

    def send_deferred(self):
        '''
        Try send deferred transaction to Billing system
        :return:
        '''
        try:
            logging.debug("send_deferred")
            ids = []
            sql = "SELECT `id`,`code`,`timestamp`,`mac`,`vehicle_id`,`route_guid`,`type` " \
                  "FROM `deferred` ORDER BY `timestamp`"
            cursor = self.db_exec(sql)
            rows = cursor.fetchall()
            for row in rows:
                payload = {
                    'route':row[5],
                    'vehicle_id':row[4],
                    'mac':row[3],
                    't_type':row[6],
                }
                logging.debug(str(payload))

                r = True
                try:

                    if row[6] == 0:
                        url = self.REPAYMENT_URL.format(str(row[1]))
                        self.do_repayment('PUT', url, payload, payload, False)
                    else:
                        url = self.LEGLIST_URL.format(str(row[1]))
                        self.write_to_remote_leglist('PUT', url, payload, payload, False)

                except MyError as e:
                    r = True if e.code == 200 or e.code == 201 else False

                if r is not False:
                    ids.append(row[0])
                    self.send_xdr(row[1], 1)

            sql = "DELETE FROM `deferred` WHERE id = :id"
            for id in ids:
                self.db_execute(sql, {"id":id})

        except Exception as e:
            logging.error("send_deferred exception: '{}'".format(str(e)))

    def send_xdr(self, code, transaction_type):
        '''
        :param code:
        :param transaction_type: 0 - standart, 1- deferred, 9 - random
        :return:
        '''
        logging.info("send_xdr: code={} type={}".format(code, transaction_type))

        if self._internet_status is False:
            return False

        self.transaction_cnt += 1
        payload = dict(
            tid=1,
            type=transaction_type,
            rate=self.route_rate,
            vehicle_id=self.vehicle_id,
            route_id=self.route_id,
            hex=code,
            time=int(datetime.datetime.now().timestamp()),
            duration=self.last_duration,
            bt_id=transaction_type,
            lat=self.latitude,
            lng=self.longitude,
        )
        self.to_atelecom("POST", "mob/v1/front/portaone/payment", payload)


    '''
    Code validation function
    mosquitto_pub -d -h localhost -t t_bkts  -f qrVAlidation.json
    '''
    def code_validation(self, reqDict):
        logging.info("Call for code_validation")
        try:
            # Required arguments: check fo integrity
            try:
                type = reqDict['type']
                validator_id = reqDict['validator_id']
                message_id = reqDict['message_id']
                code = reqDict['qr']
                timestamp = reqDict['timestamp']
            except KeyError as e:
                logging.error("Key {} required.".format(str(e)))
                raise MyError(self.get_response('conflict'))

            logging.debug("Code: '{}',  length: {}".format(code, str(len(code))))

            if self._driver_on_route is False:
                self.driver_registration(reqDict)
                reqDict['price'] = self.route_rate
                reqDict['ukr'] = self.get_vehicle_type_ukr(self.route_guid) + str(self.route_name)
                reqDict['eng'] = self.get_vehicle_type_eng(self.route_guid) + str(self.route_name)
                reqDict['route'] = self.route_guid
                reqDict['equipment'] = self._equipment_list

                routeDict = dict(
                    type=201,
                    message_id=self._message_id,
                    route_info=dict(
                        name=self.get_vehicle_type_ukr(self.route_guid) + str(self.route_name),
                        short=self.get_vehicle_type_short(self.route_guid) + str(self.route_name),
                    ),
                    equipments=self._equipment_list,
                )
                logging.debug(str(routeDict))
                self.to_ikts(routeDict)
                self.to_driver(routeDict)

                self.goto_payment_mode()
                self.bkts_registration()
            else:
                self.code_repayment(code, reqDict)

        except MyError as e:
            logging.error(str(e))
            reqDict['error'] = e.message
            reqDict['success'] = e.code
            self.to_validator(reqDict)
            if e.code == 0:
                self.send_xdr(code, 0)
        except Exception as e:
            reqDict['error'] = e
            reqDict['success'] = -1
            self.to_validator(reqDict)
        self._message_id += 1
        return

    def randomValidationCB(self, reqDict):
        logging.debug("Call for randomValidationCB")
        try:
            code = reqDict.pop('qr')
            if self._driver_on_route is not False:
                if self.code_repayment(code, reqDict):
                    self.send_xdr(code, 9)
        except MyError as e:
            logging.error(str(e))
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
        logging.debug("alarmCB")
        payload = dict(
            device_mac_address = self._mac,
            code = 201,
            staff_id = self.driver_id,
            vehicle_id = self.vehicle_id,
            route_id = self.route_id,
            location = dict(
                lat = self.latitude,
                lng = self.longitude,
                timestamp = datetime.datetime.now().timestamp()
            )
        )
        #curl -i -X POST -H "AUTHORIZATION: Bearer F9898736657462791FDCAE1143F404DF" -d '{"route_id": 23, "location": {"lng": 0.0, "timestamp": 1504245387, "lat": 0.0}, "staff_id": 122, "vehicle_id": 59, "device_mac_address": "b827eb3001c2"}' http://st.atelecom.biz/mob/v1/front/alarms/danger
        '''
        url = 'http://st.atelecom.biz/mob/v1/front/alarms/danger'
        r = requests.post(url, headers=self.get_auth_header(), json=payload)
        '''
        self.to_atelecom("POST", "mob/v1/front/alarms/danger", payload)

    def call_operator_cb(self, reqDict):
        logging.debug("call_operator_cb")
        payload = dict(
            device_mac_address=self._mac,
            code=201,
            staff_id=self.driver_id,
            vehicle_id=self.vehicle_id,
            route_id=self.route_id,
            location = dict(
                lat = self.latitude,
                lng = self.longitude,
                timestamp = datetime.datetime.now().timestamp()
            )
        )
        #curl -i -X POST -H "AUTHORIZATION: Bearer F9898736657462791FDCAE1143F404DF" -d '{"route_id": 23, "location": {"lng": 0.0, "timestamp": 1504245387, "lat": 0.0}, "staff_id": 122, "vehicle_id": 59, "device_mac_address": "b827eb3001c2"}' http://st.atelecom.biz/mob/v1/front/alarms/danger

        self.to_atelecom("POST", "mob/v1/front/alarms/call-me", payload)

    def on_connect(self, client, payload, flag, rc):
        logging.info("connected OK" if rc == 0 else "Bad connnection = {}".format(rc))

    def on_informer(self, client, userdata, message):
        logging.debug("Message from Informer received")
        try:
            payload_dict = json.loads(message.payload.decode("utf-8"))

            _type = int(payload_dict.get('type', None))

            if _type == 0:  # 'Registration'
                self.ikts_registration_cb(payload_dict)
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
                logging.error("Unknown informator request 'type': '", payload_dict['_type'], "'")
                return False
            return True

        except ValueError as e:
            logging.error(str(message.payload))
            logging.error(str(message.payload.decode("utf-8")))
            logging.error("Error JSON format: " + str(e))
            return False
        except KeyError as e:
            logging.error(str(e))
            return False
        except Exception as e:
            logging.error(str(e))
            return False

    def on_message(self, client, userdata, message):
        try:
            payload_dict = json.loads(message.payload.decode("utf-8"))
            _type = int(payload_dict['type'])

            if _type == 0:  # 'Registration'
                self.on_validator_reg_cb(payload_dict)
            elif _type == 1:  # ):
                self.on_validator_status_cb(payload_dict)
            elif _type == 10 or _type == 11:
                self.code_validation(payload_dict)
            elif _type == 12:
                self.randomValidationCB(payload_dict)
            elif _type == 110:
                self.on_gps_coordinates(payload_dict)
            elif _type == 200:
                self.ikts_registration_cb(payload_dict)
            elif _type == 202:
                self.on_ikts_status_cb(payload_dict)
            elif _type == 230:
                self.on_message_viewed(payload_dict)
            elif _type == 250:
                self.on_event_recieved(payload_dict)
            elif _type == 400:
                self.send_debug(payload_dict)
            else:
                logging.error("Unknown request type: '{}'".format(_type))
                return False
            return True

        except ValueError as e:
            logging.error(message.payload.decode("utf-8"))
            logging.error("Error JSON format: " + str(e))
            return False
        except KeyError as e:
            logging.error("'on_message 'key error: {}".format(str(e)))
            return False

    def send_debug(self, payload):
        logging.debug("send_debug")

        deferred = []
        sql = "SELECT `code`, `type`, `timestamp` FROM `deferred` ORDER by `timestamp`"
        rows = self.db_exec(sql).fetchall()
        for row in rows:
            deferred.append({"code": row[0],"type": row[1],"timestamp": row[2],})

        trusted = []
        sql = "SELECT `code`, `quantity` FROM `trusted` ORDER by `code`"
        rows = self.db_exec(sql).fetchall()
        for row in rows:
            trusted.append({"code": row[0], "quantity": row[1], "rest": "N/A", "timestamp": payload["timestamp"]})

        multipass = []
        sql = "SELECT `code` FROM `multipass` ORDER by `code`"
        rows = self.db_exec(sql).fetchall()
        for row in rows:
            multipass.append({"code": row[0], "timestamp": payload["timestamp"]})


        payload["deferred"] = deferred
        payload["trusted"] = trusted
        payload["multipass"] = multipass

        self.to_driver(payload)

    def on_event_recieved(self, payload):
        logging.info("on_event_recieved {}".format(str(payload)))
        event_id = payload['event_id']
        logging.info("on_event_recieved type:{}".format(event_id))
        if event_id == 1:
            self.alarmCB(payload)
        elif event_id == 2:
            self.call_operator_cb(payload)
        elif event_id == 0:
            logging.info(self.route_guid)

            curr_click_time = time.time()

            if (curr_click_time - self._last_click_time) < 0.5:
                self.driver_logout()
                return True
            self._last_click_time = curr_click_time

            if not self.gps_emulator_run:
                gps_emulator.Emulator()
                self.gps_emulator_run = True

            self.clear_local_leglist()
            self.clear_remote_leglist()

    # Send message to Validator
    def to_validator(self, payload):
        logging.debug("to_validator")
        self._message_id += 1
        payload['timestamp'] = int((time.time())) + self._utc_offset
        logging.debug(str(payload))
        resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
        self.client.publish("t_validator", resultJSON)
        return True

    def to_ikts(self, payload):
        logging.debug("to_ikts")
        self._message_id += 1
        payload['timestamp'] = int((time.time())) + self._utc_offset
        # payload['mac'] = "5EBDABF60273"
        # payload['mac'] = "2289AB315E6E"
        payload['mac'] = self._ikts_mac

        logging.debug(str(payload))
        resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
        self.client.publish("t_informer", resultJSON)
        return

    def to_driver(self, payload):
        logging.debug("to_driver")
        self._message_id += 1
        payload['timestamp'] = int((time.time())) + self._utc_offset
        payload['mac'] = self._mac
        logging.debug(str(payload))
        resultJSON = json.dumps(payload, ensure_ascii=False).encode('utf8')
        self.client.publish("t_driver", resultJSON)
        return

    def local_exec(self):
        pass
        # logging.debug("local_exec")
        # self.check_validators()
        # self.check_ikts()
        # self.emmulate_gps()

        # self.check_internet()

        self.get_trusted()
        self.get_multypass()

        self.send_equipment_status()

        self._local_exec_cnt += 1

        if self._local_exec_cnt % 23 == 0:
            if self.token is not None:
                self.get_messages()
        if self._local_exec_cnt % 5 == 0:
            pass
            self.send_coordinates()

            if self.token is not None:
                pass
                self.get_equipment_status();

    def local_exec_in_thred(self):
        while True:
            # logging.debug("check_internet")

            update_equipment_status = False

            try:
                urllib.request.urlopen('http://st.atelecom.biz/ping/', timeout=1)
                # urllib.request.urlopen('http://beta.speedtest.net/', timeout=1)
                # urllib.request.urlopen('http://st.atelecom.biz/mob/v1/test', None, timeout=1)
                if self._internet_status is False:
                    self._internet_status = True
                    logging.warning("INTERNET CONNECTED")
                    self.on_internet_up()
                    self.do_send_equipment_status = True
                    # self.send_equipment_status()

            except Exception as e:
                if self._internet_status is True:
                    self._internet_status = False
                    logging.warning("INTERNET DISCONNECTED")
                    self.do_send_equipment_status = True
                    # self.send_equipment_status()


            if self._driver_on_route:
                try:
                    '''
                    self.get_trusted()
                    self.get_multypass()
                    '''
                except Exception as e:
                    logging.error(str(e))

            if self._gps_cnt > 3:
                if self._gps_status is not False:
                    self._gps_status = False
                    self.do_send_equipment_status = True
                    logging.warning("GPS DISCONNECTED")
            elif self._gps_status is not True:
                self._gps_status = True
                self.do_send_equipment_status = True
                logging.warning("GPS CONNECTED")
            self._gps_cnt += 1
            # logging.warning("_gps_cnt: {}".format(str(self._gps_cnt)))

            time.sleep(1)

    def on_internet_up(self):
        self.send_deferred()

    def send_coordinates(self):
        if self._internet_status is False:
            return False
        if self.vehicle_id is not None:
            payload = {
                "id": self.vehicle_id,
                "lat": self.latitude,
                "lng": self.longitude,
            }
            logging.debug("send_coordinates {}".format(str(payload)))
            try:
                r = requests.post(self.COORDINATE_URL, json=payload, verify=False)
                return r
            except Exception as e:
                logging.error(str(e))
                return False

    def run(self):
        self.db_init()

        broker = "localhost"
        self.client = mqtt.Client("BKTS")  # create new instance
        self.client.on_connect = self.on_connect  # attach function to callback
        self.client.on_message = self.on_message  # attach function to callback

        logging.debug("Connection to broker " + broker)
        try:
            self.client.connect(broker)

        except Exception as e:
            logging.critical("Can't connect: ", str(e))
            exit(1)
        else:
            self.client.loop_start()
            self.client.subscribe("t_bkts")

            self.check_driver_registration()

            i = 0
            loop_flag = 1
            while loop_flag == 1:
                time.sleep(1)
                # self.local_exec()
                if self.token is not None:
                    self.local_exec()

            self.client.loop_stop()
            self.client.disconnect()

# *****************************************************************************************
if __name__ == "__main__": main()
