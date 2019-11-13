import sqlite3

db = sqlite3.connect('floorlocation.db')
cursor = db.cursor()
try:
    Cart = cursor.execute('SELECT cart FROM moves WHERE rowid = (SELECT MAX(rowid) FROM moves);')
    Cart = cursor.fetchall()
    Employee = cursor.execute('SELECT empID FROM empinfo;')
    Employee = cursor.fetchall()
except:
    Cart = []
    Employee = []

settings = {
    "Version" : "1.8.0",
    "Server" : "wl-scanning",
    "Port" : "10000",
    "DevServer" : "localhost"
}

if not Cart:
    settings['Cart'] = "None"
else:
    settings['Cart'] = Cart[0][0]
if not Employee:
    settings['Employee'] = "Logged Out"
else:
    settings['Employee'] = Employee[0][0]
