# main.py

import wx

from advanced_search import AdvancedSearch
from regular_search import RegularSearch
from pubsub import pub


class MainPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        pub.subscribe(self.update_ui, 'update_ui')

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        search_sizer = wx.BoxSizer()

        txt = 'Search for images on NASA'
        label = wx.StaticText(self, label=txt)
        self.main_sizer.Add(label, 0, wx.ALL, 5)
        self.search = wx.SearchCtrl(
            self, style=wx.TE_PROCESS_ENTER, size=(-1, 25))
        self.search.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        self.search.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        search_sizer.Add(self.search, 1, wx.EXPAND)

        self.advanced_search_btn = wx.Button(self, label='Advanced Search',
                                    size=(-1, 25))
        self.advanced_search_btn.Bind(wx.EVT_BUTTON, self.on_advanced_search)
        search_sizer.Add(self.advanced_search_btn, 0, wx.ALL, 5)
        self.main_sizer.Add(search_sizer, 0, wx.EXPAND)

        self.search_panel = RegularSearch(self)
        self.advanced_search_panel = AdvancedSearch(self)
        self.advanced_search_panel.Hide()
        self.main_sizer.Add(self.search_panel, 1, wx.EXPAND)
        self.main_sizer.Add(self.advanced_search_panel, 1, wx.EXPAND)

        self.SetSizer(self.main_sizer)

    def on_search(self, event):
        search_results = []
        search_term = event.GetString()
        if search_term:
            query = {'q': search_term, 'media_type': 'image'}
            pub.sendMessage('search_results', query=query)

    def on_advanced_search(self, event):
        self.search.Hide()
        self.search_panel.Hide()
        self.advanced_search_btn.Hide()
        self.advanced_search_panel.Show()
        self.main_sizer.Layout()

    def update_ui(self):
        """
        Hide advanced search and re-show original screen

        Called by pubsub when advanced search is invoked
        """
        self.advanced_search_panel.Hide()
        self.search.Show()
        self.search_panel.Show()
        self.advanced_search_btn.Show()
        self.main_sizer.Layout()


class SearchFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title='NASA Search',
                         size=(1200, 800))
        panel = MainPanel(self)
        self.Show()

if __name__ == '__main__':
    app = wx.App(False)
    frame = SearchFrame()
    app.MainLoop()