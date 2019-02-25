# dialogs.py

import controller
import wx

from concurrent import futures


class RecordDialog(wx.Dialog):
    """
    Add / Modify Record dialog
    """

    def __init__(self, database, row=None, title="Add", addRecord=True):
        """Constructor"""
        super().__init__(None, title="%s Record" % title)
        self.addRecord = addRecord
        self.selected_row = row
        self.database = database
        if row:
            book_title = self.selected_row.title
            first_name = self.selected_row.first_name
            last_name = self.selected_row.last_name
            isbn = self.selected_row.isbn
            publisher = self.selected_row.publisher
        else:
            book_title = first_name = last_name = isbn = publisher = ""
        size = (80, -1)
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)

        # create the sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        author_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # create some widgets
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        title_lbl = wx.StaticText(self, label="Title:", size=size)
        title_lbl.SetFont(font)
        self.title_txt = wx.TextCtrl(self, value=book_title)
        main_sizer.Add(self.row_builder([title_lbl, self.title_txt]),
                       0, wx.ALL)

        author_lbl = wx.StaticText(self, label="Author:", size=size)
        author_lbl.SetFont(font)
        author_sizer.Add(author_lbl, 0, wx.ALL, 5)
        self.author_first_txt = wx.TextCtrl(self, value=first_name)
        author_sizer.Add(self.author_first_txt, 1, wx.ALL, 5)
        self.author_last_txt = wx.TextCtrl(self, value=last_name)
        author_sizer.Add(self.author_last_txt, 1, wx.ALL, 5)
        main_sizer.Add(author_sizer, 0, wx.ALL)

        isbn_lbl = wx.StaticText(self, label="ISBN:", size=size)
        isbn_lbl.SetFont(font)
        self.isbn_txt = wx.TextCtrl(self, value=isbn)
        main_sizer.Add(self.row_builder([isbn_lbl, self.isbn_txt]),
                      0, wx.ALL)

        publisher_lbl = wx.StaticText(self, label="Publisher:", size=size)
        publisher_lbl.SetFont(font)
        self.publisher_txt = wx.TextCtrl(self, value=publisher)
        main_sizer.Add(self.row_builder([publisher_lbl, self.publisher_txt]),
                      0, wx.ALL)

        ok_btn = wx.Button(self, label="%s Book" % title)
        ok_btn.Bind(wx.EVT_BUTTON, self.on_record)
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        cancel_btn = wx.Button(self, label="Close")
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_close)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)

        main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(main_sizer)

    def get_data(self):
        """
        Gets the data from the widgets in the dialog

        Also display an error message if required fields
        are empty
        """
        author_dict = {}
        book_dict = {}

        fName = self.author_first_txt.GetValue()
        lName = self.author_last_txt.GetValue()
        title = self.title_txt.GetValue()
        isbn = self.isbn_txt.GetValue()
        publisher = self.publisher_txt.GetValue()

        if fName == "" or title == "":
            show_message("Author and Title are Required!",
                         "Error")
            return None, None
            
        if "-" in isbn:
            isbn = isbn.replace("-", "")
        author_dict["first_name"] = fName
        author_dict["last_name"] = lName
        book_dict["title"] = title
        book_dict["isbn"] = isbn
        book_dict["publisher"] = publisher

        return author_dict, book_dict

    def on_add(self):
        """
        Add the record to the database
        """
        authorDict, bookDict = self.get_data()
        if authorDict is None or bookDict is None:
            return
        
        data = ({"author":authorDict, "book":bookDict})
        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            f = executor.submit(self.database.add_record, data)
            f.add_done_callback(wx.CallAfter, self.add_finished)
    
    def add_finished(self, future):
        if future is not None:
            if future.cancelled():
                return
            elif future.done():
                error = future.exception()
                if error:
                    print(f'Error adding book: {error}')
                    return
                
        # show dialog upon completion
        show_message("Book Added",
                     "Success!", wx.ICON_INFORMATION)

        # clear dialog so we can add another book
        for child in self.GetChildren():
            if isinstance(child, wx.TextCtrl):
                child.SetValue("")

    def on_close(self, event):
        """
        Close the dialog
        """
        self.Destroy()

    def on_edit(self):
        """
        Edit a record in the database
        """
        authorDict, bookDict = self.get_data()
        comboDict = {**authorDict, **bookDict}
        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            f = executor.submit(
                self.database.edit_record,
                self.selected_row.id, 
                comboDict)
            f.add_done_callback(self.edit_finished)
            
    def edit_finished(self, future):
        try:
            if future is not None:
                if future.cancelled():
                    return
                elif future.done():
                    error = future.exception()
                    if error:
                        print(f'Error adding book: {error}')
                        return
            show_message("Book Edited Successfully!", 
                         "Success",
                         wx.ICON_INFORMATION)
        finally:
            self.Destroy()

    def on_record(self, event):
        """
        Add or edit a record
        """
        if self.addRecord:
            self.on_add()
        else:
            self.on_edit()
        self.title_txt.SetFocus()

    def row_builder(self, widgets):
        """
        Helper function for building a row of widgets
        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl, txt = widgets
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(txt, 1, wx.ALL, 5)
        return sizer


def show_message(message, caption, flag=wx.ICON_ERROR):
    """
    Show a message dialog
    """
    msg = wx.MessageDialog(None, message=message,
                           caption=caption, style=flag)
    msg.ShowModal()
    msg.Destroy()


if __name__ == "__main__":
    app = wx.App(False)
    dlg = RecordDialog(session=None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()