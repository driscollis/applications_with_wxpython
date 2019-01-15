import wx

class CalcPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        buttons = ['C', '', '',  '/',
                   '7', '8', '9', 'X',
                   '4', '5', '6', '-',
                   '1', '2', '3', '+',
                   '.', '0', '=', '']
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        count = 1
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for button in buttons:
            size = (50, 50)
            if button:
                btn = wx.Button(self, label=button, size=size)
                btn.Bind(wx.EVT_BUTTON, self.on_button_press)
            else:
                btn = wx.StaticText(self, size=size)

            btn_sizer.Add(btn, 0, wx.ALL)

            if count == 4:
                main_sizer.Add(btn_sizer)
                btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
                count = 0
            count += 1

        self.SetSizer(main_sizer)

    def on_button_press(self, event):
        pass


class CalcFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title='wxCalculator')
        panel = CalcPanel(self)
        self.Show()


if __name__ == '__main__':
    app = wx.App(False)
    frame = CalcFrame()
    app.MainLoop()
