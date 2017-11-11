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
curs = db.cursor()
# db.create_function("t_diff", 2, t_diff)

# CREATE equipment
sql = "SELECT name, direction FROM `point` WHERE `type`=1 ORDER BY direction, id"

sql = "SELECT " \
          "p.name," \
          "-1001, " \
          "-1001 " \
          "from schedule s " \
          "INNER JOIN point p  ON s.station_id = p.id AND s.`direction`= p.`direction` " \
          "WHERE s.round={round} AND s.`date`='{wd}' AND s.`direction`={direction} AND p.`type`=1 " \
          "ORDER BY s.time".format(round=3, wd=1, direction=1)
schedule = []
for row in curs.execute(sql):
    schedule.append(dict(zip(('name','schedule','lag'), row)))
print(schedule)



