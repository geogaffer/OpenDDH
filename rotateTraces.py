import math
import sqlite3

# import * from math
# import qgis._core

# TODO: Generalize to function/module.

conn = sqlite3.connect('2018 Drilling.sqlite')
cur = conn.cursor()  # general cursor
curOut = conn.cursor()  # cursor for output in rotation loop

'''
Rotation

x' = x * cos(theta) - y * sin(theta)
y' = x * sin(theta) + y * cos(theta)

x = xi - xorg
y = yi - yorg

x'' = x' + xoff
y'' = y' + yoff
'''

secname = 'Traces135'
theta = 180 - 135
theta = math.radians(theta)

xorg = 692963.6814190865  # copy and pasted from
yorg = 666925.9742074887

xoff = 1000  # possibly use this as the default when this is converted to a function
yoff = 10000  # possibly use this as the default when this is converted to a function

# Drop the rotated traces table if it exists
sql = "DROP TABLE IF EXISTS " + secname
print(sql)
cur.execute(sql)

# Build a copy of Traces named TracesXXX where XXX will be orientation of the sections
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='Traces'")
row = cur.fetchone()
sql = row[0]
newsql = sql.replace('Traces', secname)
print(newsql)

cur.execute(newsql)

sql = 'INSERT INTO ' + secname + ' SELECT * FROM Traces'
cur.execute(sql)

sql = 'SELECT * FROM ' + secname
cur.execute(sql)

for row in cur:
    x = row[2]
    y = row[3]
    hole_id = row[0]
    distance = row[1]

    xnew = (x - xorg) * math.cos(theta) - (y - yorg) * math.sin(theta)
    ynew = (x - xorg) * math.sin(theta) + (y - yorg) * math.cos(theta)

    xnew = xnew + xoff
    ynew = ynew + yoff

    print("rot: ", x, y, " to: ",  xnew, ynew)

    sql = 'UPDATE ' + secname + ''' SET
        (easting, northing)
        = (?, ?)
        WHERE collar_fk = ? AND distance = ?'''
    curOut.execute(sql, (xnew, ynew, hole_id, distance))
    conn.commit()

print("finished...")