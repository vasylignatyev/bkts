#!/usr/bin/python3
import sqlite3


print("connect to database")
db = sqlite3.connect('bkts.db')
curs = db.cursor()
# db.create_function("t_diff", 2, t_diff)


print("SHOW TRUSTED")
cnt = 0

sql = "SELECT `code`,`quantity`,`amount` FROM `trusted` ORDER BY `code`"
cursor = curs.execute(sql)
print("Fields :  `code`,`quantity`,`amount`")
for row in curs.execute(sql):
    print("Trusted: {}".format(str(row)))
    cnt += 1
print("*****************************")
sql = "UPDATE `trusted` SET `amount` = `amount`- 6000 WHERE `code` = '0473DBFA4F5380' AND `amount`>= 6000"
curs.execute(sql)
row = curs.execute("SELECT changes()").fetchone()
print(row)
print("*****************************")
sql = "SELECT `code`,`quantity`,`amount` FROM `trusted` ORDER BY `code`"
cursor = curs.execute(sql)
print("Fields :  `code`,`quantity`,`amount`")
for row in curs.execute(sql):
    print("Trusted: {}".format(str(row)))
    cnt += 1
print("*****************************")
print( "Count: {}".format(cnt) )



