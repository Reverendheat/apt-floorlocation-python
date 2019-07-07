import urwid
import urwid.raw_display
import urwid.web_display
import socket
import pyodbc

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
global ScaleCode
ScaleCode = ''
global Cleared
Cleared = ""
global binFound
binFound = ''



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
        listbox.set_focus(11) #index
        _, boxText = listbox.get_focus()
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(text)
        global Weight
        Weight = ''
        


    text_header = (u"Weigh Later Application. / for UP  + for DOWN.") #adjust this per keypad


    textEditBinCode = ('editcp', u"Bin Code: ")
    textBinFound = ('editcp', u"")
    text_bintypes = [(
        u" 1 = Flat Bin | 2 = Wheel Bin |"
        u" 3 = Plastic Bin | 4 = Gaylord")]
    textEditBinType = ('editcp', u"Bin Type: ")
    textEditScaleCode = ('editcp', u"Scale Code : ")
    textEditWeight = ('editcp', u"Bin Weight: ")  
    text_enterDash = [u""]
    text_WeightButton = [u"Update Weight From Scale"]
    text_ExitButton = [u"Exit Application"]

    def WeightButton_press(button):
        ScaleCode = CollectCode(9) #index
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'button')
        listbox.set_focus(11) #index
        global Weight
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        Weight = '800.01'
        #Weight = CollectWeight(ScaleCode) 
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(Weight)

    check_button_list = [u"Find Bin"]
    def check_button_press(button):
        binCode = CollectCode(3) #index
        checkBoxText = ''
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'button')
        listbox.set_focus(7) #index
        SqlFunctions = SQLServerFunctions()
        isBinValid= SqlFunctions.WeighLaterTest(binCode)
        if isBinValid == True:
            checkBoxText = 'Bin Found'
        elif isBinValid == False:
            checkBoxText = 'Bin not Found'
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(checkBoxText)
        
    
    text_divider =  [u"Press SUBMIT to insert data and reset."]

    submit_text_button_list = [u"SUBMIT"]
    def submit_button_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'header')
        SqlFunctions = SQLServerFunctions()
        ScaleIp = CollectCode(9)
        ScanCode0 = CollectCode(3) 
        isBinValid= SqlFunctions.WeighLaterTest(ScanCode0)
        
        global Weight
        FilledBinWeight = Weight      
        manualEntry = CollectCode(11)

        if FilledBinWeight == '' or (len(manualEntry) > 0):
            FilledBinWeight = manualEntry

        elif (len(ScanCode0) != 5): #must be at least one bin
            ResetCode(3)
        elif isBinValid != True:
            ResetCode(3)
        elif ((len(FilledBinWeight)) < 1): 
            ResetCode(11)
        else:
            SqlFunctions.UpdateWipBin(ScanCode0,FilledBinWeight)               
            #clear weight,Scancode, WIP #
            for i in [7,9,11,3]:
                ResetCode(i)
            FilledBinWeight = ''
            Weight = ''
            
    def ExitButton_Press(button):
        raise urwid.ExitMainLoop()
            
   
    #index numbers for reference []
    blank = urwid.Divider()
    listbox_content = [
        blank, #[0]
        blank, #[1]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode, ScanCode0), # [3] bincode0
            'editbx','editfc' ), left=10, width=22),
        blank, #[4]
         urwid.Padding(urwid.GridFlow(                           # [5] Find Bin button
            [urwid.AttrWrap(urwid.Button(txt, check_button_press),
                'buttn','buttnf') for txt in check_button_list],
            15, 3, 1, 'left'),
            left=15, right=3, min_width=13),
        blank, #[6]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textBinFound, binFound), #[7] Bin found text
            'editbx','editfc' ), left=15, width=15),
        blank, #[8]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditScaleCode, ScaleCode), #[9] ScaleCode
            'editbx','editfc' ), left=10, width=31),
        blank, #[10]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditWeight, Weight), # [11] weight
            'editbx','editfc' ), left=5, width=36),
        urwid.Padding(urwid.Text(text_enterDash), left=2, right=2, min_width=20), #[12] enter dash text line - this is just blank
        urwid.Padding(urwid.GridFlow(           #[13] weight button
            [urwid.AttrWrap(urwid.Button(txt, WeightButton_press),
                'buttn','buttnf') for txt in text_WeightButton],
            20, 3, 1, 'left'),
            left=12, right=3, min_width=20),  
        blank, #[14]
        urwid.Padding(urwid.GridFlow(                           #[15] submit button
            [urwid.AttrWrap(urwid.Button(txt, submit_button_press),
                'buttn','buttnf') for txt in submit_text_button_list],
            15, 3, 1, 'left'),
            left=15, right=3, min_width=13),
        blank, #16]
        urwid.Padding(urwid.GridFlow( #[17] exit button
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