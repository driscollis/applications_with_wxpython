# main.py

import os
import wx

import wx.lib.agw.flatnotebook as fnb


class Main(wx.Frame):
    
    def __init__(self):
        super().__init__(
            None, title="XML Editor",
            size=(800, 600))
        
        self.notebook = None
        self.opened_files = []
        self.current_page = None
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self)
        self.panel.SetSizer(self.main_sizer)
        
    def create_new_editor(self, xml_path):
        """
        Create the tree and xml editing widgets when the user loads
        an XML file
        """
        if not self.notebook:
            self.notebook = fnb.FlatNotebook(
                    self.panel)
            self.main_sizer.Add(self.notebook, 1, 
                                wx.ALL|wx.EXPAND, 5)
            style = self.notebook.GetAGWWindowStyleFlag()
            style |= fnb.FNB_X_ON_TAB
            self.notebook.SetAGWWindowStyleFlag(style)
            self.notebook.Bind(
                    fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, 
                    self.on_page_closing)
    
        if xml_path not in self.opened_files:
            self.current_page = NewPage(
                self.notebook, xml_path, self.size,
                self.opened_files)
            self.notebook.AddPage(self.current_page,
                                  os.path.basename(xml_path),
                                  select=True)
            self.last_opened_file = xml_path
    
            self.opened_files.append(self.last_opened_file)
    
        self.panel.Layout()
        
    def on_page_closing(self, event):
        pass