import eyed3
import glob
import wx

from ObjectListView import ObjectListView, ColumnDefn

class Mp3:

    def __init__(self, artist, album, title, id3):
        self.artist = artist
        self.album = album
        self.title = title
        self.id3 = id3


class TaggerPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.mp3s = []
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.mp3_olv = ObjectListView(
            self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.mp3_olv.SetEmptyListMsg("No Mp3s Found")
        self.update_mp3_info()
        main_sizer.Add(self.mp3_olv, 1, wx.ALL | wx.EXPAND, 5)

        edit_btn = wx.Button(self, label='Edit Mp3')
        edit_btn.Bind(wx.EVT_BUTTON, self.edit_mp3)
        main_sizer.Add(edit_btn, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(main_sizer)

    def edit_mp3(self, event):
        pass

    def load_mp3s(self, path):
        mp3_paths = glob.glob(path + '/*.mp3')
        for mp3_path in mp3_paths:
            id3 = eyed3.load(mp3_path)
            mp3_obj = Mp3(id3.tag.artist, id3.tag.album, id3.tag.title, id3)
            self.mp3s.append(mp3_obj)
        self.update_mp3_info()

    def update_mp3_info(self):
        self.mp3_olv.SetColumns([
        ColumnDefn("Artist", "left", 100, "artist"),
                ColumnDefn("Album", "left", 100, "album"),
                ColumnDefn("Title", "left", 150, "title")
        ])
        self.mp3_olv.SetObjects(self.mp3s)


class TaggerFrame(wx.Frame):

    def __init__(self):
        super().__init__(
            None, title="Mp3 Tag Editor")
        self.panel = TaggerPanel(self)
        self.create_menu()
        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        open_folder_menu_item = file_menu.Append(
            wx.ID_ANY, 'Open Mp3 Folder', 'Open a folder with MP3s'
        )
        menu_bar.Append(file_menu, '&File')
        self.Bind(wx.EVT_MENU, self.on_open_folder,
                  open_folder_menu_item)
        self.SetMenuBar(menu_bar)

    def on_open_folder(self, event):
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE,
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.panel.load_mp3s(dlg.GetPath())
        dlg.Destroy()


if __name__ == '__main__':
    app = wx.App(False)
    frame = TaggerFrame()
    app.MainLoop()