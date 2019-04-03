# main.py

import wx

from merge_panel import MergePanel
from split_panel import SplitPanel


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
        super().__init__(None, title='PDF Merger / Splitter',
                         size=(800, 600))
        self.panel = MainPanel(self)
        self.Show()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()