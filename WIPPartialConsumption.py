import urwid
import urwid.raw_display
import urwid.web_display
import socket
import pyodbc
from dotenv import load_dotenv
load_dotenv()
import os
from SQLServerClasses import SQLServerFunctions

#assign key remappings here, this overrides the keypress method of urwid.ListBox
class MyBox(urwid.ListBox):
    def keypress(self, size, key): 
        if key == '/':
            key = 'up'
        if key == '+':
            key = 'down'
        if key == 'enter':
            if 'editbx' in str(self.get_focus_widgets()[0]):
                key = 'down'        
        if key == 'f8':
            raise urwid.ExitMainLoop()
        if key == '|':
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

global ScaleCode
ScaleCode = ''
global Cleared
Cleared = ""

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
        listbox.set_focus(9) #index
        _, boxText = listbox.get_focus()
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(text)
        global Weight
        Weight = ''
        


    text_header = (u"WIP Assembly Partial Consumption to Inventory Row/Location Move.") 

    textEditSourceLocation = ('editcp', u"Origination Row/Location: ")
    textEditDestinationLocation = ('editcp', u"Destination Row/Location: ")

    textEditBinCode = ('editcp', u"Bin Code 1: ")
    textEditWipNum = ('editcp', u"Inventory Part Num: ")
    textEditBinCode1 = ('editcp', u"Bin Code 2: ")
    textEditBinCode2 = ('editcp', u"Bin Code 3: ")

    textEditBinType = ('editcp', u"Bin Type: ")
    textEditScaleCode = ('editcp', u"QR Scale Code: ")
    #textEditWeight = ('editcp', u"Total Bin Weight: ")  
    textWeight = urwid.Text(u"Weight")
    text_enterDash = [u""]
    text_WeightButton = [u"Update Weight"]
    text_ExitButton = [u"   Exit Application"]
    def WeightButton_press(button):
        ScaleCode = CollectCode(7) #index
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'button')
        listbox.set_focus(9) #index
        global Weight
        Weight = CollectWeight(ScaleCode) 
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        #am.set_edit_text(Weight)
        textWeight.set_text(Weight)

    
    
    text_divider =  [u"Press SUBMIT to insert data and reset."]

    submit_text_button_list = [u"  SUBMIT"]
    def submit_button_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'header')
        SqlFunctions = SQLServerFunctions()
        EmpId = 'xxxx'
        ScaleIp = CollectCode(7)
        ScanCode0 = CollectCode(3) 
        ScanCode1 = CollectCode(4)
        ScanCode2 = CollectCode(5)
        sourceLoc = CollectCode(1)[1:] #removes leading *
        destLoc = CollectCode(13)[1:] 
        WipNum = 'USE-HISTORIC'
        typeOfBin = '-'
        if (len(sourceLoc) < 2):  #sql lookups will break if passing in blank values, so validate these parameter's lengths first
            ResetCode(1)
        elif(len(destLoc) < 2 ):
                ResetCode(13) 
       
        else:            
            global Weight
            FilledBinWeight = Weight      
            manualEntry = textWeight.text
            if ScaleIp == '':
                ScaleIp = '-'
            if FilledBinWeight == '' or (len(manualEntry) > 0):
                FilledBinWeight = manualEntry
            if (ScanCode1 == ''):
                ScanCode1 = 'NA'
            if (ScanCode2 == ''):
                ScanCode2 = 'NA'
            if ScanCode0 == ScanCode1:
                ResetCode(4)
            elif ScanCode1 == ScanCode2 and ScanCode1 != 'NA':
                ResetCode(3)
            elif (len(ScanCode0) != 5): #must be at least one bin
                ResetCode(3)
            elif (len(ScanCode1) != 5) and ((ScanCode1) != 'NA'): 
                ResetCode(4)  
            elif (len(ScanCode2) != 5) and ((ScanCode2) != 'NA'):
                ResetCode(5)
            elif ScanCode0 == ScanCode2:
                ResetCode(5)
            elif ((len(FilledBinWeight)) < 1) or FilledBinWeight == '' or FilledBinWeight == 'SktCnctErr!' or FilledBinWeight == 'SktRecErr!' or ((len(FilledBinWeight)) > 7) or FilledBinWeight == 'Scale Error': 
                #ResetCode(9)
                textWeight.set_text('Scale Error')
            else:
                SqlFunctions.SubmitWipBin(EmpId,FilledBinWeight,WipNum,ScanCode0,ScanCode1,ScanCode2,ScaleIp,sourceLoc,destLoc,typeOfBin)               
                #clear weight,Scancode, WIP #
                #for i in [13,9,7,5,4,3,1]:
                for i in [13,7,5,4,3,1]:
                    ResetCode(i)
                FilledBinWeight = ''
                Weight = ''
                textWeight.set_text('0.0')
    
    def ExitButton_Press(button):
        raise urwid.ExitMainLoop()
            
   
    #index numbers for reference []
    blank = urwid.Divider()
    listbox_content = [
        blank, #[0]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditSourceLocation, SourceLocation), # [1] SourceLocation
            'editbx','editfc' ), left=1, width=40),
        blank, #[2]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode, ScanCode0), # [3] bincode0
            'editbx','editfc' ), left=15, width=26),
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode1, ScanCode1), # [4] bincode1
            'editbx','editfc' ), left=15, width=26),
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode2, ScanCode2), #[5] bincode2
            'editbx','editfc' ), left=15, width=26),
        blank, #[6]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditScaleCode, ScaleCode), #[7] ScaleCode
            'editbx','editfc' ), left=12, width=29),
        blank, #[8]
        #urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditWeight, Weight), # [9] weight
        #    'editbx','editfc' ), left=9, width=32),
        urwid.Padding(textWeight, left=29, right=2, min_width=20), #[9]
        urwid.Padding(urwid.Text(text_enterDash), left=2, right=2, min_width=20), #[10] enter dash text line
        urwid.Padding(urwid.GridFlow(
            [urwid.AttrWrap(urwid.Button(txt, WeightButton_press),
                'buttn','buttnf') for txt in text_WeightButton],
            10, 3, 1, 'left'),
            left=29, right=3, min_width=13), #[11] weight button 
        blank, #[12]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditDestinationLocation, DestinationLocation), # [13] DestinationLocation
                    'editbx','editfc' ), left=1, width=40),      
        urwid.AttrWrap(urwid.Divider("=", 1), 'bright'), #[14]
        urwid.Padding(urwid.Text(text_divider), left=20, right=2, min_width=20), #[15]
        urwid.AttrWrap(urwid.Divider("-", 0, 1), 'bright'), #[16]
        urwid.Padding(urwid.GridFlow(                           #17 submit button
            [urwid.AttrWrap(urwid.Button(txt, submit_button_press),
                'buttn','buttnf') for txt in submit_text_button_list],
            15, 3, 1, 'left'),
            left=27, right=3, min_width=13),
        blank,
        # urwid.Padding(urwid.GridFlow(
        #     [urwid.AttrWrap(urwid.Button(txt, ExitButton_Press),
        #         'buttn','buttnf') for txt in text_ExitButton],
        #     15, 3, 1, 'left'),
        #     left=27, right=3, min_width=20), 
        
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