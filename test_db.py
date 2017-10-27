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

# CREATE equipment
sql = "CREATE TABLE IF NOT EXISTS equipment " \
      "(`mac` TEXT primary key," \
      "`serial_number` TEXT," \
      "`type` INTEGER," \
      "`i_vehicle` INTEGER DEFAULT 0,"
self.db().execute(sql)

self.db().commit()

sql = "INSERT INTO equipment (`mac`,`serial_number`,`type`) VALUES (?,?,?)"

