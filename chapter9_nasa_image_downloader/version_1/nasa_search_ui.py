# nasa_search_ui.py

import os
import requests
import wx

from download_dialog import DownloadDialog
from ObjectListView import ObjectListView, ColumnDefn
from urllib.parse import urlencode, quote_plus


base_url = 'https://images-api.nasa.gov/search'


class Result:

    def __init__(self, item):
        data = item['data'][0]
        self.title = data['title']
        self.location = data.get('location', '')
        self.nasa_id = data['nasa_id']
        self.description = data['description']
        self.photographer = data.get('photographer', '')
        self.date_created = data['date_created']
        self.item = item

        if item.get('links'):
            try:
                self.thumbnail = item['links'][0]['href']
            except BaseException:
                self.thumbnail = ''


class MainPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.search_results = []
        self.max_size = 300
        self.paths = wx.StandardPaths.Get()
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        txt = 'Search for images on NASA'
        label = wx.StaticText(self, label=txt)
        main_sizer.Add(label, 0, wx.ALL, 5)
        self.search = wx.SearchCtrl(
            self, style=wx.TE_PROCESS_ENTER, size=(-1, 25))
        self.search.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        self.search.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        main_sizer.Add(self.search, 0, wx.EXPAND)

        self.search_results_olv = ObjectListView(
            self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.search_results_olv.SetEmptyListMsg("No Results Found")
        self.search_results_olv.Bind(wx.EVT_LIST_ITEM_SELECTED,
                                     self.on_selection)
        main_sizer.Add(self.search_results_olv, 1, wx.EXPAND)
        self.update_search_results()

        main_sizer.AddSpacer(30)
        self.title = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.title.SetFont(font)
        main_sizer.Add(self.title, 0, wx.ALL|wx.EXPAND, 5)
        img = wx.Image(240, 240)
        self.image_ctrl = wx.StaticBitmap(self,
                                          bitmap=wx.Bitmap(img))
        main_sizer.Add(self.image_ctrl, 0, wx.CENTER|wx.ALL, 5
                       )
        download_btn = wx.Button(self, label='Download Image')
        download_btn.Bind(wx.EVT_BUTTON, self.on_download)
        main_sizer.Add(download_btn, 0, wx.ALL|wx.CENTER, 5)

        self.SetSizer(main_sizer)

    def on_download(self, event):
        selection = self.search_results_olv.GetSelectedObject()
        if selection:
            with DownloadDialog(selection) as dlg:
                dlg.ShowModal()

    def on_search(self, event):
        search_term = event.GetString()
        if search_term:
            query = {'q': search_term, 'media_type': 'image'}
            full_url = base_url + '?' + urlencode(query, quote_via=quote_plus)
            r = requests.get(full_url)
            data = r.json()
            self.search_results = []
            for item in data['collection']['items']:
                if item.get('data') and len(item.get('data')) > 0:
                    data = item['data'][0]
                    if data['title'].strip() == '':
                        # Skip results with blank titles
                        continue
                    result = Result(item)
                    self.search_results.append(result)
            self.update_search_results()

    def on_selection(self, event):
        selection = self.search_results_olv.GetSelectedObject()
        self.title.SetValue(f'{selection.title}')
        if selection.thumbnail:
            self.update_image(selection.thumbnail)
        else:
            img = wx.Image(240, 240)
            self.image_ctrl.SetBitmap(wx.Bitmap(img))
            self.Refresh()
            self.Layout()


    def update_image(self, url):
        filename = url.split('/')[-1]
        tmp_location = os.path.join(self.paths.GetTempDir(), filename)
        r = requests.get(url)
        with open(tmp_location, "wb") as thumbnail:
            thumbnail.write(r.content)

        if os.path.exists(tmp_location):
            img = wx.Image(tmp_location, wx.BITMAP_TYPE_ANY)
            W = img.GetWidth()
            H = img.GetHeight()
            if W > H:
                NewW = self.max_size
                NewH = self.max_size * H / W
            else:
                NewH = self.max_size
                NewW = self.max_size * W / H
            img = img.Scale(NewW,NewH)
        else:
            img = wx.Image(240, 240)

        self.image_ctrl.SetBitmap(wx.Bitmap(img))
        self.Refresh()
        self.Layout()

    def update_search_results(self):
        self.search_results_olv.SetColumns([
            ColumnDefn("Title", "left", 250, "title"),
            ColumnDefn("Description", "left", 350, "description"),
            ColumnDefn("Photographer", "left", 100, "photographer"),
            ColumnDefn("Date Created", "left", 150, "date_created")
        ])
        self.search_results_olv.SetObjects(self.search_results)


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