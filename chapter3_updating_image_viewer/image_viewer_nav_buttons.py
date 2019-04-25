# image_viewer_nav_buttons.py

import glob
import os
import wx

class ImagePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.max_size = 240
        self.photos = []
        self.layout()

    def layout(self):
        """
        Layout the widgets on the panel
        """
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        img = wx.Image(self.max_size, self.max_size)
        self.image_ctrl = wx.StaticBitmap(self, wx.ID_ANY,
                                          wx.Bitmap(img))
        self.main_sizer.Add(self.image_ctrl, 0, wx.ALL|wx.CENTER, 5)
        self.image_label = wx.StaticText(self, label="")
        self.main_sizer.Add(self.image_label, 0, wx.ALL|wx.CENTER, 5)

        btn_data = [("Previous", btn_sizer, self.on_previous),
                    ("Slide Show", btn_sizer, self.on_slideshow),
                    ("Next", btn_sizer, self.on_next)]
        for data in btn_data:
            label, sizer, handler = data
            self.btn_builder(label, sizer, handler)

        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(self.main_sizer)

    def btn_builder(self, label, sizer, handler):
        """
        Builds a button, binds it to an event handler and adds it to a sizer
        """
        btn = wx.Button(self, label=label)
        btn.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)

    def on_next(self, event):
        pass

    def on_previous(self, event):
        pass

    def on_slideshow(self, event):
        pass

    def update_photo(self, image):
        """
        Update the currently shown photo
        """
        img = wx.Image(image, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.max_size
            NewH = self.max_size * H / W
        else:
            NewH = self.max_size
            NewW = self.max_size * W / H
        img = img.Scale(NewW, NewH)

        self.image_ctrl.SetBitmap(wx.Bitmap(img))
        self.Refresh()


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title='Image Viewer',
                         size=(400, 400))
        self.panel = ImagePanel(self)
        self.create_toolbar()
        self.Show()

    def create_toolbar(self):
        """
        Create a toolbar
        """
        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((16,16))

        open_ico = wx.ArtProvider.GetBitmap(
            wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16,16))
        openTool = self.toolbar.AddTool(
            wx.ID_ANY, "Open", open_ico, "Open an Image Directory")
        self.Bind(wx.EVT_MENU, self.on_open_directory, openTool)

        self.toolbar.Realize()

    def on_open_directory(self, event):
        """
        Open a directory dialog
        """
        with wx.DirDialog(self, "Choose a directory",
                          style=wx.DD_DEFAULT_STYLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.folder_path = dlg.GetPath()

                photos = glob.glob(os.path.join(self.folder_path, '*.jpg'))
                self.panel.photos = photos
                if photos:
                    self.panel.update_photo(photos[0])


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.MainLoop()