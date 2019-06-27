import pyodbc
from dotenv import load_dotenv
load_dotenv()
class SQLServerFunctions:


#pyodbc can only return tuple values from SQL Server, use this to clean them up.
    def RemoveTupleGarbage(self, input):
        garbage = ")''(, "
        for char in garbage:
            input = input.replace(char,'')
        return input

#checks part number against IM1_Inventory masterfile, returns bool value.
    def PartExistsTest(self, partNumber):
        conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=%s;TDS_Version=7.4' % os.getenv("NEWMAS_DB_PASS")) 
        cursor = conn.cursor()
        sql = "DECLARE @response nvarchar(50);EXEC dbo.ABW_DoesItemNumExist @partNum = [{}], @paramOut = @response OUT; SELECT @response AS PartConfirmed;".format(partNumber)
        cursor.execute(sql)
        dirtyRecord = str(cursor.fetchone())
        cleanRecord = self.RemoveTupleGarbage(dirtyRecord)
        if cleanRecord == 'T':
            return True
        elif cleanRecord == 'F':
            return False
        else:
            return 'Error with PartExistsTest function'

if __name__ == '__main__':
    lilbilly = SQLServerFunctions()
    print(lilbilly.PartExistsTest(100))