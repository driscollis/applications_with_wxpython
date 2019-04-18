# download_dialog.py

import requests
import wx

wildcard = "All files (*.*)|*.*"


class DownloadDialog(wx.Dialog):

    def __init__(self, selection):
        super().__init__(None, title='Download images')
        self.paths = wx.StandardPaths.Get()
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.list_box = wx.ListBox(self, choices=[], size=wx.DefaultSize)
        urls = self.get_image_urls(selection)
        if urls:
            choices = {url.split('/')[-1]: url for url in urls if 'jpg' in url}
            for choice in choices:
                self.list_box.Append(choice, choices[choice])
        main_sizer.Add(self.list_box, 1, wx.EXPAND|wx.ALL, 5)

        save_btn = wx.Button(self, label='Save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        main_sizer.Add(save_btn, 0, wx.ALL|wx.CENTER, 5)
        self.SetSizer(main_sizer)

    def get_image_urls(self, item):
        asset_url = f'https://images-api.nasa.gov/asset/{item.nasa_id}'
        image_request = requests.get(asset_url)
        image_json = image_request.json()
        try:
            image_urls = [url['href'] for url in image_json['collection']['items']]
        except:
            image_urls = []
        return image_urls

    def on_save(self, event):
        selection = self.list_box.GetSelection()
        if selection != -1:
            with wx.FileDialog(
                self, message="Save file as ...",
                defaultDir=self.paths.GetDocumentsDir(),
                defaultFile=self.list_box.GetString(selection),
                wildcard=wildcard,
                style=wx.FD_SAVE
                ) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    self.save(path)
        else:
            message = 'No image selected'
            with wx.MessageDialog(None, message=message,
                              caption='Cannot Save',
                              style=wx.ICON_ERROR) as dlg:
                dlg.ShowModal()

    def save(self, path):
        selection = self.list_box.GetSelection()
        r = requests.get(
            self.list_box.GetClientData(selection))
        try:
            with open(path, "wb") as image:
                image.write(r.content)

            message = 'File saved successfully'
            with wx.MessageDialog(None, message=message,
                                  caption='Save Successful',
                                  style=wx.ICON_INFORMATION) as dlg:
                dlg.ShowModal()
        except BaseException:
            message = 'File failed to save!'
            with wx.MessageDialog(None, message=message,
                                  caption='Save Failed',
                                  style=wx.ICON_ERROR) as dlg:
                dlg.ShowModal()