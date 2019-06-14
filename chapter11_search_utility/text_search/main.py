# main.py

import os
import sys
import subprocess
import time
import wx

from configparser import ConfigParser, NoSectionError
from ObjectListView import ObjectListView, ColumnDefn
from preferences import PreferencesDialog
from pubsub import pub
from search_thread import SearchThread


class SearchResult:

    def __init__(self, path, modified_time, data):
        self.path = path
        self.modified = time.strftime('%D %H:%M:%S',
                                      time.gmtime(modified_time))
        self.data = data


class MainPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.search_results = []
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.create_ui()
        self.SetSizer(self.main_sizer)
        pub.subscribe(self.update_search_results, 'update')

        module_path = os.path.dirname(os.path.abspath( __file__ ))
        self.config = os.path.join(module_path, 'config.ini')
        if not os.path.exists(self.config):
            message = 'Unable to find grin3 for text searches. ' \
                       'Install grin3 and open preferences to ' \
                       'configure it:  pip install grin3'
            self.show_error(message)

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
        self.search_results_olv.Bind(wx.EVT_LIST_ITEM_SELECTED,
                                     self.on_selection)
        self.main_sizer.Add(self.search_results_olv, 1, wx.ALL | wx.EXPAND, 5)
        self.update_ui()

        self.results_txt = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.main_sizer.Add(self.results_txt, 1, wx.ALL | wx.EXPAND, 5)

        show_result_btn = wx.Button(self, label='Open Containing Folder')
        show_result_btn.Bind(wx.EVT_BUTTON, self.on_show_result)
        self.main_sizer.Add(show_result_btn, 0, wx.ALL | wx.CENTER, 5)

    def on_choose_folder(self, event):
        with wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE,
                          ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.directory.SetValue(dlg.GetPath())

    def on_selection(self, event):
        current_selection = self.search_results_olv.GetSelectedObject()
        self.results_txt.SetValue('\n'.join(current_selection.data))

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
                self.show_error(message)

    def on_search(self, event):
        search_term = self.search_ctrl.GetValue()
        self.search(search_term)

    def search(self, search_term):
        """
        Search for the specified term in the directory and its
        sub-directories
        """
        folder = self.directory.GetValue()
        config = ConfigParser()
        config.read(self.config)
        try:
            grin = config.get("Settings", "grin")
        except NoSectionError:
            self.show_error('Settings or grin section not found')
            return

        if not os.path.exists(grin):
            self.show_error(f'Grin location does not exist {grin}')
            return
        if folder:
            self.search_results = []
            SearchThread(folder, search_term)

    def show_error(self, message):
        with wx.MessageDialog(None, message=message,
                              caption='Error',
                              style= wx.ICON_ERROR) as dlg:
            dlg.ShowModal()

    def update_search_results(self, results):
        """
        Called by pubsub from thread
        """
        for key in results:
            if os.path.exists(key):
                stat = os.stat(key)
                modified_time = stat.st_mtime
                result = SearchResult(key, modified_time, results[key])
                self.search_results.append(result)

        if results:
            self.update_ui()
        else:
            search_term = self.search_ctrl.GetValue()
            self.search_results_olv.ClearAll()
            msg = f'No Results Found for: "{search_term}"'
            self.search_results_olv.SetEmptyListMsg(msg)

    def update_ui(self):
        self.search_results_olv.SetColumns([
            ColumnDefn("File Path", "left", 800, "path"),
            ColumnDefn("Modified Time", "left", 150, "modified")
        ])
        self.search_results_olv.SetObjects(self.search_results)


class Search(wx.Frame):

    def __init__(self):
        super().__init__(None, title='Text Search Utility',
                         size=(1200, 800))
        pub.subscribe(self.update_status, 'status')
        panel = MainPanel(self)
        self.create_menu()
        self.statusbar = self.CreateStatusBar(1)
        self.Show()

    def update_status(self, search_time):
        msg = f'Search finished in {search_time:5.4} seconds'
        self.SetStatusText(msg)

    def create_menu(self):
        menu_bar = wx.MenuBar()

        # Create file menu
        file_menu = wx.Menu()

        preferences = file_menu.Append(
            wx.ID_ANY, "Preferences",
            "Open Preferences Dialog")
        self.Bind(wx.EVT_MENU, self.on_preferences,
                  preferences)

        exit_menu_item = file_menu.Append(
            wx.ID_ANY, "Exit",
            "Exit the application")
        menu_bar.Append(file_menu, '&File')
        self.Bind(wx.EVT_MENU, self.on_exit,
                  exit_menu_item)

        self.SetMenuBar(menu_bar)

    def on_exit(self, event):
        self.Close()

    def on_preferences(self, event):
        with PreferencesDialog() as dlg:
            dlg.ShowModal()

if __name__ == '__main__':
    app = wx.App(False)
    frame = Search()
    app.MainLoop()