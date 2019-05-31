import urwid
import urwid.raw_display
import urwid.web_display
import socket
import pyodbc 

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
global Cleared
Cleared = ""

def main(): 
    
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
         
    def CollectCode(bincodeindex):
        listbox.set_focus(bincodeindex)
        _, boxText = listbox.get_focus() 
        code = listbox_content[boxText].original_widget.base_widget._edit_text
        return code
    
    def ResetCode(codeindex): #make this iterate through a list of Bin indexes clearing out all if one does not meet bin# conditions (num or blank)
        listbox.set_focus(codeindex-1) #here because directly going to the 3rd field clears the value, but does not update the graphic
        listbox.set_focus(codeindex)
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(Cleared) 

    def ResetWeight(): 
        listbox.set_focus(11) 
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(Cleared)  
        
    text_header = (u"Molded Part Weight Utility. / for UP  * for DOWN.  Period Key exits.") #adjust this per keypad
    text_intro = [(
        u" Enter information into all fields"
        u" before submitting.")]  
    textEditBinCode = ('editcp', u"Bin Code: ")
    textEditWipNum = ('editcp', u"Part Num: ")
    textEditBinCode1 = ('editcp', u"Bin Code: ")
    textEditBinCode2 = ('editcp', u"Bin Code: ")
    textEditWeight = ('editcp', u"Total Bin Weight: ")  
    text_WeightButton = [u"Update Weight"]
    def WeightButton_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'button')
        listbox.set_focus(11) #11 sets focus on listbox index of the weight text
        global Weight 
        Weight = CollectWeight() 
        _, boxText = listbox.get_focus() 
        am = listbox_content[boxText].original_widget 
        am.set_edit_text(Weight) 
    
    text_divider =  [u"Press SUBMIT to insert data and reset."]

    submit_text_button_list = [u"SUBMIT"]
    def submit_button_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'header')
        ScanCode0 = CollectCode(5) 
        ScanCode1 = CollectCode(7)
        ScanCode2 = CollectCode(9)
        WipNum = CollectCode(3)
        EmpId = 'xxxx'
        FilledBinWeight = Weight
        if (len(ScanCode0) != 5):
            ResetCode(5)
        elif (len(ScanCode1) != 5):
            ResetCode(7)
        elif (len(ScanCode2) != 5):
            ResetCode(9)   
        elif (len(WipNum) != 12):
            ResetCode(3)       
        elif ((len(Weight)) < 5) or ((len(Weight)) >= 8):
            ResetCode(11)
        else:       
            conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};' # to get this driver working had to install mssqltools msft package
                                'Server=NEWMAS;'
                                'Database=FloorLocations;'
                                'uid=SA;pwd=AA734248pass;'
                                )
            conn.autocommit = True
            cursor = conn.cursor() 
            #below, the @PartNum parameter had to be escaped with [] for hyphens to correctly pass through
            cursor.execute("EXEC dbo.ABW_WIP_BinInsert @EmpID = {}, @FilledBinWeight = {}, @PartNum = [{}], @ScanCode0 = {}, @ScanCode1 = {}, @ScanCode2 = {} ".format(EmpId,FilledBinWeight,WipNum,ScanCode0,ScanCode1,ScanCode2))
            conn.close()                    
            #clear weight,Scancode, WIP #
            ResetWeight()
            ResetCode(5)
            ResetCode(7)
            ResetCode(9)
            ResetCode(11)
            ResetCode(3)
   
    #index numbers for reference    
    blank = urwid.Divider()
    listbox_content = [
        blank, #[0]
        urwid.Padding(urwid.Text(text_intro), left=2, right=2, min_width=20), #[1]
        blank, #[2] 
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditWipNum, WipNum), # [3] wipnum
            'editbx','editfc' ), left=10, width=24),
        blank, #[4]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode, ScanCode0), # [5] bincode
            'editbx','editfc' ), left=10, width=22),
        blank, #[6]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode1, ScanCode1), # [7] bincode1
            'editbx','editfc' ), left=10, width=22),
        blank, #[8]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditBinCode2, ScanCode2), #[9] bincode2
            'editbx','editfc' ), left=10, width=22),
        blank, #[10]
        urwid.Padding(urwid.AttrWrap(urwid.Edit(textEditWeight, Weight), # [11] weight
            'editbx','editfc' ), left=5, width=30),
        blank, #[12]
        urwid.Padding(urwid.GridFlow(
            [urwid.AttrWrap(urwid.Button(txt, WeightButton_press),
                'buttn','buttnf') for txt in text_WeightButton],
            10, 3, 1, 'left'),
            left=17, right=3, min_width=13), #[13]
        blank, #[14]        
        urwid.AttrWrap(urwid.Divider("=", 1), 'bright'),
        urwid.Padding(urwid.Text(text_divider), left=2, right=2, min_width=20),
        urwid.AttrWrap(urwid.Divider("-", 0, 1), 'bright'),
        urwid.Padding(urwid.GridFlow(
            [urwid.AttrWrap(urwid.Button(txt, submit_button_press),
                'buttn','buttnf') for txt in submit_text_button_list],
            15, 3, 1, 'left'),
            left=15, right=3, min_width=13),
        blank,
        
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