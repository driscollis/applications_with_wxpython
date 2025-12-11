import controller
import wx


class CipherPanel(wx.Panel):
    """"""


    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        choices = ["", "Alpha2Num", "ASCII", "L33t", "Hex"]
        decode_choices = ["", "ASCII", "Hex", "Num2Alpha"]
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)

        toLbl = wx.StaticText(self, label="Translate into:")
        self.toCbo = wx.ComboBox(self, value=choices[1], choices=choices)
        self.add2HSizer([toLbl, self.toCbo])

        fromLbl = wx.StaticText(self, label="Translate from:")
        self.fromCbo = wx.ComboBox(self, value="", choices=decode_choices)
        self.add2HSizer([fromLbl, self.fromCbo])

        txtLbl = wx.StaticText(self, label="Enter text to encode or decode:")
        self.originalTxt = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        self.translatedTxt = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        encodeBtn = wx.Button(self, label="Encode")
        encodeBtn.Bind(wx.EVT_BUTTON, self.onEncode)
        decodeBtn = wx.Button(self, label="Decode")
        decodeBtn.Bind(wx.EVT_BUTTON, self.onDecode)

        # layout widgets
        self.mainSizer.Add(txtLbl, 0, wx.ALL, 5)
        self.mainSizer.Add(self.originalTxt, 1, wx.EXPAND|wx.ALL, 5)
        self.mainSizer.Add(self.translatedTxt, 1, wx.EXPAND|wx.ALL, 5)
        self.add2HSizer([encodeBtn, decodeBtn])

        self.SetSizer(self.mainSizer)


    def add2HSizer(self, widgets):
        """
        Add widgets to a horizontal sizer
        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for widget in widgets:
            sizer.Add(widget, 0, wx.ALL|wx.CENTER, 5)

        if isinstance(widgets[0], wx.Button):
            self.mainSizer.Add(sizer, 0, wx.CENTER)
        else:
            self.mainSizer.Add(sizer)


    def onDecode(self, event):
        """
        Decodes what's in the original text box to the encoding
        specified and puts the result in the bottom text box
        """
        from_value = self.fromCbo.GetValue()
        value_to_decode = self.originalTxt.GetValue()
        if from_value == "Hex":
            new_value = value_to_decode.decode("hex")
        elif from_value == "ASCII":
            value_to_decode = [int(i) for i in value_to_decode.split()]
            new_value = controller.convertFromASCII(value_to_decode)
        elif from_value == "Num2Alpha":
            value_to_decode = value_to_decode.split()
            new_value = controller.convertFromNumbers(value_to_decode)
        else:
            return

        self.translatedTxt.SetValue(new_value)


    def onEncode(self, event):
        """
        Encodes what's in the original text box to the encoding
        specified and puts the result in the bottom text box
        """
        to_value = self.toCbo.GetValue()
        value_to_encode = self.originalTxt.GetValue()
        if to_value == "Hex":
            new_value = value_to_encode.encode("hex")
        elif to_value == "ASCII":
            new_value = controller.convertToASCII(value_to_encode)
        elif to_value == "L33t":
            new_value = controller.convertToLeet(value_to_encode)
        elif to_value == "Alpha2Num":
            new_value = controller.convertToNumbers(value_to_encode)

        self.translatedTxt.SetValue(new_value)


class CipherFrame(wx.Frame):
    """"""

    def __init__(self):
        title = "Cipher Creator / Translator"
        size = (800,600)
        wx.Frame.__init__(self, None, title=title, size=size)
        panel = CipherPanel(self)
        self.Show()

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = CipherFrame()
    app.MainLoop()