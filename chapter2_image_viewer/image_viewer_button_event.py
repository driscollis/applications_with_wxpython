# image_viewer_button_event.py

import wx

class ImagePanel(wx.Panel):

    def __init__(self, parent):
        super(ImagePanel, self).__init__(parent)

        img = wx.Image(240,240)
        self.image_ctrl = wx.StaticBitmap(self, 
                                          bitmap=wx.Bitmap(img))
        
        browse_btn = wx.Button(self, label='Browse')
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        
        self.photo_txt = wx.TextCtrl(self, size=(200, -1))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        main_sizer.Add(self.image_ctrl, 0, wx.ALL, 5)
        hsizer.Add(browse_btn, 0, wx.ALL, 5)
        hsizer.Add(self.photo_txt, 0, wx.ALL, 5)
        main_sizer.Add(hsizer, 0, wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        main_sizer.Fit(parent)
        self.Layout()
        
    def on_browse(self, event):
        """
        Browse for an image file
        @param event: The event object
        """
        wildcard = "JPEG files (*.jpg)|*.jpg"
        dialog = wx.FileDialog(None, "Choose a file",
                               wildcard=wildcard,
                               style=wx.ID_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.photo_txt.SetValue(dialog.GetPath())
        dialog.Destroy()


class MainFrame(wx.Frame):

    def __init__(self):
        super(MainFrame, self).__init__(None, title='Image Viewer')
        panel = ImagePanel(self)
        self.Show()


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.MainLoop()