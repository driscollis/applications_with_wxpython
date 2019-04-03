import os
import wx


class SplitPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        row_sizer = wx.BoxSizer()
        lbl = wx.StaticText(self, label='Input PDF:')
        lbl.SetFont(font)
        row_sizer.Add(lbl, 0, wx.ALL | wx.CENTER, 5)
        self.pdf_path = wx.TextCtrl(self, style=wx.TE_READONLY)
        row_sizer.Add(self.pdf_path, 1, wx.EXPAND | wx.ALL, 5)
        pdf_btn = wx.Button(self, label='Open PDF')
        row_sizer.Add(pdf_btn, 0, wx.ALL, 5)
        main_sizer.Add(row_sizer, 0, wx.EXPAND)

        # split PDF
        row_sizer = wx.BoxSizer()
        page_lbl = wx.StaticText(self, label='Pages:')
        page_lbl.SetFont(font)
        row_sizer.Add(page_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.pdf_split_options = wx.TextCtrl(self)
        row_sizer.Add(self.pdf_split_options, 0, wx.ALL, 5)
        main_sizer.Add(row_sizer)

        msg = 'Type page numbers and/or page ranges separated by commas.' \
            ' For example: 1, 3 or 4-10. Note you cannot use both commas ' \
            'and dashes.'
        self.directions_lbl = wx.TextCtrl(
            self, value=msg,
            style=wx.TE_MULTILINE | wx.NO_BORDER)
        self.directions_lbl.SetFont(font)
        self.directions_lbl.Disable()
        main_sizer.Add(self.directions_lbl, 0, wx.ALL | wx.EXPAND, 5)

        split_btn = wx.Button(self, label='Split PDF')
        split_btn.Bind(wx.EVT_BUTTON, self.on_split)
        main_sizer.Add(split_btn, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizer(main_sizer)

    def on_choose(self, event):
        pass

    def on_split(self, event):
        input_pdf = self.pdf_path.GetValue()
        split_options = self.pdf_split_options.GetValue()
        if not input_pdf:
            with wx.MessageDialog(
                None, message='You must choose an input PDF!',
                caption='Error',
                style= wx.ICON_ERROR) as dlg:
                dlg.ShowModal()
            return

        if not os.path.exists(input_pdf):
            message = f'Input PDF {input_pdf} does not exist!'
            with wx.MessageDialog(
                None, message=message,
                caption='Error',
                style= wx.ICON_ERROR) as dlg:
                dlg.ShowModal()
            return

        if ',' in split_options and '-' in split_options:
            message = 'You cannot have both commas and dashes in options'
            with wx.MessageDialog(
                None, message=message,
                caption='Error',
                style= wx.ICON_ERROR) as dlg:
                dlg.ShowModal()
            return

        self.split(input_pdf, split_options)

    def split(self, input_pdf, split_options):
        pass
