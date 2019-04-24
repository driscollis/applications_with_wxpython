# main.py

import os
import sys
import subprocess
import time
import wx

from ObjectListView import ObjectListView, ColumnDefn
from pubsub import pub
from search_threads import SearchFolderThread, SearchSubdirectoriesThread


class SearchResult:

    def __init__(self, path, modified_time):
        self.path = path
        self.modified = time.strftime('%D %H:%M:%S',
                                      time.gmtime(modified_time))


class MainPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.search_results = []
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.create_ui()
        self.SetSizer(self.main_sizer)
        pub.subscribe(self.update_search_results, 'update')

    def create_ui(self):
        # Create the widgets for the search path
        row_sizer = wx.BoxSizer()
        lbl = wx.StaticText(self, label='Location:')
        row_sizer.Add(lbl, 0, wx.ALL | wx.CENTER, 5)
        self.directory = wx.TextCtrl(self, style=wx.TE_READONLY)
        row_sizer.Add(self.directory, 1, wx.ALL | wx.EXPAND, 5)
        open_dir_btn = wx.Button(self, label='Choose Folder')
        open_dir_btn.Bind(wx.EVT_BUTTON, self.on_choose_folder)
        row_sizer.Add(open_dir_btn, 0, wx.ALL, 5)
        self.main_sizer.Add(row_sizer, 0, wx.EXPAND)

        # Create search filter widgets
        row_sizer = wx.BoxSizer()
        lbl = wx.StaticText(self, label='Limit search to filetype:')
        row_sizer.Add(lbl, 0, wx.ALL|wx.CENTER, 5)

        self.file_type = wx.TextCtrl(self)
        row_sizer.Add(self.file_type, 0, wx.ALL, 5)

        self.sub_directories = wx.CheckBox(self, label='Sub-directories')
        row_sizer.Add(self.sub_directories, 0, wx.ALL | wx.CENTER, 5)

        self.case_sensitive = wx.CheckBox(self, label='Case-sensitive')
        row_sizer.Add(self.case_sensitive, 0, wx.ALL | wx.CENTER, 5)
        self.main_sizer.Add(row_sizer)

        # Add search bar
        self.search_ctrl = wx.SearchCtrl(
            self, style=wx.TE_PROCESS_ENTER, size=(-1, 25))
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        self.search_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        self.main_sizer.Add(self.search_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Search results widget
        self.search_results_olv = ObjectListView(
            self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.search_results_olv.SetEmptyListMsg("No Results Found")
        self.main_sizer.Add(self.search_results_olv, 1, wx.ALL | wx.EXPAND, 5)
        self.update_ui()

        show_result_btn = wx.Button(self, label='Open Containing Folder')
        show_result_btn.Bind(wx.EVT_BUTTON, self.on_show_result)
        self.main_sizer.Add(show_result_btn, 0, wx.ALL | wx.CENTER, 5)

    def on_choose_folder(self, event):
        with wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE,
                          ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.directory.SetValue(dlg.GetPath())

    def on_show_result(self, event):
        """
        Attempt to open the folder that the result was found in
        """
        result = self.search_results_olv.GetSelectedObject()
        if result:
            path = os.path.dirname(result.path)
            try:
                if sys.platform == 'darwin':
                    subprocess.check_call(['open', '--', path])
                elif 'linux' in sys.platform:
                    subprocess.check_call(['xdg-open', path])
                elif sys.platform == 'win32':
                    subprocess.check_call(['explorer', path])
            except:
                if sys.platform == 'win32':
                    # Ignore error on Windows as there seems to be
                    # a weird return code on Windows
                    return

                message = f'Unable to open file manager to {path}'
                with wx.MessageDialog(None, message=message,
                                      caption='Error',
                                      style= wx.ICON_ERROR) as dlg:
                    dlg.ShowModal()

    def on_search(self, event):
        search_term = self.search_ctrl.GetValue()
        file_type = self.file_type.GetValue()
        file_type = file_type.lower()
        if '.' not in file_type:
            file_type = f'.{file_type}'

        if not self.sub_directories.GetValue():
            # Do not search sub-directories
            self.search_current_folder_only(search_term, file_type)
        else:
            self.search(search_term, file_type)

    def search(self, search_term, file_type):
        """
        Search for the specified term in the directory and its
        sub-directories
        """
        folder = self.directory.GetValue()
        if folder:
            self.search_results = []
            SearchSubdirectoriesThread(folder, search_term, file_type,
                                       self.case_sensitive.GetValue())

    def search_current_folder_only(self, search_term, file_type):
        """
        Search for the specified term in the directory only. Do
        not search sub-directories
        """
        folder = self.directory.GetValue()
        if folder:
            self.search_results = []
            SearchFolderThread(folder, search_term, file_type,
                               self.case_sensitive.GetValue())

    def update_search_results(self, result):
        """
        Called by pubsub from thread
        """
        if result:
            path, modified_time = result
            self.search_results.append(SearchResult(path, modified_time))
        self.update_ui()

    def update_ui(self):
        self.search_results_olv.SetColumns([
            ColumnDefn("File Path", "left", 300, "path"),
            ColumnDefn("Modified Time", "left", 150, "modified")
        ])
        self.search_results_olv.SetObjects(self.search_results)


class Search(wx.Frame):

    def __init__(self):
        super().__init__(None, title='Search Utility',
                         size=(600, 600))
        pub.subscribe(self.update_status, 'status')
        panel = MainPanel(self)
        self.statusbar = self.CreateStatusBar(1)
        self.Show()

    def update_status(self, search_time):
        msg = f'Search finished in {search_time:5.4} seconds'
        self.SetStatusText(msg)


if __name__ == '__main__':
    app = wx.App(False)
    frame = Search()
    app.MainLoop()