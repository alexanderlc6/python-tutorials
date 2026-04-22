from cProfile import label

import wx
# app = wx.App()
# frm = wx.Frame(None, title="Hello World", size=(400,300),pos =(100,100))
# frm.Show()
# app.MainLoop()

# Define my window
class MyFrame1(wx.Frame):
    def __init__(self):
        super().__init__(None, title='My own window', size = (400,300), pos = (100,100))
        panel = wx.Panel(parent=self)
        self.staticText = wx.StaticText(panel, label='Test label', pos=(10,10))
        btn = wx.Button(parent=panel, label='OK', pos=(100,50))
        self.Bind(wx.EVT_BUTTON, self.on_btn_click, btn)

        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.Add(self.staticText, proportion=1, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.FIXED_MINSIZE | wx.TOP, border=30)
        vBox.Add(btn, proportion=1, flag = wx.EXPAND|wx.BOTTOM, border=10)
        panel.SetSizer(vBox)

    def on_btn_click(self, event):
        self.staticText.SetLabelText('Changed me!')

class MyFrame2(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Cascade layout manager', size = (300,120))
        panel = wx.Panel(parent=self)
        self.staticText = wx.StaticText(panel, label='Click Me', pos=(10,10))
        btn1 = wx.Button(parent=panel, label='btn1', id = 10)
        btn2 = wx.Button(parent=panel, label='btn2', id = 11)

        hBox = wx.BoxSizer(wx.HORIZONTAL)
        hBox.Add(btn1, proportion=1, flag = wx.EXPAND|wx.ALL, border=10)
        hBox.Add(btn2, proportion=1, flag = wx.EXPAND|wx.ALL, border=10)

        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.Add(self.staticText, proportion=1, flag=wx.CENTER | wx.FIXED_MINSIZE | wx.TOP, border=10)
        vBox.Add(hBox, proportion=1, flag = wx.CENTER)
        panel.SetSizer(vBox)

        self.Bind(wx.EVT_BUTTON, self.on_btn_click, id = 10, id2 = 20)

    def on_btn_click(self, event):
        event_id = event.GetId()
        print(event_id)
        if event_id == 10:
            self.staticText.SetLabelText('Clicked btn1')
        else:
            self.staticText.SetLabelText('Clicked btn2')

class MyFrame3(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Text input control demo', size=(300, 260))
        panel = wx.Panel(parent=self)
        tc1 = wx.TextCtrl(panel)
        tc2 = wx.TextCtrl(panel, style= wx.TE_PASSWORD)
        tc3 = wx.TextCtrl(panel, style=wx.TE_MULTILINE)

        user_id = wx.StaticText(panel, label='User ID:')
        user_pwd = wx.StaticText(panel, label='Password:')
        content = wx.StaticText(panel, label='Content:')

        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.Add(user_id, flag=wx.EXPAND | wx.LEFT, border=10)
        vBox.Add(tc1, flag=wx.EXPAND | wx.ALL, border=10)
        vBox.Add(user_pwd, flag=wx.EXPAND | wx.LEFT, border=10)
        vBox.Add(tc2, flag=wx.EXPAND | wx.ALL, border=10)
        vBox.Add(content, flag=wx.EXPAND | wx.LEFT, border=10)
        vBox.Add(tc3, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vBox)
        tc1.SetValue('David')
        print('Read user ID:{0}'.format(tc1.GetValue()))

class MyFrame4(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Multi select demo', size=(500, 300))
        panel = wx.Panel(parent=self)
        st1 = wx.StaticText(panel, label='Select your favorite language:')
        cb1 = wx.CheckBox(panel, id = 1, label='Python')
        cb2 = wx.CheckBox(panel, id = 2, label='Java')
        cb2.SetValue(True)
        cb3 = wx.CheckBox(panel, id = 3, label='C++')
        self.Bind(wx.EVT_CHECKBOX, self.on_checkbox_click, id = 1, id2 = 3)

        hBox1 = wx.BoxSizer()
        hBox1.Add(st1, flag=wx.LEFT | wx.RIGHT, border=5)
        hBox1.Add(cb1)
        hBox1.Add(cb2)
        hBox1.Add(cb3)

        st2 = wx.StaticText(panel, label='Select your gender:')
        rd1 = wx.RadioButton(panel, id = 4, label='Male', style=wx.RB_GROUP)
        rd2 = wx.RadioButton(panel, id = 5, label='Female')
        self.Bind(wx.EVT_RADIOBUTTON, self.on_radioBtn_click, id = 4, id2 = 5)

        hBox2 = wx.BoxSizer()
        hBox2.Add(st2, flag=wx.LEFT | wx.RIGHT, border=5)
        hBox2.Add(rd1)
        hBox2.Add(rd2)

        st3 = wx.StaticText(panel, label='Select your course:')
        list1 = ['Science', 'Math', 'English']
        lb1 = wx.ListBox(panel, choices=list1, style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self.on_listBox1_click, lb1)

        hBox3 = wx.BoxSizer()
        hBox3.Add(st3, proportion=1, flag=wx.LEFT | wx.RIGHT, border=5)
        hBox3.Add(lb1, proportion=1)

        st4 = wx.StaticText(panel, label='Select your fruit:')
        list2 = ['Apple', 'Pear', 'Orange']
        lb2 = wx.ListBox(panel, choices=list2, style=wx.LB_EXTENDED)
        self.Bind(wx.EVT_LISTBOX, self.on_listBox2_click, lb2)

        hBox4 = wx.BoxSizer()
        hBox4.Add(st4, proportion=1, flag=wx.LEFT | wx.RIGHT, border=5)
        hBox4.Add(lb2, proportion=1)

        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.Add(hBox1, flag=wx.EXPAND | wx.ALL, border=5)
        vBox.Add(hBox2, flag=wx.EXPAND | wx.ALL, border=5)
        vBox.Add(hBox3, flag=wx.EXPAND | wx.ALL, border=5)
        vBox.Add(hBox4, flag=wx.EXPAND | wx.ALL, border=5)

        panel.SetSizer(vBox)

    def on_checkbox_click(self, event):
        # Event source object
        cb = event.GetEventObject()
        print('Chosen item:{0}, Status:{1}'.format(cb.GetLabel(), event.IsChecked()))

    def on_radioBtn_click(self, event):
        rb = event.GetEventObject()
        print('Chosen group item:{0}'.format(rb.GetLabel()))

    def on_listBox1_click(self, event):
        listbox = event.GetEventObject()
        print('Chosen item:{0}'.format(listbox.GetSelection()))

    def on_listBox2_click(self, event):
        listbox = event.GetEventObject()
        print('Chosen item:{0}'.format(listbox.GetSelection()))

class MyFrame5(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Switch images demo', size=(300, 300))
        self.panel = wx.Panel(parent=self)
        self.bmps = [wx.Bitmap('1.jpg', wx.BITMAP_TYPE_JPEG),
                     wx.Bitmap('2.jpg', wx.BITMAP_TYPE_JPEG),
                     wx.Bitmap('3.jpg', wx.BITMAP_TYPE_JPEG)]
        b1 = wx.Button(self.panel, id = 1, label='SwitchImg1')
        b2 = wx.Button(self.panel, id = 2, label='SwitchImg2')
        self.Bind(wx.EVT_BUTTON, self.on_btn_click, id = 1, id2 = 2)
        self.image = wx.StaticBitmap(self.panel, bitmap=self.bmps[0])
        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.Add(b1, flag=wx.CENTER | wx.ALL, border=10)
        vBox.Add(b2, flag=wx.CENTER | wx.ALL, border=10)
        vBox.Add(self.image, flag=wx.CENTER | wx.ALL, border=10)
        self.panel.SetSizer(vBox)

    def on_btn_click(self, event):
        event_id = event.GetId()
        if event_id == 1:
            self.image.SetBitmap(self.bmps[1])
        else:
            self.image.SetBitmap(self.bmps[2])
        self.panel.Layout()
app = wx.App()
# frm = MyFrame1()
# frm = MyFrame2()
# frm = MyFrame3()
# frm = MyFrame4()
frm = MyFrame5()
frm.Show()
app.MainLoop()