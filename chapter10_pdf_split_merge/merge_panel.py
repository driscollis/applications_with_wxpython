# merge_panel.py

import os
import wx

from ObjectListView import ObjectListView, ColumnDefn
from pubsub import pub
from PyPDF2 import PdfFileReader, PdfFileWriter

wildcard = "PDFs (*.pdf)|*.pdf"


class DropTarget(wx.FileDropTarget):

    def __init__(self, window):
        super().__init__()
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        self.window.update_on_drop(filenames)
        return True


class Pdf:

    def __init__(self, pdf_path):
        self.full_path = pdf_path
        self.filename = os.path.basename(pdf_path)
        try:
            with open(pdf_path, 'rb') as f:
                pdf = PdfFileReader(f)
                number_of_pages = pdf.getNumPages()
        except:
            number_of_pages = 0
        self.number_of_pages = str(number_of_pages)


class MergePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.pdfs = []
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        pub.subscribe(self.add_pdf_from_menu, 'pdf_path')

        self.pdf_olv = ObjectListView(
            self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.pdf_olv.SetEmptyListMsg("No PDFs Loaded")
        self.update_pdfs()
        main_sizer.Add(self.pdf_olv, 1, wx.ALL | wx.EXPAND, 5)

        merge_pdfs = wx.Button(self, label='Merge PDFs')
        merge_pdfs.Bind(wx.EVT_BUTTON, self.on_merge)
        main_sizer.Add(merge_pdfs, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(main_sizer)

    def add_pdf(self, path):
        self.pdfs.append(Pdf(path))

    def add_pdf_from_menu(self, paths):
        for path in paths:
            self.add_pdf(path)
        self.update_pdfs()

    def load_pdfs(self, path):
        pdf_paths = glob.glob(path + '/*.pdf')
        for path in pdf_paths:
            self.add_pdf(path)
        self.update_pdfs()

    def on_merge(self, event):
        """
        TODO - Move this into a thread
        """
        objects = self.pdf_olv.GetObjects()
        if len(objects) < 2:
            print('Need more than one PDF to merge!')
            return
        with wx.FileDialog(
            self, message="Choose a file",
            defaultDir='~',
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_SAVE | wx.FD_CHANGE_DIR
            ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
        if path:
            _, ext = os.path.splitext(path)
            if '.pdf' not in ext.lower():
                path = f'{path}.pdf'
            self.merge(path)

    def merge(self, output_path):
        pdf_writer = PdfFileWriter()

        objects = self.pdf_olv.GetObjects()

        for obj in objects:
            pdf_reader = PdfFileReader(obj.full_path)
            for page in range(pdf_reader.getNumPages()):
                pdf_writer.addPage(pdf_reader.getPage(page))

        with open(output_path, 'wb') as fh:
            pdf_writer.write(fh)

    def update_on_drop(self, paths):
        for path in paths:
            _, ext = os.path.splitext(path)
            if os.path.isdir(path):
                self.load_pdfs(path)
            elif os.path.isfile(path) and ext.lower() == '.mp3':
                self.add_pdf(path)
                self.update_pdfs()

    def update_pdfs(self):
        self.pdf_olv.SetColumns([
            ColumnDefn("PDF Name", "left", 200, "filename"),
            ColumnDefn("Full Path", "left", 250, "full_path"),
            ColumnDefn("Page Count", "left", 100, "number_of_pages")
        ])
        self.pdf_olv.SetObjects(self.pdfs)