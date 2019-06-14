# main.py

import eyed3
import editor
import glob
import os
import wx

from ObjectListView import ObjectListView, ColumnDefn

class Mp3:

    def __init__(self, id3):
        self.artist = ''
        self.album = ''
        self.title = ''
        self.year = ''

        # Attempt to extract MP3 tags
        if not isinstance(id3.tag, type(None)):
            id3.tag.artist = self.normalize_mp3(
                id3.tag.artist)
            self.artist = id3.tag.artist
            id3.tag.album = self.normalize_mp3(
                id3.tag.album)
            self.album = id3.tag.album
            id3.tag.title = self.normalize_mp3(
                id3.tag.title)
            self.title = id3.tag.title
            if hasattr(id3.tag, 'best_release_date'):
                if not isinstance(
                    id3.tag.best_release_date, type(None)):
                    self.year = self.normalize_mp3(
                        id3.tag.best_release_date.year)
                else:
                    id3.tag.release_date = 2019
                    self.year = self.normalize_mp3(
                        id3.tag.best_release_date.year)
        else:
            tag = id3.initTag()
            tag.release_date = 2019
            tag.artist = 'Unknown'
            tag.album = 'Unknown'
            tag.title = 'Unknown'
        self.id3 = id3
        self.update()

    def normalize_mp3(self, tag):
        try:
            if tag is not None:
                return tag
            else:
                return 'Unknown'
        except:
            return 'Unknown'

    def update(self):
        self.artist = self.id3.tag.artist
        self.album = self.id3.tag.album
        self.title = self.id3.tag.title
        self.year = self.id3.tag.best_release_date.year


class DropTarget(wx.FileDropTarget):

    def __init__(self, window):
        super().__init__()
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        self.window.update_on_drop(filenames)
        return True


class TaggerPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.mp3s = []
        drop_target = DropTarget(self)
        self.SetDropTarget(drop_target)
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

    def add_mp3(self, path):
        id3 = eyed3.load(path)
        mp3_obj = Mp3(id3)
        self.mp3s.append(mp3_obj)

    def edit_mp3(self, event):
        selection = self.mp3_olv.GetSelectedObject()
        if selection:
            with editor.Mp3TagEditorDialog(selection) as dlg:
                dlg.ShowModal()
                self.update_mp3_info()

    def find_mp3s(self, folder):
        mp3_paths = glob.glob(folder + '/*.mp3')
        for mp3_path in mp3_paths:
            self.add_mp3(mp3_path)

    def load_mp3s(self, path):
        if self.mp3s:
            # clear the current contents
            self.mp3s = []
        self.find_mp3s(path)
        self.update_mp3_info()

    def update_on_drop(self, paths):
        for path in paths:
            _, ext = os.path.splitext(path)
            if os.path.isdir(path):
                self.load_mp3s(path)
            elif os.path.isfile(path) and ext.lower() == '.mp3':
                self.add_mp3(path)
                self.update_mp3_info()

    def update_mp3_info(self):
        self.mp3_olv.SetColumns([
            ColumnDefn("Artist", "left", 100, "artist"),
            ColumnDefn("Album", "left", 100, "album"),
            ColumnDefn("Title", "left", 150, "title"),
            ColumnDefn("Year", "left", 100, "year")
        ])
        self.mp3_olv.SetObjects(self.mp3s)


class TaggerFrame(wx.Frame):

    def __init__(self):
        super().__init__(
            None, title="Serpent - MP3 Editor")
        self.panel = TaggerPanel(self)
        self.create_menu()
        self.create_tool_bar()
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

    def create_tool_bar(self):
        self.toolbar = self.CreateToolBar()

        add_folder_ico = wx.ArtProvider.GetBitmap(
            wx.ART_FOLDER_OPEN, wx.ART_TOOLBAR, (16, 16))
        add_folder_tool = self.toolbar.AddTool(
            wx.ID_ANY, 'Add Folder', add_folder_ico,
            'Add a folder to be archived')
        self.Bind(wx.EVT_MENU, self.on_open_folder,
                  add_folder_tool)
        self.toolbar.Realize()

    def on_open_folder(self, event):
        with wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE,
                          ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.panel.load_mp3s(dlg.GetPath())


if __name__ == '__main__':
    app = wx.App(False)
    frame = TaggerFrame()
    app.MainLoop()