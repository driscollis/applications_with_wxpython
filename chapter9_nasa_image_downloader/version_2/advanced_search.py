# advanced_search.py

import wx

from pubsub import pub


class AdvancedSearch(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.free_text = wx.TextCtrl(self)
        self.ui_helper('Free text search:', self.free_text)
        self.nasa_center = wx.TextCtrl(self)
        self.ui_helper('NASA Center:', self.nasa_center)
        self.description = wx.TextCtrl(self)
        self.ui_helper('Description:', self.description)
        self.description_508 = wx.TextCtrl(self)
        self.ui_helper('Description 508:', self.description_508)
        self.keywords = wx.TextCtrl(self)
        self.ui_helper('Keywords (separate with commas):',
                       self.keywords)
        self.location = wx.TextCtrl(self)
        self.ui_helper('Location:', self.location)
        self.nasa_id = wx.TextCtrl(self)
        self.ui_helper('NASA ID:', self.nasa_id)
        self.photographer = wx.TextCtrl(self)
        self.ui_helper('Photographer:', self.photographer)
        self.secondary_creator = wx.TextCtrl(self)
        self.ui_helper('Secondary photographer:', self.secondary_creator)
        self.title = wx.TextCtrl(self)
        self.ui_helper('Title:', self.title)
        search = wx.Button(self, label='Search')
        search.Bind(wx.EVT_BUTTON, self.on_search)
        self.main_sizer.Add(search, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(self.main_sizer)

    def ui_helper(self, label, textctrl):
        sizer = wx.BoxSizer()
        lbl = wx.StaticText(self, label=label, size=(150, -1))
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(textctrl, 1, wx.ALL | wx.EXPAND, 5)
        self.main_sizer.Add(sizer, 0, wx.EXPAND)

    def on_search(self, event):
        query = {'q': self.free_text.GetValue(),
                 'media_type': 'image',
                 'center': self.nasa_center.GetValue(),
                 'description': self.description.GetValue(),
                 'description_508': self.description_508.GetValue(),
                 'keywords': self.keywords.GetValue(),
                 'location': self.location.GetValue(),
                 'nasa_id': self.nasa_id.GetValue(),
                 'photographer': self.photographer.GetValue(),
                 'secondary_creator': self.secondary_creator.GetValue(),
                 'title': self.title.GetValue()}
        pub.sendMessage('update_ui')
        pub.sendMessage('search_results', query=query)