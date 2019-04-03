import wx


class SplitPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        row_sizer = wx.BoxSizer()
        lbl = wx.StaticText(self, label='Input PDF:')
        row_sizer.Add(lbl, 0, wx.ALL, 5)
        self.pdf_path = wx.TextCtrl(self, style=wx.TE_READONLY)
        row_sizer.Add(self.pdf_path, 1, wx.EXPAND | wx.ALL, 5)
        pdf_btn = wx.Button(self, label='Open PDF')
        row_sizer.Add(pdf_btn, 0, wx.ALL, 5)
        main_sizer.Add(row_sizer, 0, wx.EXPAND)

        # split PDF into one page per PDF

        # split PDF
        row_sizer = wx.BoxSizer()
        msg = 'Specify which pages are to be split out (Ex 1, 2 or 5-10)'
        page_lbl = wx.StaticText(self, label=msg)
        row_sizer.Add(page_lbl, 0, wx.ALL, 5)
        self.pdf_split_options = wx.TextCtrl(self)
        row_sizer.Add(self.pdf_split_options, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(row_sizer, 0, wx.EXPAND)

        split_btn = wx.Button(self, label='Split PDF')
        main_sizer.Add(split_btn, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizer(main_sizer)