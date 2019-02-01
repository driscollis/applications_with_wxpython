# image_viewer.py

import wx

class ImagePanel(wx.Panel):
    
    def __init__(self, parent, image_size):
        super().__init__(parent)
        
        img = wx.Image(*image_size)
        self.image_ctrl = wx.StaticBitmap(self, 
                                         bitmap=wx.Bitmap(img))
        browse_btn = wx.Button(self, label='Browse')
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.image_ctrl, 0, wx.ALL, 5)
        main_sizer.Add(browse_btn)
        self.SetSizer(main_sizer)
        main_sizer.Fit(parent)
        self.Layout()


class MainFrame(wx.Frame):
    
    def __init__(self):
        super().__init__(None, title='Image Viewer')
        panel = ImagePanel(self, image_size=(240,240))
        self.Show()


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.MainLoop()