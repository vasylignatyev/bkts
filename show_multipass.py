#!/usr/bin/python3
import sqlite3


print("connect to database")
db = sqlite3.connect('bkts.db')
curs = db.cursor()
# db.create_function("t_diff", 2, t_diff)


print("SHOW TRUSTED")

cnt = 0

sql = "SELECT `code` FROM `multipass` ORDER BY `code`"

cursor = curs.execute(sql)
for row in curs.execute(sql):
    print("Multipass: {}".format(row[0]))
    cnt += 1
print("*****************************")
print( "Count: {}".format(cnt) )



