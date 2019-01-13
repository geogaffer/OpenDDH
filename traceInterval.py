import sqlite3
#import qgis._core

# TODO: Generalize to function/module.

conn = sqlite3.connect('2018 Drilling.sqlite')
cur = conn.cursor()  # general cursor for various uses

# Find the Collars record for the trace to be processed
name = "MOY18-04"
depth1 = 93.93
depth2 = 94.27
filename = name + str(depth1) + ".csv"
print("Writing to", filename)

#f = open(filename, 'w')
f = open('MyNew.csv', 'w')
f.write("name, x, y, z\n")

cur.execute('SELECT * FROM Collars WHERE name = ?', (name,))
row = cur.fetchone()
holeid = row[0]

print("Processing DDH ", name)

# Find the position of the top of the interval

cur.execute('''SELECT * FROM Traces
        WHERE collar_fk = ? AND distance <= ?
        ORDER BY distance DESC''', [holeid, depth1])
row = cur.fetchone()
depthfrom = row[1]
eastfrom = row[2]
northfrom = row[3]
elevfrom = row[4]

cur.execute('''SELECT * FROM Traces
    WHERE collar_fk = ? AND distance > ?
    ORDER BY distance''', [holeid, depth1])
row = cur.fetchone()
depthto = row[1]
eastto = row[2]
northto = row[3]
elevto = row[4]

fraction = (depth1 - depthfrom) / (depthto - depthfrom)
x = (eastto - eastfrom) * fraction + eastfrom
y = (northto - northfrom) * fraction + northfrom
z = (elevto - elevfrom) * fraction + elevfrom

print("From:", depthfrom, eastfrom, northfrom, elevfrom)
print("--->:", depth1)
print("  To:", depthto, eastto, northto, elevto)
print("Frac:", fraction)
print("Point east, north, elev:", x, y, z)
f.write("1," + str(x) + "," + str(y) + "," + str(z) + "\n")

# -----------------------------------------------------------

# Find any trace points within the interval.  (There may be none.)

cur.execute('''SELECT * FROM Traces
        WHERE collar_fk = ? AND distance > ? AND distance <= ?
        ORDER BY distance''', [holeid, depth1, depth2])

print("Trace points:")
for row in cur:
    print("Point east, north, elev:", row[2], row[3], row[4])
    f.write("1," + str(row[2]) + "," + str(row[3]) + "," + str(row[4]) + "\n")

# -----------------------------------------------------------

# Find the position of the bottom of the interval

cur.execute('''SELECT * FROM Traces
        WHERE collar_fk = ? AND distance <= ?
        ORDER BY distance DESC''', [holeid, depth2])
row = cur.fetchone()
depthfrom = row[1]
eastfrom = row[2]
northfrom = row[3]
elevfrom = row[4]

cur.execute('''SELECT * FROM Traces
    WHERE collar_fk = ? AND distance > ?
    ORDER BY distance''', [holeid, depth2])
row = cur.fetchone()
depthto = row[1]
eastto = row[2]
northto = row[3]
elevto = row[4]

fraction = (depth2 - depthfrom) / (depthto - depthfrom)
x = (eastto - eastfrom) * fraction + eastfrom
y = (northto - northfrom) * fraction + northfrom
z = (elevto - elevfrom) * fraction + elevfrom

print("From:", depthfrom, eastfrom, northfrom, elevfrom)
print("--->:", depth2)
print("  To:", depthto, eastto, northto, elevto)
print("Frac:", fraction)
print("Point east, north, elev:", x, y, z)
f.write("1," + str(x) + "," + str(y) + "," + str(z) + "\n")

f.close()

# -----------------------------------------------------------