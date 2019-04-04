# split_panel.py

import os
import string
import wx

from PyPDF2 import PdfFileReader, PdfFileWriter

wildcard = "PDFs (*.pdf)|*.pdf"


class CharValidator(wx.PyValidator):
    '''
    Validates data as it is entered into the text controls.
    '''

    def __init__(self, flag):
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        '''Required Validator method'''
        return CharValidator(self.flag)

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def OnChar(self, event):
        keycode = int(event.GetKeyCode())
        if keycode < 256:
            key = chr(keycode)
            if self.flag == 'no-alpha' and key in string.ascii_letters:
                return
            if self.flag == 'no-digit' and key in string.digits:
                return
        event.Skip()


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
        pdf_btn.Bind(wx.EVT_BUTTON, self.on_choose)
        row_sizer.Add(pdf_btn, 0, wx.ALL, 5)
        main_sizer.Add(row_sizer, 0, wx.EXPAND)

        # split PDF
        row_sizer = wx.BoxSizer()
        page_lbl = wx.StaticText(self, label='Pages:')
        page_lbl.SetFont(font)
        row_sizer.Add(page_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.pdf_split_options = wx.TextCtrl(
            self, validator=CharValidator('no-alpha'))
        row_sizer.Add(self.pdf_split_options, 0, wx.ALL, 5)
        main_sizer.Add(row_sizer)

        msg = 'Type page numbers and/or page ranges separated by commas.' \
            ' For example: 1, 3 or 4-10. Note you cannot use both commas ' \
            'and dashes.'
        directions_txt = wx.TextCtrl(
            self, value=msg,
            style=wx.TE_MULTILINE | wx.NO_BORDER)
        directions_txt.SetFont(font)
        directions_txt.Disable()
        main_sizer.Add(directions_txt, 0, wx.ALL | wx.EXPAND, 5)

        split_btn = wx.Button(self, label='Split PDF')
        split_btn.Bind(wx.EVT_BUTTON, self.on_split)
        main_sizer.Add(split_btn, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizer(main_sizer)

    def on_choose(self, event):
        path = None
        with wx.FileDialog(
            self, message="Choose a file",
            defaultDir='~',
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
            ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
        if path:
            self.pdf_path.SetValue(path)

    def on_split(self, event):
        output_path = None
        input_pdf = self.pdf_path.GetValue()
        split_options = self.pdf_split_options.GetValue()
        if not input_pdf:
            message='You must choose an input PDF!'
            self.show_message(message)
            return

        if not os.path.exists(input_pdf):
            message = f'Input PDF {input_pdf} does not exist!'
            self.show_message(message)
            return

        if not split_options:
            message = 'You need to choose what page(s) to split off'
            self.show_message(message)
            return

        if ',' in split_options and '-' in split_options:
            message = 'You cannot have both commas and dashes in options'
            self.show_message(message)
            return

        if split_options.count('-') > 1:
            message = 'You can only use one dash'
            self.show_message(message)
            return

        if '-' in split_options:
            page_begin, page_end = split_options.split('-')
            if not page_begin or not page_end:
                message = 'Need both a beginning and ending page'
                self.show_message(message)
                return

        if not any(char.isdigit() for char in split_options):
            message = 'You need to enter a page number to split off'
            self.show_message(message)
            return

        with wx.FileDialog(
            self, message="Choose a file",
            defaultDir='~',
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_SAVE | wx.FD_CHANGE_DIR
            ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                output_path = dlg.GetPath()

        if output_path:
            _, ext = os.path.splitext(output_path)
            if '.pdf' not in ext.lower():
                output_path = f'{output_path}.pdf'
            split_options = split_options.strip()
            self.split(input_pdf, output_path, split_options)

    def split(self, input_pdf, output_path, split_options):
        pdf = PdfFileReader(input_pdf)
        pdf_writer = PdfFileWriter()
        if ',' in split_options:
            pages = [page for page in split_options.split(',')
                     if page]
            for page in pages:
                pdf_writer.addPage(pdf.getPage(int(page)))
        else:
            page_begin, page_end = split_options.split('-')
            page_begin = int(page_begin)
            page_end = int(page_end)
            if page_begin < 0 or page_begin == 1:
                page_begin = 0
            if page_begin > 1:
                # Take off by one error into account
                page_begin -= 1

            for page in range(page_begin, page_end):
                pdf_writer.addPage(pdf.getPage(page))

        # Write PDF to disk
        with open(output_path, 'wb') as out:
            pdf_writer.write(out)

        # Let user know that PDF is split
        message = f'PDF split successfully to {output_path}'
        self.show_message(message, caption='Split Finished',
                          style=wx.ICON_INFORMATION)

    def show_message(self, message, caption='Error', style=wx.ICON_ERROR):
        with wx.MessageDialog(None, message=message,
                              caption=caption,
                              style=style) as dlg:
            dlg.ShowModal()
