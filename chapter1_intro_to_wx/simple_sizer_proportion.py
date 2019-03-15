# simple_sizer_proportion.py

import wx


class MyPanel(wx.Panel):

    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)

        button = wx.Button(self, label='Press Me')

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(button, proportion=1, flag=wx.ALL | wx.CENTER, border=5)
        self.SetSizer(main_sizer)


class MyFrame(wx.Frame):

    def __init__(self):
        super(MyFrame, self).__init__(None, title='Hello World')
        panel = MyPanel(self)
        self.Show()


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MyFrame()
    app.MainLoop()