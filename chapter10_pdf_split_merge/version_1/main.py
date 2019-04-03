# main.py

import os
import wx

from merge_panel import MergePanel
from pubsub import pub
from split_panel import SplitPanel

wildcard = "PDFs (*.pdf)|*.pdf"


class MainPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self)
        merge_tab = MergePanel(notebook)
        notebook.AddPage(merge_tab, 'Merge PDFs')
        split_tab = SplitPanel(notebook)
        notebook.AddPage(split_tab, 'Split PDFs')
        main_sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(main_sizer)

class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title='Template', size=(800, 600))
        self.panel = MainPanel(self)
        self.create_menu()
        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        add_file_menu_item = file_menu.Append(
            wx.ID_ANY, 'Add PDFs', 'Add PDF files'
        )
        menu_bar.Append(file_menu, '&File')
        self.Bind(wx.EVT_MENU, self.on_add_file,
                  add_file_menu_item)
        self.SetMenuBar(menu_bar)

    def on_add_file(self, event):
        with wx.FileDialog(
            self, message="Choose a file",
            defaultDir='~',
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE
            ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                paths = dlg.GetPaths()
        if paths:
            pub.sendMessage('pdf_path', paths=paths)

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()