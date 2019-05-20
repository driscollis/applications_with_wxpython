# CR0103_hello_with_classes_super.py

import wx


class MyFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title='Hello World')
        self.Show()


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MyFrame()
    app.MainLoop()