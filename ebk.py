import urwid
import urwid.raw_display
import urwid.web_display
import socket
import pyodbc 
from SQLServerClasses import SQLServerFunctions
#from dotenv import load_dotenv
#load_dotenv()
#import os

class MyBox(urwid.ListBox):

    def keypress(self, size, key): 
        if key == '/':
            key = 'up'
        if key == '+':
            key = 'down'
        if key == 'f8':
            raise urwid.ExitMainLoop()
        super().keypress(size, key) 
   
global ScanCode
ScanCode = ''
global BinType
BinType = ''
global Weight
Weight = ''
global ClearedWeight
ClearedWeight = ''
global Cleared
Cleared = ""
global ScaleCode
ScaleCode = ''

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
            return('800.01')
            #return('SktCnctErr!')
        
    def CollectCode(binCodeIndex):
        listbox.set_focus(binCodeIndex)
        _, boxText = listbox.get_focus() 
        code = listbox_content[boxText].original_widget.base_widget._edit_text
        return code
    
    def ResetCode(codeindex): 
        listbox.set_focus(codeindex-1) #need to hop around here - directly focusing to the 3rd field clears the value, but does not update the graphic
        listbox.set_focus(codeindex)
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(Cleared) 
        

    def ResetWeight():
        listbox.set_focus(10) 
        global ClearedWeight
        ClearedWeight = ""
        global Weight
        Weight = ""
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(ClearedWeight) 
    
    text_header = (u"Empty Bin Weight Application. / for UP  + for DOWN.") 
    text_intro = [(
        u" Enter information into all fields"
        u" before  submitting.")]
    text_bintypes = [(
        u" 1 = Flat Bin | 2 = Wheel Bin |"
        u" 3 = Plastic Bin | 4 = Gaylord")]    
    textEditBinCode = ('editcp', u"Bin Code: ")
    textEditBinType = ('editcp', u"Bin Type: ")
    textEditScaleCode = ('editcp', u"Scale Code : ")
    textEditWeight = ('editcp', u"Bin Weight: ")  
    text_WeightButton = [u"Update Weight"]
    text_ExitButton = [u"Exit Application"]
    def WeightButton_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'button')
        listbox.set_focus(10) 
        global Weight 
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        Weight = '800.01'
        #Weight = CollectWeight(ScaleCode) 
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(Weight) 
    
    text_divider =  [u"Select bin condition to submit entry."]

    acceptable_text_button_list = [u"Acceptable"]
    def acceptable_button_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'header')
        ScanCode = CollectCode(3) 
        binType = CollectCode(5)
        scaleIp = CollectCode(8)
        emptyWeight = Weight
        SqlFunctions = SQLServerFunctions()
        Condition = 'acceptable'
        if binType not in ['1','2','3','4']:
            ResetCode(5)
        elif (len(ScanCode) != 5):
            ResetCode(3)
        elif ((len(emptyWeight)) < 5) or ((len(emptyWeight)) >= 8): 
            ResetWeight()
        else:
            SqlFunctions.SubmitCondition(emptyWeight,ScanCode,Condition,binType,scaleIp)
            ResetWeight()
            for i in [10,5,8,3]:
                ResetCode(i)
            Condition=''
    damaged_text_button_list = [u"Damaged"]
    def damaged_button_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'header')
        ScanCode = CollectCode(3) 
        binType = CollectCode(5)
        scaleIp = CollectCode(8)
        emptyWeight = Weight 
        SqlFunctions = SQLServerFunctions()
        Condition = 'damaged'
        if binType not in ['1','2','3','4']:
            ResetCode(5)
        elif (len(ScanCode) != 5):
            ResetCode(3)
        elif ((len(Weight)) < 5) or ((len(Weight)) >= 8):
            ResetWeight()
        else:
            SqlFunctions.SubmitDamaged(emptyWeight,ScanCode,Condition,binType,scaleIp)
            ResetWeight()
            for i in [10,5,8,3]:
                ResetCode(i)
            Condition=''
    
    def ExitButton_Press(button):
        raise urwid.ExitMainLoop()

    blank = urwid.Divider()
    listbox_content = [
        blank, #0
        urwid.Padding(urwid.Text(text_intro), left=2, right=2, min_width=20), #1
        blank, #2
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode, ScanCode), #3 bincode 
            'editbx','editfc' ), left=10, width=20),
        blank,#4

        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinType, BinType), #5 bintype
            'editbx','editfc' ), left=10, width=20),
        
        urwid.Padding(urwid.Text(text_bintypes), left=2, right=2, min_width=20), #6 bin types description

        blank, #7
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditScaleCode, ScaleCode), #8 Scale ip address
            'editbx','editfc' ), left=10, width=31),
        blank,#9

        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditWeight, Weight), #10 weight
            'editbx','editfc' ), left=10, width=20),
        blank, 
        urwid.Padding(urwid.GridFlow(
            [urwid.AttrWrap(urwid.Button(txt, WeightButton_press),
                'buttn','buttnf') for txt in text_WeightButton],
            10, 3, 1, 'left'),
            left=20, right=3, min_width=13),
        urwid.AttrWrap(urwid.Divider("=", 1), 'bright'),
        urwid.Padding(urwid.Text(text_divider), left=2, right=2, min_width=20),
        urwid.AttrWrap(urwid.Divider("-", 0, 1), 'bright'),
        urwid.Padding(urwid.GridFlow(
            [urwid.AttrWrap(urwid.Button(txt, acceptable_button_press),
                'buttn','buttnf') for txt in acceptable_text_button_list],
            15, 3, 1, 'left'),
            left=15, right=3, min_width=13),
        urwid.Padding(urwid.GridFlow(
            [urwid.AttrWrap(urwid.Button(txt, damaged_button_press),
                'buttn','buttnf') for txt in damaged_text_button_list],
            13, 3, 1, 'left'),
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
