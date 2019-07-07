import urwid
import urwid.raw_display
import urwid.web_display
import socket
import pyodbc
#from dotenv import load_dotenv
#load_dotenv()
#import os
from SQLServerClasses import SQLServerFunctions

#assign key remappings here, this overrides the keypress method of urwid.ListBox
class MyBox(urwid.ListBox):
    def keypress(self, size, key): 
        if key == '/':
            key = 'up'
        if key == '+':
            key = 'down'
        if key == 'f8':
            raise urwid.ExitMainLoop()
        super().keypress(size, key) 

global Weight
Weight = '' 
global ScanCode0
ScanCode0 = ''
global ScanCode1
ScanCode1 = ''
global ScanCode2
ScanCode2 = ''
global WipNum
WipNum = ''
global ScaleCode
ScaleCode = ''
global Cleared
Cleared = ""

global BinType
BinType = ''
global SourceLocation
SourceLocation = ''
global DestinationLocation
DestinationLocation = ''

def main(): 
    
    #makes scale connection, grabs the weight, and closes the connection.
    def CollectWeight(ScaleCode):
        s = socket.socket()
        s.settimeout(2)
        port = 23
        try:
            s.connect((ScaleCode,23))
            #s.connect(('10.79.3.33', 23))
            s.settimeout(None)
            try:
                scaleData1  = s.recv(19) #19 bytes to trim off lbs, tare, and net weight information
                scaleData2 = scaleData1.decode()
                scaleData3 = scaleData2.replace('Gross','') #wipes off 'Gross' text
                scaleData4 = scaleData3.lstrip() #wipes leading spaces
                return scaleData4
            except:
                return('SktRecErr!')
        except:
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #return('800.01')
            return('SktCnctErr!')
         
    def CollectCode(bincodeindex):
        listbox.set_focus(bincodeindex)
        _, boxText = listbox.get_focus() 
        code = listbox_content[boxText].original_widget.base_widget._edit_text
        return code
    
    def ResetCode(codeindex): 
        listbox.set_focus(codeindex-1) #need to hop around here - directly focusing to the 3rd field clears the value, but does not update the graphic
        listbox.set_focus(codeindex)
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(Cleared) 

    def ResetWeight(text): 
        listbox.set_focus(14) #index
        _, boxText = listbox.get_focus()
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(text)
        global Weight
        Weight = ''
        


    text_header = (u"WIP Weight and Transfer Application. / for UP  + for DOWN.") #adjust this per keypad
    #text_intro = [(
    #    u"Part MUST be the same if "
    #    u"moving multiple bins.")]  

    textEditSourceLocation = ('editcp', u"Source Location: ")
    textEditDestinationLocation = ('editcp', u"Destination Location: ")

    textEditBinCode = ('editcp', u"Bin Code 1: ")
    textEditWipNum = ('editcp', u"Part Num: ")
    textEditBinCode1 = ('editcp', u"Bin Code 2: ")
    textEditBinCode2 = ('editcp', u"Bin Code 3: ")
    text_bintypes = [(
        u" 1 = Flat Bin | 2 = Wheel Bin |"
        u" 3 = Plastic Bin | 4 = Gaylord")]
    textEditBinType = ('editcp', u"Bin Type: ")
    textEditScaleCode = ('editcp', u"Scale Code : ")
    textEditWeight = ('editcp', u"Total Bin Weight: ")  
    text_enterDash = [u"Enter a dash - to record weight later."]
    text_WeightButton = [u"Update Weight"]
    text_ExitButton = [u"Exit Application"]
    #Weight = "Scan Scale Code"
    def WeightButton_press(button):
        ScaleCode = CollectCode(12) #index
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'button')
        listbox.set_focus(14) #index
        global Weight
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        Weight = '800.01'
        #Weight = CollectWeight(ScaleCode) 
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(Weight)

    
    
    text_divider =  [u"Press SUBMIT to insert data and reset."]

    submit_text_button_list = [u"SUBMIT"]
    def submit_button_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'header')
        SqlFunctions = SQLServerFunctions()
        EmpId = 'xxxx'
        typeOfBin = CollectCode(9)
        WipNum = CollectCode(3)
        ScaleIp = CollectCode(12)
        ScanCode0 = CollectCode(5) 
        ScanCode1 = CollectCode(6)
        ScanCode2 = CollectCode(7)
        
        sourceLoc = CollectCode(1)[1:] #removes leading *
        destLoc = CollectCode(18)[1:] 
        if (len(sourceLoc) < 2):  #sql lookups will break if passing in blank values, so validate these parameter's lengths first
            ResetCode(1)
        elif(len(destLoc) < 2 ):
                ResetCode(18) 
        elif (len(WipNum) != 12):
                ResetCode(3) 
        else:
            isPartValid = SqlFunctions.PartExistsTest(WipNum) 
            isSourceLocationValid = SqlFunctions.LocationExistsTest(sourceLoc)
            isDestinationLocationValid = SqlFunctions.LocationExistsTest(destLoc)
            
            global Weight
            FilledBinWeight = Weight      
            manualEntry = CollectCode(14)

            if FilledBinWeight == '' or (len(manualEntry) > 0):
                FilledBinWeight = manualEntry
            if (ScanCode1 == ''):
                ScanCode1 = 'NA'
            if (ScanCode2 == ''):
                ScanCode2 = 'NA'
            if ScanCode0 == ScanCode1:
                ResetCode(6)
            elif typeOfBin not in ['1','2','3','4']:
                ResetCode(9)
            elif ScanCode1 == ScanCode2 and ScanCode1 != 'NA':
                ResetCode(5)
            elif (len(ScanCode0) != 5): #must be at least one bin
                ResetCode(5)
            elif (len(ScanCode1) != 5) and ((ScanCode1) != 'NA'): 
                ResetCode(6)  
            elif (len(ScanCode2) != 5) and ((ScanCode2) != 'NA'):
                ResetCode(7)
            elif isPartValid == False:
                ResetCode(3)
            elif isSourceLocationValid == False:
                ResetCode(1)
            elif isDestinationLocationValid == False:
                ResetCode(18)
            elif ((len(FilledBinWeight)) < 1): 
                ResetCode(14)
            else:
                SqlFunctions.SubmitWipBin(EmpId,FilledBinWeight,WipNum,ScanCode0,ScanCode1,ScanCode2,ScaleIp,sourceLoc,destLoc,typeOfBin)               
                #clear weight,Scancode, WIP #
                for i in [18,3,5,6,7,9,12,14,1]:
                    ResetCode(i)
                FilledBinWeight = ''
                Weight = ''
    
    def ExitButton_Press(button):
        raise urwid.ExitMainLoop()
            
   
    #index numbers for reference []
    blank = urwid.Divider()
    listbox_content = [
        blank, #[0]
        #urwid.Padding(urwid.Text(text_intro), left=2, right=2, min_width=20), #[]
        #blank, #[] 
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditSourceLocation, SourceLocation), # [1] SourceLocation
            'editbx','editfc' ), left=10, width=30),
        blank, #[2]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditWipNum, WipNum), # [3] wipnum
            'editbx','editfc' ), left=10, width=24),
        blank, #[4]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode, ScanCode0), # [5] bincode0
            'editbx','editfc' ), left=10, width=22),
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode1, ScanCode1), # [6] bincode1
            'editbx','editfc' ), left=10, width=22),
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode2, ScanCode2), #[7] bincode2
            'editbx','editfc' ), left=10, width=22),
        blank, #[8]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinType, BinType), # [9]bintype
            'editbx','editfc' ), left=10, width=20),
        urwid.Padding(urwid.Text(text_bintypes), left=2, right=2, min_width=20), # [10]bin types description
        blank, #[11]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditScaleCode, ScaleCode), #[12] ScaleCode
            'editbx','editfc' ), left=10, width=31),
        blank, #[13]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditWeight, Weight), # [14] weight
            'editbx','editfc' ), left=5, width=36),
        urwid.Padding(urwid.Text(text_enterDash), left=2, right=2, min_width=20), #[15] enter dash text line
        urwid.Padding(urwid.GridFlow(
            [urwid.AttrWrap(urwid.Button(txt, WeightButton_press),
                'buttn','buttnf') for txt in text_WeightButton],
            10, 3, 1, 'left'),
            left=17, right=3, min_width=13), #[16] weight button 
        blank, #[17]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditDestinationLocation, DestinationLocation), # [18] DestinationLocation
                    'editbx','editfc' ), left=10, width=35),      
        urwid.AttrWrap(urwid.Divider("=", 1), 'bright'), #[19]
        urwid.Padding(urwid.Text(text_divider), left=2, right=2, min_width=20), #[20]
        urwid.AttrWrap(urwid.Divider("-", 0, 1), 'bright'), #[21]
        urwid.Padding(urwid.GridFlow(                           #22 submit button
            [urwid.AttrWrap(urwid.Button(txt, submit_button_press),
                'buttn','buttnf') for txt in submit_text_button_list],
            15, 3, 1, 'left'),
            left=15, right=3, min_width=13),
        blank,
        urwid.Padding(urwid.GridFlow(
            [urwid.AttrWrap(urwid.Button(txt, ExitButton_Press),
                'buttn','buttnf') for txt in text_ExitButton],
            15, 3, 1, 'left'),
            left=15, right=3, min_width=20), 
        
         ]


    header = urwid.AttrWrap(urwid.Text(text_header), 'header')
    listbox = MyBox(urwid.SimpleListWalker(listbox_content))
    frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)

    palette = [
        ('body','black','light gray', 'standout'),
        ('reverse','light gray','black'),
        ('header','white','dark red', 'bold'),
        ('important','dark blue','light gray',('standout','underline')),
        ('editfc','white', 'dark blue', 'bold'),
        ('editbx','light gray', 'dark blue'),
        ('editcp','black','light gray', 'standout'),
        ('bright','dark gray','light gray', ('bold','standout')),
        ('buttn','black','dark cyan'),
        ('buttnf','white','dark blue','bold'),
        ]

    
    # use appropriate Screen class
    if urwid.web_display.is_web_request():
        screen = urwid.web_display.Screen()
    else:
        screen = urwid.raw_display.Screen()

    urwid.MainLoop(frame, palette, screen).run()


def setup():
    urwid.web_display.set_preferences("Urwid Tour")
    # try to handle short web requests quickly  
    if urwid.web_display.handle_short_request():
        return

    main()


if '__main__'==__name__ or urwid.web_display.is_web_request():
    setup()