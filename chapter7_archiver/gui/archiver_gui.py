# archiver_gui.py

import controller

import os
import pathlib
import time
import wx

from ObjectListView import ObjectListView, ColumnDefn


class Items:

    def __init__(self, path, name, size, item_type,
                 modified):
        self.path = path
        self.name = name
        self.size = size
        self.item_type = item_type
        self.modified = modified


class DropTarget(wx.FileDropTarget):

    def __init__(self, window):
        super().__init__()
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        self.window.update_display(filenames)
        return True

class ArchivePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)
        drop_target = DropTarget(self)
        self.SetDropTarget(drop_target)
        self.archive_items = []
        paths = wx.StandardPaths.Get()
        self.current_directory = paths.GetDocumentsDir()

        # Create sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create input widget
        self.archive_olv = ObjectListView(
            self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.archive_olv.SetEmptyListMsg("Add Files / Folders here")

        self.update_archive()
        main_sizer.Add(self.archive_olv, 1, wx.ALL|wx.EXPAND, 5)
        # Create output related widgets
        label = wx.StaticText(self, label='File name:')
        label.SetFont(font)
        h_sizer.Add(label, 0, wx.CENTER)
        self.archive_filename = wx.TextCtrl(self)
        h_sizer.Add(self.archive_filename, 1, wx.EXPAND)
        self.archive_types = wx.ComboBox(
            self, value='Tar',
            choices=['Tar'],
            size=(75, -1))
        h_sizer.Add(self.archive_types, 0)
        main_sizer.Add(h_sizer, 0, wx.EXPAND|wx.ALL, 5)

        # Create archive button
        create_archive_btn = wx.Button(self, label='Create Archive')
        create_archive_btn.Bind(wx.EVT_BUTTON, self.on_create_archive)
        main_sizer.Add(create_archive_btn, 0, wx.ALL|wx.CENTER, 5)

        self.SetSizer(main_sizer)

    def on_create_archive(self, event):
        if not self.archive_olv.GetObjects():
            self.show_message('No files / folders to archive',
                              'Error', wx.ICON_ERROR)
            return

        if not self.archive_filename.GetValue():
            self.show_message('File name is required!',
                              'Error', wx.ICON_ERROR)
            return

        with wx.DirDialog(
            self, "Choose a directory:",
            style=wx.DD_DEFAULT_STYLE,
            defaultPath=self.current_directory) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                self.current_directory = path
                archive_filename = self.archive_filename.GetValue()
                archive_type = self.archive_types.GetValue()

                full_save_path = pathlib.Path(
                    path, '{filename}.{type}'.format(
                        filename=archive_filename,
                        type=archive_type.lower()
                    ))
                controller.create_archive(
                    full_save_path,
                    self.archive_olv.GetObjects(),
                    archive_type)
                message = f'Archive created at {full_save_path}'
                self.show_message(message, 'Archive Created',
                                  wx.ICON_INFORMATION)

    def update_archive(self):
        self.archive_olv.SetColumns([
                            ColumnDefn("Name", "left", 100, "name"),
                            ColumnDefn("Path", "left", 350, "path"),
                            ColumnDefn("Size", "left", 75, "size"),
                            ColumnDefn("Type", "right", 75, "item_type"),
                            ColumnDefn("Modified", "left", 150, "modified")
                        ])
        self.archive_olv.SetObjects(self.archive_items)

    def update_display(self, items):
        paths = [pathlib.Path(item) for item in items]
        for path in paths:
            basename = path.name
            size = self.get_size(path)
            if path.is_dir():
                item_type = 'folder'
            else:
                item_type = 'file'
            last_modified = time.ctime(path.stat().st_mtime)
            item = Items(path, basename, size, item_type,
                         last_modified)
            self.archive_items.append(item)

        self.update_archive()

    def get_size(self, path):
        size = path.stat().st_size

        suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
        index = 0
        while size > 1024:
            index += 1
            size = size / 1024.0

        suffix = suffixes[index]
        return f'{size:.1f} {suffix}'

    def show_message(self, message, caption, flag=wx.ICON_ERROR):
        """
        Show a message dialog
        """
        msg = wx.MessageDialog(None, message=message,
                               caption=caption, style=flag)
        msg.ShowModal()
        msg.Destroy()


class MainFrame(wx.Frame):

    def __init__(self):
        """Constructor"""
        super().__init__(
            None, title="PyArchiver",
            size=(800, 600))
        self.panel = ArchivePanel(self)

        self.Show()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
