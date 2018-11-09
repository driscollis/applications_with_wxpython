# event_hierarchy.py

import wx


class MyPanel(wx.Panel):
    
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)
        
        button = wx.Button(self, label='Press Me')
        self.Bind(wx.EVT_BUTTON, self.frame_button_handler, button)
        button.Bind(wx.EVT_BUTTON, self.on_button_press)
        
    def frame_button_handler(self, event):
        print('frame_button_handler called')
        
    def on_button_press(self, event):
        print('on_button_press called')
        event.Skip()

class MyFrame(wx.Frame):
    
    def __init__(self):
        super(MyFrame, self).__init__(None, title='Hello World')
        panel = MyPanel(self)
        self.Show()


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MyFrame()
    app.MainLoop()