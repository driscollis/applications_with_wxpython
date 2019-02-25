# main.py

import controller
import dialogs
import os
import wx

from concurrent import futures
from ObjectListView import ObjectListView, ColumnDefn


class BookPanel(wx.Panel):
    """
    The book panel widget - holds majority of the widgets 
    in the UI
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        
        if not os.path.exists("books.db"):
            controller.setup_database()
        
        self.database = controller.Database()
        
        try:
            self.book_results = controller.get_all_records(self.session)
        except:
            self.book_results = []
    
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD) 
    
        # create the search related widgets
        categories = ["Author", "Title", "ISBN", "Publisher"]
        search_label = wx.StaticText(self, label="Search By:")
        search_label.SetFont(font)
        search_sizer.Add(search_label, 0, wx.ALL, 5)
    
        self.categories = wx.ComboBox(self, value="Author", choices=categories)
        search_sizer.Add(self.categories, 0, wx.ALL, 5)
    
        self.search_ctrl = wx.SearchCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.search_ctrl.Bind(wx.EVT_TEXT_ENTER, self.search)
        search_sizer.Add(self.search_ctrl, 0, wx.ALL, 5)
    
        self.book_results_olv = ObjectListView(self, style=wx.LC_REPORT
                                                 |wx.SUNKEN_BORDER)
        self.book_results_olv.SetEmptyListMsg("No Records Found")
        self.update_book_results()
    
        # create the button row
        add_record_btn = wx.Button(self, label="Add")
        add_record_btn.Bind(wx.EVT_BUTTON, self.add_record)
        btn_sizer.Add(add_record_btn, 0, wx.ALL, 5)
    
        edit_record_btn = wx.Button(self, label="Edit")
        edit_record_btn.Bind(wx.EVT_BUTTON, self.edit_record)
        btn_sizer.Add(edit_record_btn, 0, wx.ALL, 5)
    
        delete_record_btn = wx.Button(self, label="Delete")
        delete_record_btn.Bind(wx.EVT_BUTTON, self.delete_record)
        btn_sizer.Add(delete_record_btn, 0, wx.ALL, 5)
    
        show_all_btn = wx.Button(self, label="Show All")
        show_all_btn.Bind(wx.EVT_BUTTON, self.on_show_all)
        btn_sizer.Add(show_all_btn, 0, wx.ALL, 5)
    
        main_sizer.Add(search_sizer)
        main_sizer.Add(self.book_results_olv, 1, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(main_sizer)
        
    def add_record(self, event):
        """
        Add a record to the database
        """
        with dialogs.RecordDialog(self.database) as dlg:
            dlg.ShowModal()
            
        self.show_all_records()
    
    def edit_record(self, event):
        """
        Edit a record
        """
        selected_row = self.book_results_olv.GetSelectedObject()
        if selected_row is None:
            dialogs.show_message('No row selected!', 'Error')
            return
        
        with dialogs.RecordDialog(self.database,
                                  selected_row, 
                                  title='Modify',
                                  addRecord=False) as dlg:
            dlg.ShowModal()
        
        self.show_all_records()
    
    def delete_record(self, event):
        """
        Delete a record
        """
        selected_row = self.book_results_olv.GetSelectedObject()
        if selected_row is None:
            dialogs.show_message('No row selected!', 'Error')
            return
        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            f = executor.submit(self.database.delete_record, selected_row.id)
            f.add_done_callback(self.show_all_records)
        
    def show_all_records(self, future=None):
        """
        Updates the record list to show all of them
        """
        if future is not None:
            if future.cancelled():
                return
            elif future.done():
                error = future.exception()
                if error:
                    print(f'Error updating record list: {error}')
                    return
                
        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            f = executor.submit(self.database.get_all_records)
            f.add_done_callback(self.update_book_results)
        
    def search(self, event):
        """
        Searches database based on the user's filter 
        choice and keyword
        """
        filter_choice = self.categories.GetValue()
        keyword = self.search_ctrl.GetValue()
        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            f = executor.submit(
                self.database.search_records, 
                filter_choice,
                keyword)
            f.add_done_callback(self.update_book_results)
    
    def on_show_all(self, event):
        """
        Updates the record list to show all the records
        """
        self.show_all_records()
        
    def refresh_view(self):
        self.book_results_olv.SetColumns([
                    ColumnDefn("Title", "left", 350, "title"),
                    ColumnDefn("Author", "left", 150, "author"),
                    ColumnDefn("ISBN", "right", 150, "isbn"),
                    ColumnDefn("Publisher", "left", 150, "publisher")
                ])
        self.book_results_olv.SetObjects(self.book_results)
    
    def update_book_results(self, future=None):
        """
        Updates the ObjectListView's contents
        """
        if future is not None:
            if future.cancelled():
                return
            elif future.done():
                error = future.exception()
                if error:
                    print(f'Error updating books {error}')
                else:
                    self.refresh_view()
    
    
class BookFrame(wx.Frame):
    """
    The top level frame widget
    """

    def __init__(self):
        """Constructor"""
        super().__init__(
            None, title="Media Organizer",
            size=(800, 600))
        panel = BookPanel(self)
        
        self.Show()
        
if __name__ == "__main__":
    app = wx.App(False)
    frame = BookFrame()
    app.MainLoop()