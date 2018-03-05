#!/usr/bin/python3
import sqlite3


print("connect to database")
db = sqlite3.connect('bkts.db')
curs = db.cursor()

print("SHOW DEFERRED")

cnt = 0

sql = "SELECT `code`,`type` FROM `deferred` ORDER BY `code`"

cursor = curs.execute(sql)
for row in curs.execute(sql):
    print("Deferred code: {} type {}".format(row[0],row[1]))
    cnt += 1
print("*****************************")
print( "Count: {}".format(cnt) )



