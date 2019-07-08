import pyodbc
#from dotenv import load_dotenv
#load_dotenv()
#import os
class SQLServerFunctions:


#pyodbc can only return tuple values from SQL Server, use this to clean them up.
    def RemoveTupleGarbage(self, input):
        garbage = ")''(, "
        for char in garbage:
            input = input.replace(char,'')
        return input

    def WeighLaterTest(self, binCode):
            
            conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=lookincw;TDS_Version=7.4')
            #conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=%s;TDS_Version=7.4' % os.getenv("NEWMAS_DB_PASS")) 
            
            cursor = conn.cursor()
            sql = "DECLARE @response nvarchar(50);EXEC dbo.ABW_WeighLaterTest @binCode = [{}], @paramOut = @response OUT; SELECT @response AS PartConfirmed;".format(binCode)
            cursor.execute(sql)
            dirtyRecord = str(cursor.fetchone())
            cleanRecord = self.RemoveTupleGarbage(dirtyRecord)
            if cleanRecord == 'T':
                return True
            elif cleanRecord == 'F':
                return False
            else:
                return 'Error with WeighLaterTest function'
            conn.close()
    
    def UpdateWipBin(self, binCode, binWeight):     
        conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=lookincw;TDS_Version=7.4')
        #until dotenv is fixed leave below line out
        #conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=%s;TDS_Version=7.4' % os.getenv("NEWMAS_DB_PASS"))  
        conn.autocommit = False
        cursor = conn.cursor() 
        cursor.execute("EXEC dbo.ABW_UpdateWipBinData @binCode = {}, @binWeight = [{}];".format(binCode,binWeight))
        conn.commit()
        conn.close()   

#checks part number against IM1_Inventory masterfile, returns bool value.
    def PartExistsTest(self, partNumber):
        
        conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=lookincw;TDS_Version=7.4')
        #conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=%s;TDS_Version=7.4' % os.getenv("NEWMAS_DB_PASS")) 
        
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
        conn.close()
    
    def LocationExistsTest(self, location):
    
        conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=lookincw;TDS_Version=7.4')
        #conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=%s;TDS_Version=7.4' % os.getenv("NEWMAS_DB_PASS"))    
        cursor = conn.cursor()
        sql = "DECLARE @response nvarchar(50);EXEC dbo.ABW_DoesLocationExist @Location = [{}], @paramOut = @response OUT; SELECT @response AS PartConfirmed;".format(location)
        cursor.execute(sql)
        dirtyRecord = str(cursor.fetchone())
        cleanRecord = self.RemoveTupleGarbage(dirtyRecord)
        if cleanRecord == 'T':
            return True
        elif cleanRecord == 'F':
            return False
        else:
            return 'Error with LocationExistsTest function'
        conn.close()

    def SubmitWipBin(self, EmpId, FilledBinWeight,WipNum,ScanCode0, ScanCode1, ScanCode2,ScaleIp,sourceLoc,destLoc,typeOfBin):
        if typeOfBin == '1':
            binTypeChar = 'fl'
        if typeOfBin == '2':
            binTypeChar = 'wb'
        if typeOfBin == '3':
            binTypeChar = 'pl'
        if typeOfBin == '4':
            binTypeChar = 'gl'
        
        conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=lookincw;TDS_Version=7.4')
        
        #until dotenv is fixed leave below line out
        #conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=%s;TDS_Version=7.4' % os.getenv("NEWMAS_DB_PASS"))  
        
        conn.autocommit = False
        cursor = conn.cursor() 
        #@PartNum parameter had to be escaped with [] for hyphens to correctly pass through
        cursor.execute("EXEC dbo.ABW_WIP_BinInsert @EmpID = {}, @FilledBinWeight = [{}], @PartNum = [{}], @ScanCode0 = [{}], @ScanCode1 = [{}], @ScanCode2 = [{}], @ScaleIp = [{}], @SourceLocation = [{}], @DestinationLocation = [{}], @BinType = [{}] ".format(EmpId,FilledBinWeight,WipNum,ScanCode0,ScanCode1,ScanCode2,ScaleIp,sourceLoc,destLoc,binTypeChar))
        conn.commit()
        conn.close()   

    def SubmitCondition(self, emptyWeight,ScanCode,Condition,binType,scaleIp):
        if binType == '1':
            binTypeChar = 'fl'
        if binType == '2':
            binTypeChar = 'wb'
        if binType == '3':
            binTypeChar = 'pl'
        if binType == '4':
            binTypeChar = 'gl'
        else: 
            conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=lookincw;TDS_Version=7.4')
            #conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=%s;TDS_Version=7.4' % os.getenv("NEWMAS_DB_PASS"))
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("EXEC dbo.ABW_bindataInsert @emptyweight = {}, @scancode = {}, @condition = {}, @binTypeChar = {}, @scaleIp = [{}]".format(emptyWeight,ScanCode,Condition,binTypeChar,scaleIp))
            conn.commit()
            conn.close()

    

if __name__ == '__main__':
    lilbilly = SQLServerFunctions()
    print(lilbilly.PartExistsTest(100))