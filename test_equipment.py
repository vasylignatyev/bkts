#!/usr/bin/python3
import sqlite3
import datetime


print("connect to database")
db = sqlite3.connect('bkts.db')

c = db.cursor()
# sql = "SELECT * FROM equipment"

'''
type name
1 BKTS
2 Validator
4 IKTS
'''

# sql="SET I = 8"
# db.execute(sql)

equipment = []

sql = "SELECT 5,`last_status`,`mac` FROM equipment where type = 4"
result = c.execute(sql)
for row in result:
    (i, last_status, mac) = row
    equipment.append(dict(
        type = i,
        state = last_status,
        mac=mac,
    ))


sql = "SELECT 7,`last_status`,`mac` FROM equipment where type = 1"
result = c.execute(sql)
for row in result:
    (i, last_status, mac) = row
    equipment.append(dict(
        type = i,
        state = last_status,
        mac=mac,
    ))


sql = "SELECT 8,`last_status`,`mac` FROM equipment where type = 2"
result = c.execute(sql)
k = 0
for row in result:
    (i, last_status, mac) = row
    equipment.append(dict(
        type = i+k,
        state = last_status,
        mac=mac,
    ))
    k+=1

print(equipment)