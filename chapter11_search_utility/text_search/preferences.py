# preferences.py

import os
import wx

from configparser import ConfigParser

class PreferencesDialog(wx.Dialog):

    def __init__(self):
        super().__init__(None, title='Preferences')
        module_path = os.path.dirname(os.path.abspath( __file__ ))
        self.config = os.path.join(module_path, 'config.ini')
        if not os.path.exists(self.config):
            self.create_config()

        config = ConfigParser()
        config.read(self.config)
        self.grin = config.get("Settings", "grin")

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.create_ui()
        self.SetSizer(self.main_sizer)

    def create_ui(self):
        row_sizer = wx.BoxSizer()
        lbl = wx.StaticText(self, label='Grin3 Location:')
        row_sizer.Add(lbl, 0, wx.ALL | wx.CENTER, 5)
        self.grin_location = wx.TextCtrl(self, value=self.grin)
        row_sizer.Add(self.grin_location, 1, wx.ALL | wx.EXPAND, 5)
        browse_button = wx.Button(self, label='Browse')
        browse_button.Bind(wx.EVT_BUTTON, self.on_browse)
        row_sizer.Add(browse_button, 0, wx.ALL, 5)
        self.main_sizer.Add(row_sizer, 0, wx.EXPAND)

        save_btn = wx.Button(self, label='Save')
        save_btn.Bind(wx.EVT_BUTTON, self.save)
        self.main_sizer.Add(save_btn, 0, wx.ALL | wx.CENTER, 5)

    def create_config(self):
        config = ConfigParser()
        config.add_section("Settings")
        config.set("Settings", 'grin', '')

        with open(self.config, 'w') as config_file:
            config.write(config_file)

    def save(self, event):
        grin_location = self.grin_location.GetValue()
        if not grin_location:
            self.show_error('Grin location not set!')
            return
        if not os.path.exists(grin_location):
            self.show_error(f'Grin location does not exist {grin_location}')
            return

        config = ConfigParser()
        config.read(self.config)
        config.set("Settings", "grin", grin_location)
        with open(self.config, 'w') as config_file:
            config.write(config_file)
        self.Close()

    def show_error(self, message):
        with wx.MessageDialog(None, message=message,
                              caption='Error',
                              style= wx.ICON_ERROR) as dlg:
            dlg.ShowModal()

    def on_browse(self, event):
        """
        Browse for the grin file
        """
        wildcard = "All files (*.*)|*.*"
        with wx.FileDialog(None, "Choose a file",
                           wildcard=wildcard,
                           style=wx.ID_OPEN) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.grin_location.SetValue(dialog.GetPath())
