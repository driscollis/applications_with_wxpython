# template.py

import wx

class MyPanel(wx.Panel):
    
    def __init__(self, parent):
        super().__init__(parent)
        
class MyFrame(wx.Frame):
    
    def __init__(self):
        super().__init__(None, title='Template')
        panel = MyPanel(self)
        self.Show()
        
if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()