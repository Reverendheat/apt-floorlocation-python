import pyodbc
import sqlite3
from dotenv import load_dotenv
load_dotenv()
import os

db = sqlite3.connect('floorlocation.db')
sqlitecursor = db.cursor()

conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=%s;TDS_Version=7.4' % os.getenv("NEWMAS_DB_PASS"))  
conn.autocommit = False
cursor = conn.cursor()

sqlitecursor.execute('SELECT rowid, * FROM wipfl')
for row in sqlitecursor:
    cursor.execute("EXEC dbo.ABW_WIP_BinInsert @EmpID = {}, @FilledBinWeight = [{}], @PartNum = [{}], @ScanCode0 = [{}], @ScanCode1 = [{}], @ScanCode2 = [{}], @ScaleIp = [{}], @SourceLocation = [{}], @DestinationLocation = [{}], @BinType = [{}], @timeEntered = [{}] ".format(row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))
    sqlitecursor.execute('DELETE FROM wipfl WHERE rowid={}'.format(row[0]))

db.commit()
conn.commit()
conn.close()
db.close()