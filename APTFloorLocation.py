import csv
import sqlite3
import datetime
from colorama import init
from colorama import Fore, Back, Style
init()

db = sqlite3.connect('floorlocation.db')
cursor = db.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS moves (
        date text, bin1 INTEGER, bin2 INTEGER, bin3 INTEGER, bin4 INTEGER, source TEXT, destination TEXT)
''')
title = """
 /$$      /$$           /$$                                            
| $$  /$ | $$          | $$                                            
| $$ /$$$| $$  /$$$$$$ | $$  /$$$$$$$  /$$$$$$  /$$$$$$/$$$$   /$$$$$$ 
| $$/$$ $$ $$ /$$__  $$| $$ /$$_____/ /$$__  $$| $$_  $$_  $$ /$$__  $$
| $$$$_  $$$$| $$$$$$$$| $$| $$      | $$  \ $$| $$ \ $$ \ $$| $$$$$$$$
| $$$/ \  $$$| $$_____/| $$| $$      | $$  | $$| $$ | $$ | $$| $$_____/
| $$/   \  $$|  $$$$$$$| $$|  $$$$$$$|  $$$$$$/| $$ | $$ | $$|  $$$$$$$
|__/     \__/ \_______/|__/ \_______/ \______/ |__/ |__/ |__/ \_______/
     """
mainInput = ""
bins = []
sourceLocation = ""
destinationLocation = ""
tempString = ""
locationWords = ["*","FLC"]
binPop = ""

#COMMANDS
removeBin = "REMOVELASTBIN"
removeSource = "REMOVESOURCE"
removeLastLine = "REMOVELAST"
clearInput = "CLEARINPUT"
startOver = "STARTOVER"

print(Fore.GREEN + title + Style.RESET_ALL)
def mainFunction():
    global mainInput
    global bins
    global sourceLocation
    global destinationLocation
    global tempString
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
                if "1" in fullInput:
                    print("this is a full stack")
                    bins.append(mainInput + ":" + "FULL")
                    tempString = ""
                    for x in range(len(bins)):
                        tempString += (bins[x] + ",")
                    print(Fore.GREEN + Style.BRIGHT + tempString)
                    mainFunction()
                elif "2" in fullInput:
                    partialInput = input(Fore.BLUE + Style.BRIGHT + "Enter the number of units in this stack: \n" + Style.RESET_ALL)
                    bins.append(mainInput + ":" + partialInput)
                    tempString = ""
                    for x in range(len(bins)):
                        tempString += (bins[x] + ",")
                    print(Fore.GREEN + Style.BRIGHT + tempString)
                    mainFunction()
                elif "3" in fullInput:
                    bins.append(mainInput)
                    tempString = ""
                    for x in range(len(bins)):
                        tempString += (bins[x] + ",")
                    print(Fore.GREEN + Style.BRIGHT + tempString)
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
        print (Fore.GREEN + Style.BRIGHT + tempString + " moved from " + sourceLocation + " to " + destinationLocation)
        sendToSQL()
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
    bins.insert(0,'{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
    print(bins)
    cursor.execute('INSERT INTO moves(date,bin1,bin2,bin3,bin4,source,destination) VALUES(?,?,?,?,?,?,?)',bins)
    db.commit() 
def removeLastLineSQL():
    cursor.execute('DELETE FROM moves WHERE rowid = (SELECT MAX(rowid) FROM moves);')
    db.commit()
    print(Fore.YELLOW + Style.BRIGHT + "Your previous entry has been removed!" + Style.RESET_ALL)
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
        csvWriter.writerow(bins)
try:
    mainFunction()
except KeyboardInterrupt:
    print(Fore.RED + """
  /$$$$$$                            /$$ /$$                           /$$
 /$$__  $$                          | $$| $$                          | $$
| $$  \__/  /$$$$$$   /$$$$$$   /$$$$$$$| $$$$$$$  /$$   /$$  /$$$$$$ | $$
| $$ /$$$$ /$$__  $$ /$$__  $$ /$$__  $$| $$__  $$| $$  | $$ /$$__  $$| $$
| $$|_  $$| $$  \ $$| $$  \ $$| $$  | $$| $$  \ $$| $$  | $$| $$$$$$$$|__/
| $$  \ $$| $$  | $$| $$  | $$| $$  | $$| $$  | $$| $$  | $$| $$_____/    
|  $$$$$$/|  $$$$$$/|  $$$$$$/|  $$$$$$$| $$$$$$$/|  $$$$$$$|  $$$$$$$ /$$
 \______/  \______/  \______/  \_______/|_______/  \____  $$ \_______/|__/
                                                   /$$  | $$              
                                                  |  $$$$$$/              
                                                   \______/               
    """ + Style.RESET_ALL)