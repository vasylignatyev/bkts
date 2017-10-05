#!/usr/bin/python3
import sqlite3
import datetime


def t_diff(ts1, ts2):
    t1 = datetime.datetime.strptime(ts1, '%H:%M:%S').time()
    t2 = datetime.datetime.strptime(ts2, '%H:%M:%S').time()
    td1 = datetime.timedelta(hours=t1.hour, minutes=t1.minute, seconds=t1.second)
    td2 = datetime.timedelta(hours=t2.hour, minutes=t2.minute, seconds=t2.second)
    delta = td1 - td2
    total_sec = delta.total_seconds()
    if total_sec < 0:
        total_sec = total_sec * (-1)
    return int(total_sec)

print("connect to database")
db = sqlite3.connect('bkts.db')
db.create_function("t_diff", 2, t_diff)

#t1 = datetime.time(9, 33, 25)
#t2 = datetime.time(9, 43, 35)
#print(t_diff("09:15:33", "08:16:45"))

# "WHERE s.round=1 AND s.`date`=5 AND p.`type`=1  AND s.`direction`=1 "

print("TEST 4")

#sql = "SELECT p.`name`,p.`id`,s.`id`,s.`time`, s.`time`,p.`now_audio_url`,p.`now_audio_dttm`,p.`now_video_url`,p.`now_video_dttm`, p.`future_audio_url`, p.`future_audio_dttm`, p.`future_video_url`, p.`future_video_dttm` FROM `schedule` s INNER JOIN `point` p  ON s.`station_id` = p.`id` AND s.`direction`= p.`direction` WHERE s.`time` >= '17:22:00' AND s.`date`=3 AND p.`type`=1  AND s.`direction`=1 AND s.`round` = 55 ORDER BY s.time LIMIT 3"
#sql = "SELECT p.`id`,s.`id`,p.`direction`,p.`name`,s.`time` FROM `schedule` s INNER JOIN `point` p  ON s.`station_id` = p.`id` AND s.`direction`= p.`direction` WHERE s.`date`=3 AND p.`type`=1 AND p.`direction`=1 ORDER BY s.time "
#sql = "SELECT `id`,`direction`,`name` FROM point WHERE `type`=1"
#sql = "SELECT * FROM leg "
sql ="SELECT s.round FROM schedule s INNER JOIN point p  ON s.station_id = p.id AND s.`direction`= p.`direction` WHERE p.`name` = 'ст. м. Харківська' AND s.`date`=3 AND p.`type`=1  AND s.`direction`=1 ORDER BY t_diff(time(s.time), time('11:28')) LIMIT 1"
sql="SELECT * FROM schedule"
cursor = db.execute(sql)
for row in cursor:
    print(row)
cursor.close()

