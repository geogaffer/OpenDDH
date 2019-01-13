import sqlite3

# TODO: Generalize to function/module.

conn = sqlite3.connect('2018 Drilling.sqlite')
cur = conn.cursor()  # general cursor for various uses

# Find the Collars record for the trace to be processed
name = "MOY18-17"
depth = 44.34

cur.execute('SELECT * FROM Collars WHERE name = ?', (name,))
row = cur.fetchone()
holeid = row[0]

print("Processing DDH ", name)

cur.execute('''SELECT * FROM Traces
        WHERE collar_fk = ? AND distance <= ?
        ORDER BY distance DESC''', [holeid, depth])
row = cur.fetchone()
depthfrom = row[1]
eastfrom = row[2]
northfrom = row[3]
elevfrom = row[4]

cur.execute('''SELECT * FROM Traces
    WHERE collar_fk = ? AND distance > ?
    ORDER BY distance''', [holeid, depth])
row = cur.fetchone()
depthto = row[1]
eastto = row[2]
northto = row[3]
elevto = row[4]

fraction = (depth - depthfrom) / (depthto - depthfrom)
x = (eastto - eastfrom) * fraction + eastfrom
y = (northto - northfrom) * fraction + northfrom
z = (elevto - elevfrom) * fraction + elevfrom

print("From:", depthfrom, eastfrom, northfrom, elevfrom)
print("--->:", depth)
print("  To:", depthto, eastto, northto, elevto)
print("Frac:", fraction)
print("Point east, north, elev:", x, y, z)