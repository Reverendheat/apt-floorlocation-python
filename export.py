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

sqlitecursor.execute('SELECT * FROM wipfl')
for stuff in sqlitecursor:
    cursor.execute("EXEC dbo.ABW_WIP_BinInsert @EmpID = {}, @FilledBinWeight = [{}], @PartNum = [{}], @ScanCode0 = [{}], @ScanCode1 = [{}], @ScanCode2 = [{}], @ScaleIp = [{}], @SourceLocation = [{}], @DestinationLocation = [{}], @BinType = [{}] ".format(stuff[0],stuff[1],stuff[2],stuff[3],stuff[4],stuff[5],stuff[6],stuff[7],stuff[8],stuff[9]))


conn.commit()
conn.close()   
