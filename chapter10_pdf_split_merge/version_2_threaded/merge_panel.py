# merge_panel.py

import os
import glob
import wx

from ObjectListView import ObjectListView, ColumnDefn
from pubsub import pub
from pypdf import PdfReader, PdfWriter
from threading import Thread

wildcard = "PDFs (*.pdf)|*.pdf"


class MergeThread(Thread):

    def __init__(self, objects, output_path):
        super().__init__()
        self.objects = objects
        self.output_path = output_path
        self.start()

    def run(self):
        pdf_writer = PdfWriter()
        page_count = 1

        for obj in self.objects:
            pdf_reader = PdfReader(obj.full_path)
            for page in range(pdf_reader.get_num_pages()):
                pdf_writer.add_page(pdf_reader.get_page(page))
                wx.CallAfter(pub.sendMessage, 'update',
                             msg=page_count)
                page_count += 1

        # All pages are added, so write it to disk
        with open(self.output_path, 'wb') as fh:
            pdf_writer.write(fh)

        wx.CallAfter(pub.sendMessage, 'close')


class MergeGauge(wx.Gauge):

    def __init__(self, parent, range):
        super().__init__(parent, range=range)

        pub.subscribe(self.update_progress, "update")

    def update_progress(self, msg):
        self.SetValue(msg)


class MergeProgressDialog(wx.Dialog):

    def __init__(self, objects, path):
        super().__init__(None, title='Merging Progress')
        pub.subscribe(self.close, "close")

        sizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(self, label='Merging PDFS')
        sizer.Add(lbl, 0, wx.ALL | wx.CENTER, 5)
        total_page_count = sum([int(obj.number_of_pages)
                                for obj in objects])
        gauge = MergeGauge(self, total_page_count)
        sizer.Add(gauge, 0, wx.ALL | wx.EXPAND, 5)

        MergeThread(objects, output_path=path)
        self.SetSizer(sizer)

    def close(self):
        self.Close()


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
                pdf = PdfReader(f)
                number_of_pages = pdf.get_num_pages()
        except:
            number_of_pages = 0
        self.number_of_pages = str(number_of_pages)


class MergePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.pdfs = []
        drop_target = DropTarget(self)
        self.SetDropTarget(drop_target)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.create_ui()

    def create_ui(self):
        btn_sizer = wx.BoxSizer()
        add_btn = wx.Button(self, label='Add')
        add_btn.Bind(wx.EVT_BUTTON, self.on_add_file)
        btn_sizer.Add(add_btn, 0, wx.ALL, 5)
        remove_btn = wx.Button(self, label='Remove')
        remove_btn.Bind(wx.EVT_BUTTON, self.on_remove)
        btn_sizer.Add(remove_btn, 0, wx.ALL, 5)
        self.main_sizer.Add(btn_sizer)

        move_btn_sizer = wx.BoxSizer(wx.VERTICAL)
        row_sizer = wx.BoxSizer()

        self.pdf_olv = ObjectListView(
            self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.pdf_olv.SetEmptyListMsg("No PDFs Loaded")
        self.update_pdfs()
        row_sizer.Add(self.pdf_olv, 1, wx.ALL | wx.EXPAND)

        move_up_btn = wx.Button(self, label='Up')
        move_up_btn.Bind(wx.EVT_BUTTON, self.on_move)
        move_btn_sizer.Add(move_up_btn, 0, wx.ALL, 5)
        move_down_btn = wx.Button(self, label='Down')
        move_down_btn.Bind(wx.EVT_BUTTON, self.on_move)
        move_btn_sizer.Add(move_down_btn, 0, wx.ALL, 5)
        row_sizer.Add(move_btn_sizer)

        self.main_sizer.Add(row_sizer, 1, wx.ALL | wx.EXPAND, 5)

        merge_pdfs = wx.Button(self, label='Merge PDFs')
        merge_pdfs.Bind(wx.EVT_BUTTON, self.on_merge)
        self.main_sizer.Add(merge_pdfs, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(self.main_sizer)

    def add_pdf(self, path):
        self.pdfs.append(Pdf(path))

    def load_pdfs(self, path):
        pdf_paths = glob.glob(path + '/*.pdf')
        for path in pdf_paths:
            self.add_pdf(path)
        self.update_pdfs()

    def on_merge(self, event):
        objects = self.pdf_olv.GetObjects()
        if len(objects) < 2:
            with wx.MessageDialog(
                None,
                message='You need 2 or more files to merge!',
                caption='Error',
                style= wx.ICON_INFORMATION) as dlg:
                dlg.ShowModal()
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
            self.merge(path, objects)

    def merge(self, output_path, objects):
        with MergeProgressDialog(objects, output_path) as dlg:
            dlg.ShowModal()

        with wx.MessageDialog(None, message='Save completed!',
                              caption='Save Finished',
                             style= wx.ICON_INFORMATION) as dlg:
            dlg.ShowModal()

    def on_add_file(self, event):
        paths = None
        with wx.FileDialog(
            self, message="Choose a file",
            defaultDir='~',
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE
            ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                paths = dlg.GetPaths()
        if paths:
            for path in paths:
                self.add_pdf(path)
            self.update_pdfs()

    def on_move(self, event):
        btn = event.GetEventObject()
        label = btn.GetLabel()
        current_selection = self.pdf_olv.GetSelectedObject()
        data = self.pdf_olv.GetObjects()
        if current_selection:
            index = data.index(current_selection)
            new_index = self.get_new_index(
                label.lower(), index, data)
            data.insert(new_index, data.pop(index))
            self.pdfs = data
            self.update_pdfs()
            self.pdf_olv.Select(new_index)

    def on_remove(self, event):
        current_selection = self.pdf_olv.GetSelectedObject()
        if current_selection:
            index = self.pdfs.index(current_selection)
            self.pdfs.pop(index)
            self.pdf_olv.RemoveObject(current_selection)

    def get_new_index(self, direction, index, data):
        if direction == 'up':
            if index > 0:
                new_index = index - 1
            else:
                new_index = len(data)-1
        else:
            if index < len(data) - 1:
                new_index = index + 1
            else:
                new_index = 0
        return new_index

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
