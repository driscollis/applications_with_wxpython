# regular_search.py

import os
import requests
import wx

from download_dialog import DownloadDialog
from ObjectListView import ObjectListView, ColumnDefn
from pubsub import pub
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


class RegularSearch(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.search_results = []
        self.max_size = 300
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.paths = wx.StandardPaths.Get()
        pub.subscribe(self.load_search_results, 'search_results')

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

    def reset_image(self):
        img = wx.Image(240, 240)
        self.image_ctrl.SetBitmap(wx.Bitmap(img))
        self.Refresh()

    def update_search_results(self):
        self.search_results_olv.SetColumns([
            ColumnDefn("Title", "left", 250, "title"),
            ColumnDefn("Description", "left", 350, "description"),
            ColumnDefn("Photographer", "left", 100, "photographer"),
            ColumnDefn("Date Created", "left", 150, "date_created")
        ])
        self.search_results_olv.SetObjects(self.search_results)

    def load_search_results(self, query):
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
        self.reset_image()