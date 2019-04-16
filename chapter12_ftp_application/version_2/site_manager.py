# site_manager.py

import wx

from pubsub import pub

class SiteManager(wx.Dialog):
    
    def __init__(self):
        super().__init__(None, title='Site Manager')
        
    def create_ui(self):
        pass