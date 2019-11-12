import sqlite3

db = sqlite3.connect('floorlocation.db')
cursor = db.cursor()

Cart = cursor.execute('SELECT cart FROM moves WHERE rowid = (SELECT MAX(rowid) FROM moves);')
Cart = cursor.fetchall()
Employee = cursor.execute('SELECT empID FROM empinfo;')
Employee = cursor.fetchall()

settings = {
    "Version" : "1.7.9",
    "Cart" : Cart[0][0],
    "Employee" : Employee[0][0],
    "Server" : "wl-scanning",
    "Port" : "10000",
    "DevServer" : "localhost"
}