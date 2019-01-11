import csv
import sqlite3
import datetime
from colorama import init
from colorama import Fore, Back, Style
init()

#Connect to local DB
db = sqlite3.connect('floorlocation.db')
cursor = db.cursor()

#Check to see if new column for cartnumbers exist, if not add it
cursor.execute('PRAGMA table_info(moves);')
columnInfo = cursor.fetchall()
if  len(columnInfo) == 0:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS moves (
        date text, bin1 INTEGER, bin2 INTEGER, bin3 INTEGER, bin4 INTEGER, source TEXT, destination TEXT, cart INTEGER)
    ''')
    print(Fore.YELLOW + Style.BRIGHT + "Created new FloorLocation Database")
else:
    lastColumn = columnInfo[-1][1]
    if lastColumn != "cart":
        cursor.execute('ALTER TABLE moves ADD COLUMN cart INTEGER')
        print(Fore.YELLOW + Style.BRIGHT + "Added cart column to existing FloorLocation Database")
    else:
        print(Fore.GREEN + Style.BRIGHT + "Database up to date")

#Variable declaration
title = "APT Floor Tracking Version: 1.1.2"
mainInput = ""
bins = []
sourceLocation = ""
destinationLocation = ""
tempString = ""
locationWords = ["*","FLC"]
binPop = ""
cartNumber = 0

#COMMANDS
removeBin = "REMOVELASTBIN"
removeSource = "REMOVESOURCE"
removeLastLine = "REMOVELAST"
clearInput = "CLEARINPUT"
startOver = "STARTOVER"

#Main loop
print(Fore.GREEN + title + Style.RESET_ALL)
def mainFunction():
    global mainInput
    global bins
    global sourceLocation
    global destinationLocation
    global tempString
    global cartNumber
    if cartNumber == 0:
        cartVal = input(Fore.BLUE + Style.BRIGHT + "Please enter your cart number: \n" + Style.RESET_ALL)
        try:
            cartNumber = int(cartVal)
        except:
            print(Fore.RED + Style.BRIGHT + "It looks like that is not a number...")
            cartNumber = 0
            mainFunction()
        finally:
            if (cartNumber < 10) or (cartNumber > 99):
                print(Fore.RED + Style.BRIGHT + "Cart numbers must be two digits...")
                cartNumber = 0
                mainFunction()
        print(Fore.GREEN + Style.BRIGHT + "Welcome cart " + str(cartNumber) + Style.RESET_ALL)
    if (not sourceLocation):
        mainInput = input(Fore.BLUE + Style.BRIGHT + "Please scan the source floor location or your bins: \n" + Style.RESET_ALL)
    else:
        mainInput = input(Fore.BLUE + Style.BRIGHT + "Please scan the destination floor location or your bins: \n" + Style.RESET_ALL)
    if (removeBin in mainInput):
        if (bins):
            bins.pop()
            tempString = ""
            for x in range(len(bins)):
                tempString += (bins[x] + ",")
            if (not bins):
                print(Fore.YELLOW + Style.BRIGHT + "Bins is now empty")
            else:
                print(Fore.GREEN + Style.BRIGHT + tempString)
        else: 
            print(Fore.RED + Style.BRIGHT + "No bins have been scanned yet!")
        mainFunction()
    elif (removeSource in mainInput):
        sourceLocation = ""
        print(Fore.YELLOW + Style.BRIGHT + "Source location has been reset")
        mainFunction()
    elif (removeLastLine in mainInput):
        removeLastLineSQL()
        mainFunction()
    elif (clearInput in mainInput):
        mainInput = ""
        print(Fore.YELLOW + Style.BRIGHT + "You just cleared the input")
        mainFunction()
    elif (startOver in mainInput):
        bins[:] = []
        sourceLocation = ""
        destinationLocation = ""
        print(Fore.YELLOW + Style.BRIGHT + "You just cleared the current session")
        mainFunction()
    elif not any(word in mainInput for word in locationWords):
        if (not mainInput):
            mainFunction()
        #elif (mainInput in bins):
        #    print(Fore.RED + Style.BRIGHT + "That bin already has been scanned!")
        #    mainFunction()
        else:
            if len(bins) == 4:
                print(Fore.RED + Style.BRIGHT + "You are carrying to many bins, please scan your source and destination location" + Style.RESET_ALL)
                mainFunction()
            else:
                fullInput = input(Fore.BLUE + Style.BRIGHT + "Is this a full stack? Press 1 for Yes | 2 for No | 3 for bin: \n" + Style.RESET_ALL)
                if "1" == fullInput:
                    print("this is a full stack")
                    bins.append(mainInput + ":" + "FULL")
                    tempString = ""
                    for x in range(len(bins)):
                        tempString += (bins[x] + ",")
                    print(Fore.GREEN + Style.BRIGHT + tempString)
                    mainFunction()
                elif "2" == fullInput:
                    partialInput = input(Fore.BLUE + Style.BRIGHT + "Enter the number of units in this stack: \n" + Style.RESET_ALL)
                    bins.append(mainInput + ":" + partialInput)
                    tempString = ""
                    for x in range(len(bins)):
                        tempString += (bins[x] + ",")
                    print(Fore.GREEN + Style.BRIGHT + tempString)
                    mainFunction()
                elif "3" == fullInput:
                    bins.append(mainInput)
                    tempString = ""
                    for x in range(len(bins)):
                        tempString += (bins[x] + ",")
                    print(Fore.GREEN + Style.BRIGHT + tempString)
                    mainFunction()
                elif (startOver in fullInput):
                    bins[:] = []
                    sourceLocation = ""
                    destinationLocation = ""
                    tempString = ""
                    print(Fore.YELLOW + Style.BRIGHT + "You just cleared the current session")
                    mainFunction()
                elif (clearInput in fullInput):
                    mainInput = ""
                    tempString = ""
                    print(Fore.YELLOW + Style.BRIGHT + "You just cleared the input")
                    if len(bins) > 0:
                        for x in range(len(bins)):
                            tempString += (bins[x] + ",")
                        print(Fore.GREEN + Style.BRIGHT + tempString + " in your current session.")
                    mainFunction()
                else:
                    print(Fore.YELLOW + Style.BRIGHT + fullInput + " is not an option, please scan your stack or bin again")
                    mainFunction()
    elif (not sourceLocation):
        sourceLocation = "S" + mainInput
        print (Fore.GREEN + Style.BRIGHT + "Source location is: " + sourceLocation + Style.RESET_ALL)
        mainFunction()
    elif (not bins):
        print(Fore.YELLOW + Style.BRIGHT + "Please scan bins before scanning your destination floor location!")
        mainFunction()
    elif (sourceLocation == "S" + mainInput):
        print(Fore.RED + Style.BRIGHT + "Your source and destination cannot be the same!")
        mainFunction()
    else:
        destinationLocation = "E" + mainInput
        sendToSQL()
        print (Fore.GREEN + Style.BRIGHT + tempString + " moved from " + sourceLocation + " to " + destinationLocation + " by cart " + str(cartNumber))
        mainInput = ""
        bins = []
        sourceLocation = ""
        destinationLocation = ""
        tempString = ""
        mainFunction()
def sendToSQL():
    total = len(bins) + 2
    max = 6
    if total < max: 
        while total < max:
            bins.append('')
            total = total + 1
    bins.append(sourceLocation)
    bins.append(destinationLocation)
    bins.append(cartNumber)
    theTime = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    theTime.replace("'",'')
    bins.insert(0,theTime)
    cursor.execute('INSERT INTO moves(date,bin1,bin2,bin3,bin4,source,destination,cart) VALUES(?,?,?,?,?,?,?,?)',bins)
    db.commit() 
def removeLastLineSQL():
    cursor.execute('SELECT * FROM moves ORDER BY rowid DESC LIMIT 1;')
    result = str(cursor.fetchone())
    print(Fore.YELLOW + Style.BRIGHT + "Removing " + result + Style.RESET_ALL)
    cursor.execute('DELETE FROM moves WHERE rowid = (SELECT MAX(rowid) FROM moves);')
    db.commit()
def sendToCSV():
    with open('moves.csv', 'a') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=',')
        total = len(bins) + 2
        max = 8
        if total < max:
            while total < max:
                bins.append('')
                total = total + 1
        bins.append(sourceLocation)
        bins.append(destinationLocation)
        bins.append(cartNumber)
        csvWriter.writerow(bins)
try:
    mainFunction()
except KeyboardInterrupt:
    print(Fore.RED + "Exiting, goodbye!" + Style.RESET_ALL)