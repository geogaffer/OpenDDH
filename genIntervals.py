import sqlite3
import trInterval
import math

# Generate desurveyed intervals from a table of downhole intervals

conn = sqlite3.connect('2018 Drilling.sqlite')
cur = conn.cursor()  # general cursor
cur2 = conn.cursor() # cursor for UPDATEs

inName = input("File name (csv) with downhole intervals to convert: ")
fhIn = open(inName)

for line in fhIn:
    parts = line.split(',')


csvInterval(conn, fh, ddhName, depth1, depth2, debug=0):