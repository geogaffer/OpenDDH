import sqlite3
import math

# TODO: Generalize to function/module.

tick = 10  # length of generated intermediate intervals
conn = sqlite3.connect('2018 Drilling.sqlite')
cur = conn.cursor()  # general cursor
cur2 = conn.cursor() # cursor for UPDATEs

# Find the Collars record for the trace to be processed
name="MOY18-06"
cur.execute('SELECT * FROM Collars WHERE name = ?', (name,))

print("Processing DDH ", name)
print("Collar Data:")
print("row count:", cur.rowcount)
row = cur.fetchone()
# TODO: generalize collar records from positions to field names.
print("row[0], x, y, z, az, dip:", row[0], row[2], row[3], row[4], row[6], row[7])
holeid = row[0]
eastfrom = row[2]
northfrom = row[3]
elevfrom = row[4]
collarAz = row[6]
collarDip = row[7]

# Empty Traces of records for holeid
cur.execute('''DELETE FROM Traces WHERE collar_fk = ? ''', [holeid])

# Get the Surveys entries for the drill hole being processed
cur.execute('''SELECT * FROM Surveys
    WHERE id_fk = ? ORDER BY distance''', [holeid])

# Put the collar coords in as the first trace point, the anchor
cur2.execute('''INSERT INTO
    Traces (collar_fk, distance, easting, northing, elev, type_fk, azimuth, dip)
    VALUES (?, 0, ?, ?, ?, 1, ?, ?)''', (holeid, eastfrom, northfrom, elevfrom, collarAz, collarDip))

# Add the downhole survey points as trace points
eoh = 0
rcount = 0

print("Survey points loaded:")
# TODO: generalize survey records from positions to field names.
for row in cur:
    print('Distance:', row[1], "Az:", row[2], "Dip:", row[3])
    rcount = rcount + 1
    if rcount == 1: continue
    cur2.execute('''
    INSERT INTO Traces (collar_fk, distance, easting, northing, elev, type_fk, azimuth, dip)
        VALUES (?, ?, 0, 0, 0, 1, ?, ?)''', (holeid, row[1], row[2], row[3]))
    if row[1] > eoh: eoh = row[1]
print("Survey points:", rcount)
print("EOH at:", eoh)
conn.commit()

# TODO: check if last survey point is beyond EOH.
# TODO: add EOH survey point if missing.
# TODO: (optional) extrapolate azimuth and dip of foot from rate of change at last survey point.

# Add trace points at interval tick, unless a survey point already EXISTS
# there.  These will be trace points where there is a direction change.
n = tick
while n < eoh :
    cur.execute('SELECT * FROM Traces WHERE collar_fk = ? AND distance = ? ', (holeid, n))
    row = cur.fetchone()
    if row is None:
        cur2.execute('''INSERT INTO Traces (collar_fk, distance, easting, northing, elev, type_fk)
            VALUES (?, ?, 0, 0, 0, 2)''', (holeid, n))
    n = n + tick
conn.commit()

# Interpolate the azimuth and dip at tick tracepoints.
# Load the survey tracepoints into cur.

# For each pair of survey tracepoints interpolate the ticks between them

surveys = conn.cursor() # a couple more cursors to make the code more readable
ticks = conn.cursor()

surveys.execute('''SELECT * FROM Traces
    WHERE collar_fk = ? AND type_fk = 1 ORDER BY distance''', [holeid])

survrows = 0
for survrow in surveys:
    if survrows == 0:
        print(survrow)
        print(survrow[6])
        lastdist = survrow[1]
        lastaz = survrow[6]
        lastdip = survrow[7]
        survrows = survrows + 1
        continue
    survrows = survrows + 1

    ticks.execute('''SELECT * FROM Traces
        WHERE collar_fk = ? AND type_fk = 2
            AND distance > ? AND distance <= ?
        ORDER BY distance''', [holeid, lastdist, survrow[1]])

    for tickrow in ticks:
        print(tickrow)
        ivalfrac = (tickrow[1] - lastdist) / (survrow[1] - lastdist)
        localaz = (survrow[6] - lastaz) * ivalfrac + lastaz
        localdip = (survrow[7] - lastdip) * ivalfrac + lastdip
        # Now udate the tickrow parameters
        cur.execute('''UPDATE Traces SET azimuth = ?, dip = ?
        WHERE collar_fk = ? AND type_fk = 2 AND distance = ?''',
                    (localaz, localdip, holeid, tickrow[1]))

    lastdist = survrow[1]
    lastaz = survrow[6]
    lastdip = survrow[7]

    # if last surv dist < tick dist <= surv dist then process

conn.commit()

# Last step.  Ready to project the X,Y,Z coordinates along the trace.

cur.execute('''SELECT * FROM Traces
    WHERE collar_fk = ? ORDER BY distance''', [holeid])

tracerows = 0
for tracerow in cur2: tracerows = tracerows + 1
print('Tracerows:', tracerows)

tracerows = 0
for tracerow in cur:
    if tracerows == 0:
        lastdist = tracerow[1]
        lastaz = tracerow[6]
        lastdip = tracerow[7]
        xlast = tracerow[2]
        ylast = tracerow[3]
        zlast = tracerow[4]
        tracerows = tracerows + 1
        print(tracerows, lastdist, xlast, ylast, zlast, lastaz, lastdip)
        continue
    tracerows = tracerows + 1
    d = tracerow[1] - lastdist
    znew = zlast - math.sin(math.radians(lastdip)) * d
    dhor = math.cos(math.radians(lastdip)) * d
    xnew = xlast + math.sin(math.radians(lastaz)) * dhor
    ynew = ylast + math.cos(math.radians(lastaz)) * dhor
    print(tracerows, tracerow[1], xnew, ynew, znew, lastaz, lastdip)
    cur2.execute('''UPDATE Traces SET easting = ?, northing = ?, elev = ?
        WHERE collar_fk = ? AND distance = ?''',
                (xnew, ynew, znew, holeid, tracerow[1]))
    lastdist = tracerow[1]
    lastaz = tracerow[6]
    lastdip = tracerow[7]
    xlast = xnew
    ylast = ynew
    zlast = znew

print('Finished updating trace:', tracerows, 'ticks.')
conn.commit()
cur.close()
cur2.close()
surveys.close()
ticks.close()
