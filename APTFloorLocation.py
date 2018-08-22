import csv
from colorama import init
from colorama import Fore, Back, Style
init()

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
locationWords = ["*","FLC","SKIDLINE","SHIPPING", "ASSEMBLY"]
binPop = ""
removeBin = "REMOVELASTBIN"
removeSource = "REMOVESOURCE"
print(Fore.GREEN + title + Style.RESET_ALL)
def mainFunction():
    global mainInput
    global bins
    global sourceLocation
    global destinationLocation
    global tempString
    mainInput = input(Fore.BLUE + Style.BRIGHT + "Please scan the source floor location or your bins: \n" + Style.RESET_ALL)
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
    elif not any(word in mainInput for word in locationWords):
        if (not mainInput):
            mainFunction()
        elif (mainInput in bins):
            print(Fore.RED + Style.BRIGHT + "That bin already has been scanned!")
            mainFunction()
        else:
            if len(bins) == 6:
                print(Fore.RED + Style.BRIGHT + "You are carrying to many bins, please scan your source and destination location" + Style.RESET_ALL)
                mainFunction()
            else:
                bins.append(mainInput)
                tempString = ""
                for x in range(len(bins)):
                    tempString += (bins[x] + ",")
                print(Fore.GREEN + Style.BRIGHT + tempString)
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
        destinationLocation = "F" + mainInput
        print (Fore.GREEN + Style.BRIGHT + tempString + " moved from " + sourceLocation + " to " + destinationLocation)
        sendToCSV()
        mainInput = ""
        bins = []
        sourceLocation = ""
        destinationLocation = ""
        tempString = ""
        mainFunction()

def sendToCSV():
    with open('moves.csv', 'a') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=',')
        total = len(bins) + 2
        print(total)
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
