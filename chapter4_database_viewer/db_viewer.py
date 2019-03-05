# db_viewer.py

import os
import wx

from ObjectListView import ObjectListView, ColumnDefn
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker, clear_mappers


class GenericDBClass(object):
    """
    Stub of a database class for ObjectListView
    """
    pass

class MainPanel(wx.Panel):
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.db_data = []
        self.current_directory = os.getcwd()
    
        self.dataOlv = ObjectListView(self, 
                                      style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        
        # load DB
        loadDBBtn = wx.Button(self, label="Load DB")
        loadDBBtn.Bind(wx.EVT_BUTTON, self.loadDatabase)
        self.table_names = []
        self.tableCbo = wx.ComboBox(self, value="", choices=self.table_names)
        self.tableCbo.Bind(wx.EVT_COMBOBOX, self.loadTable)
    
        # Create some sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
    
        main_sizer.Add(loadDBBtn, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(self.tableCbo, 0, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(self.dataOlv, 1, wx.ALL|wx.EXPAND, 5)
    
        self.SetSizer(main_sizer)
        
    def loadTable(self, event):
        """
        Load the table into the ObjectListView widget
        """
        current_table = self.tableCbo.GetValue()
        metadata = MetaData(self.engine)
        table = Table(current_table, metadata, autoload=True, autoload_with=self.engine)
        self.columns = table.columns.keys()
    
        clear_mappers()
        mapper(GenericDBClass, table)
    
        Session = sessionmaker(bind=self.engine)
        session = Session()
        self.db_data = session.query(GenericDBClass).all()
    
        self.setData()
        self.Layout()
        
    def loadDatabase(self, event):
        """
        Create a file dialog to open a database file
        
        Load the database file into the application
        
        Populate the table combobox
        """
        wildcard = "All files (*.*)|*.*"
        with wx.FileDialog(
            self, message="Choose a file",
            defaultDir=self.current_directory,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                db_path = dlg.GetPath()
            else:
                return
    
        self.engine = create_engine('sqlite:///%s' % db_path, echo=True)
    
        self.table_names = self.engine.table_names()
        self.tableCbo.SetItems(self.table_names)
        self.tableCbo.SetValue(self.table_names[0])
        self.loadTable("")
    
    def setData(self, data=None):
        """
        Update the ObjectListView widget's contents
        """
        olv_columns = []
        for column in self.columns:
            olv_columns.append(ColumnDefn(
                column.title(), "left", 120, column.lower()))
        self.dataOlv.SetColumns(olv_columns)
 
        self.dataOlv.SetObjects(self.db_data)
        
class MainFrame(wx.Frame):
    
    def __init__(self):
        super().__init__(
            parent=None, title="Database Viewer", 
            size=(800,600))
        panel = MainPanel(self)
        self.Show()
        
if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.MainLoop()
