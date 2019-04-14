# ftp_client.py

import ftplib
import sys
import time
import wx

from ftp_threads import FTPThread
from ObjectListView import ObjectListView, ColumnDefn
from pubsub import pub


class FtpPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        self.ftp = None
        self.paths = []

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.create_ui()
        self.SetSizer(self.main_sizer)
        pub.subscribe(self.update, 'update')
        pub.subscribe(self.update_status, 'update_status')

    def create_ui(self):
        size = (150, -1)
        connect_sizer = wx.BoxSizer()
        # host, username, password, port, connect button or combo
        host_lbl = wx.StaticText(self, label='Host:')
        connect_sizer.Add(host_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.host = wx.TextCtrl(self, size=size)
        connect_sizer.Add(self.host, 0, wx.ALL, 5)

        user_lbl = wx.StaticText(self, label='Username:')
        connect_sizer.Add(user_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.user = wx.TextCtrl(self, size=size)
        connect_sizer.Add(self.user, 0, wx.ALL, 5)

        password_lbl = wx.StaticText(self, label='Password:')
        connect_sizer.Add(password_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.password = wx.TextCtrl(self, size=size, style=wx.TE_PASSWORD)
        connect_sizer.Add(self.password, 0, wx.ALL, 5)

        port_lbl = wx.StaticText(self, label='Port:')
        connect_sizer.Add(port_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.port = wx.TextCtrl(self, value='21', size=(50, -1))
        connect_sizer.Add(self.port, 0, wx.ALL, 5)

        connect_btn = wx.Button(self, label='Connect')
        connect_btn.Bind(wx.EVT_BUTTON, self.on_connect)
        connect_sizer.Add(connect_btn, 0, wx.ALL, 5)

        self.main_sizer.Add(connect_sizer)

        self.status = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.main_sizer.Add(self.status, 1, wx.ALL | wx.EXPAND, 5)

        folder_ico = wx.ArtProvider.GetBitmap(
            wx.ART_FOLDER, wx.ART_TOOLBAR, (16, 16))
        file_ico = wx.ArtProvider.GetBitmap(
            wx.ART_HELP_PAGE, wx.ART_TOOLBAR, (16, 16))

        self.remote_server = ObjectListView(
            self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.remote_server.Bind(wx.EVT_LIST_ITEM_ACTIVATED,
                                self.on_change_directory)
        self.remote_server.AddNamedImages('folder', smallImage=folder_ico)
        self.remote_server.AddNamedImages('file', smallImage=file_ico)
        self.remote_server.SetEmptyListMsg("Not Connected")
        self.main_sizer.Add(self.remote_server, 2, wx.ALL | wx.EXPAND, 5)
        self.update_ui()

    def on_connect(self, event):
        host = self.host.GetValue()
        username = self.user.GetValue()
        password = self.password.GetValue()
        port = int(self.port.GetValue())

        if host and username and password and port:
            self.ftp = ftplib.FTP()
            self.ftp.set_debuglevel(1)
            self.ftp.connect(host, port)
            self.ftp.login(username, password)
            self.update_status(self.ftp.getwelcome())
            thread = FTPThread(self.ftp)

    def image_getter(self, path):
        if path.folder:
            return "folder"
        else:
            return "file"

    def on_change_directory(self, event):
        current_selection = self.remote_server.GetSelectedObject()
        if current_selection.folder:
            thread = FTPThread(self.ftp, current_selection.filename)

    def update(self, paths):
        """
        Called by pubsub / thread
        """
        self.paths = paths
        self.update_ui()

    def update_status(self, message):
        ts = time.strftime(time.strftime('%H:%M:%S',
                                         time.gmtime(time.time()
                                                     )
                                         )
                           )
        if '\n' in message:
            for line in message.split('\n'):
                line = f'{ts} {line}'
                self.status.WriteText(f'{line}\n')
        else:
            message = f'{ts} {message}'
            self.status.WriteText(f'{message}\n')

    def update_ui(self):
        self.remote_server.SetColumns([
            ColumnDefn("File/Folder", "left", 800, "filename",
                       imageGetter=self.image_getter),
            ColumnDefn("Filesize", "right", 80, "size"),
            ColumnDefn("Last Modified", "left", 150, "last_modified")
        ])
        self.remote_server.SetObjects(self.paths)


class FtpFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title='PythonFTP', size=(1200, 600))
        panel = FtpPanel(self)
        self.create_toolbar()
        self.Show()

    def create_toolbar(self):
        self.toolbar = self.CreateToolBar()

        add_ico = wx.ArtProvider.GetBitmap(
            wx.ART_GO_UP, wx.ART_TOOLBAR, (16, 16))
        add_file_tool = self.toolbar.AddTool(
            wx.ID_ANY, 'Upload File', add_ico,
            'Upload a file')
        self.Bind(wx.EVT_MENU, self.on_upload_file,
                  add_file_tool)

        add_ico = wx.ArtProvider.GetBitmap(
            wx.ART_GO_DOWN, wx.ART_TOOLBAR, (16, 16))
        add_file_tool = self.toolbar.AddTool(
            wx.ID_ANY, 'Download File', add_ico,
            'Download a file')
        self.Bind(wx.EVT_MENU, self.on_download_file,
                  add_file_tool)

        remove_ico = wx.ArtProvider.GetBitmap(
            wx.ART_MINUS, wx.ART_TOOLBAR, (16, 16))
        remove_tool = self.toolbar.AddTool(
            wx.ID_ANY, 'Remove File', remove_ico,
            'Remove file')
        self.Bind(wx.EVT_MENU, self.on_remove, remove_tool)

        self.toolbar.Realize()

    def on_upload_file(self, event):
        pass

    def on_download_file(self, event):
        pass

    def on_remove(self, event):
        pass


if __name__ == '__main__':
    app = wx.App(False)
    frame = FtpFrame()
    app.MainLoop()