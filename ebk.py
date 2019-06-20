import urwid
import urwid.raw_display
import urwid.web_display
import socket
import pyodbc 
from dotenv import load_dotenv
load_dotenv()
import os
#new test comment 6/20/2019
#ayyee
#assign key remappings here, this overrides the keypress method of urwid.ListBox
class MyBox(urwid.ListBox):

    def keypress(self, size, key): 
        if key == '/':
            key = 'up'
        if key == '*':
            key = 'down'
        if key == 'f8':
            raise urwid.ExitMainLoop()
        if key == '.':
            raise urwid.ExitMainLoop()
        super().keypress(size, key) 
   
global ScanCode
ScanCode = ''

global Weight
Weight = ''

global ClearedWeight
ClearedWeight = ''

def main(): 
    print(os.getenv("NEWMAS_DB_PASS"))
    #makes scale connection, grabs the weight, and closes the connection.
    def CollectWeight():
        s = socket.socket()
        s.settimeout(2)
        port = 23
        try:
            s.connect(('10.79.3.33', 23))
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
        
    
    
    def CollectCode():
        listbox.set_focus(3)
        _, boxText = listbox.get_focus() 
        code = listbox_content[boxText].original_widget.base_widget._edit_text
        return code
    
    def ResetCode():
        listbox.set_focus(2) #need to hop around here - directly focusing to the 3rd field clears the value, but does not update the graphic
        listbox.set_focus(3)
        _, boxText = listbox.get_focus() 
        listbox_content[boxText].original_widget.base_widget._edit_text = ""
        

    def ResetWeight():
        listbox.set_focus(4) 
        global ClearedWeight
        ClearedWeight = ""
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(ClearedWeight) 
    
    text_header = (u"Empty Bin Weight Utility. / for UP  * for DOWN.  Period Key exits.") #adjust this per keypad
    text_intro = [(
        u" Enter information into all fields"
        u" before  mitting.")]  
    textEditBinCode = ('editcp', u"Bin Code: ")
    textEditWeight = ('editcp', u"Bin Weight: ")  
    
    text_WeightButton = [u"Update Weight"]
    def WeightButton_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'button')
        listbox.set_focus(4) #4 sets focus on listbox index of the weight text
        global Weight 
        Weight = CollectWeight() 
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(Weight) 
    
    text_divider =  [u"Select bin condition to submit entry."]

    acceptable_text_button_list = [u"Acceptable"]
    def acceptable_button_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'header')
        ScanCode = CollectCode() 
        emptyWeight = Weight
        if (len(ScanCode) != 5):
            ResetCode()
        elif ((len(Weight)) < 5) or ((len(Weight)) >= 8):
            ResetWeight()
        else:
            Condition = 'acceptable'
            conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=%s;TDS_Version=7.4' % os.getenv("NEWMAS_DB_PASS")) 
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("EXEC dbo.ABW_EmptyBinWeightsInsert @emptyweight = {}, @scancode = {}, @condition = {}".format(emptyWeight,ScanCode,Condition))
            conn.commit()
            conn.close()
            #clear weight,Scancode, condition
            ResetWeight()
            ResetCode()
            Condition=''
    damaged_text_button_list = [u"Damaged"]
    def damaged_button_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'header')
        ScanCode = CollectCode()
        emptyWeight = Weight 
        if (len(ScanCode) != 5):
            ResetCode()
        elif ((len(Weight)) < 5) or ((len(Weight)) >= 8):
            ResetWeight()
        else:
            Condition = 'damaged'
            conn = pyodbc.connect('DSN=NAME1;UID=sa;PWD=%s;TDS_Version=7.4' % os.getenv("NEWMAS_DB_PASS"))
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("EXEC dbo.ABW_EmptyBinWeightsInsert @emptyweight = {}, @scancode = {}, @condition = {}".format(emptyWeight,ScanCode,Condition))
            conn.commit()
            conn.close()
            #clear weight,Scancode, condition
            ResetWeight()
            ResetCode()
            Condition=''

    
    blank = urwid.Divider()
    listbox_content = [
        blank,
        urwid.Padding(urwid.Text(text_intro), left=2, right=2, min_width=20),
        blank,
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode, ScanCode), #bincode
            'editbx','editfc' ), left=10, width=20),
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditWeight, Weight), #weight
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
