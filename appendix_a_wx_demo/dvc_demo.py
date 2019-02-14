# dvc_demo.py

import wx
import wx.dataview as dv


class MyPanel(wx.Panel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.dvlc = dvlc = dv.DataViewListCtrl(self)
        
        # Give it some columns.
        # The ID col we'll customize a bit:
        dvlc.AppendTextColumn('id', width=40)
        dvlc.AppendTextColumn('artist', width=170)
        dvlc.AppendTextColumn('title', width=260)
        dvlc.AppendTextColumn('genre', width=80)
    
        # Load the data. Each item (row) is added as a sequence of values
        # whose order matches the columns
        for itemvalues in musicdata:
            dvlc.AppendItem(itemvalues)
    
        # Set the layout so the listctrl fills the panel
        self.Sizer = wx.BoxSizer()
        self.Sizer.Add(dvlc, 1, wx.EXPAND)
        
class MyFrame(wx.Frame):
    
    def __init__(self):
        super().__init__(None, 
                         title='DVC ListCtrl Demo Extraction')
        panel = MyPanel(self)
        self.Show()

if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()