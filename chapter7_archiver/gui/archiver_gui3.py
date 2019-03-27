# archiver_gui3.py

import controller

import os
import pathlib
import time
import wx
import wx.lib.agw.multidirdialog as MDD

from ObjectListView import ObjectListView, ColumnDefn

open_wildcard = "All files (*.*)|*.*"


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

        # Create iinput widget
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
            archive_filename = self.archive_filename.GetValue()
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                self.current_directory = path
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
        self.create_menu()
        self.create_toolbar()

        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('Welcome to PyArchiver!')

        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()

        # Create file menu
        file_menu = wx.Menu()

        exit_menu_item = file_menu.Append(
            wx.ID_ANY, "Exit",
            "Exit the application")
        menu_bar.Append(file_menu, '&File')
        self.Bind(wx.EVT_MENU, self.on_exit,
                  exit_menu_item)

        # Create edit menu
        edit_menu = wx.Menu()

        add_file_menu_item = edit_menu.Append(
            wx.ID_ANY, 'Add File',
            'Add a file to be archived')
        self.Bind(wx.EVT_MENU, self.on_add_file,
                  add_file_menu_item)

        add_folder_menu_item = edit_menu.Append(
            wx.ID_ANY, 'Add Folder',
            'Add a folder to be archived')
        self.Bind(wx.EVT_MENU, self.on_add_folder,
                  add_folder_menu_item)

        remove_menu_item = edit_menu.Append(
            wx.ID_ANY, 'Remove File/Folder',
            'Remove a file or folder')
        self.Bind(wx.EVT_MENU, self.on_remove,
                  remove_menu_item)
        menu_bar.Append(edit_menu, 'Edit')

        self.SetMenuBar(menu_bar)

    def create_toolbar(self):
        self.toolbar = self.CreateToolBar()

        add_ico = wx.ArtProvider.GetBitmap(
            wx.ART_PLUS, wx.ART_TOOLBAR, (16, 16))
        add_file_tool = self.toolbar.AddTool(
            wx.ID_ANY, 'Add File', add_ico,
            'Add a file to be archived')
        self.Bind(wx.EVT_MENU, self.on_add_file,
                  add_file_tool)

        add_folder_ico = wx.ArtProvider.GetBitmap(
            wx.ART_FOLDER_OPEN, wx.ART_TOOLBAR, (16, 16))
        add_folder_tool = self.toolbar.AddTool(
            wx.ID_ANY, 'Add Folder', add_folder_ico,
            'Add a folder to be archived')
        self.Bind(wx.EVT_MENU, self.on_add_folder,
                  add_folder_tool)

        remove_ico = wx.ArtProvider.GetBitmap(
            wx.ART_MINUS, wx.ART_TOOLBAR, (16, 16))
        remove_tool = self.toolbar.AddTool(
            wx.ID_ANY, 'Remove', remove_ico,
            'Remove selected item')
        self.Bind(wx.EVT_MENU, self.on_remove, remove_tool)

        self.toolbar.Realize()

    def on_add_file(self, event):
        with wx.FileDialog(
            self, message="Choose a file",
            defaultDir=self.panel.current_directory,
            defaultFile="",
            wildcard=open_wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
            ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                paths = dlg.GetPaths()
                self.panel.update_display(paths)

    def on_add_folder(self, event):
        with wx.DirDialog(
            self, message="Choose a directory:",
            defaultPath=self.panel.current_directory,
            style=wx.DD_DEFAULT_STYLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                paths = [dlg.GetPath()]
                self.panel.update_display(paths)

    def on_exit(self, event):
        self.Close()

    def on_remove(self, event):
        selected_items = self.panel.archive_olv.GetSelectedObjects()
        self.panel.archive_olv.RemoveObjects(selected_items)

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
