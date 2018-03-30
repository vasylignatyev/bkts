#!/usr/bin/python3
import sqlite3
import datetime

print("connect to database")
db = sqlite3.connect('bkts.db')

sql = "DELETE  FROM schedule"
db.execute(sql)

params = {"dir":1, "round": 1, "wd":1}

sql = "SELECT s.`id`, p.`name`, s.time, p.`id`, p.`order` " \
              "FROM  point p  LEFT JOIN schedule s " \
              "ON s.`direction`=p.`direction` AND s.`station_id`=p.`id` AND s.`round`=:round AND s.`date`= :wd  " \
              "WHERE p.`direction`=:dir AND p.`type`=1 " \
              "ORDER BY p.`order`"


try:
    cursor = db.execute(sql, params)
    for row in cursor:
        print(row)
except Exception as e:
    print(e)


