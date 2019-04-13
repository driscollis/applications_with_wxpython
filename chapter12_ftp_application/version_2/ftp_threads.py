# ftp_threads.py

import os
import wx

from pubsub import pub
from threading import Thread

def send_status(message):
    wx.CallAfter(pub.sendMessage,
                 'update_status',
                 message=message)


class Path:

    def __init__(self, ftype, size, filename, date):
        if 'd' in ftype:
            self.folder = True
        else:
            self.folder = False
        self.size = size
        self.filename = filename
        self.last_modified = f'{date}'


class FTPThread(Thread):

    def __init__(self, ftp, folder=None):
        super().__init__()
        self.ftp = ftp
        self.folder = folder
        self.start()

    def run(self):
        if self.folder:
            self.ftp.cwd(self.folder)
            message = f'Changing directory: {self.folder}'
            send_status(message)
        self.get_dir_listing()

    def get_dir_listing(self):
        data = []
        contents = self.ftp.dir(data.append)
        self.parse_data(data)

    def parse_data(self, data):
        paths = []
        for item in data:
            parts = item.split()
            ftype = parts[0]
            size = parts[4]
            filename = parts[8]
            date = '{month} {day} {t}'.format(
                month=parts[5], day=parts[6], t=parts[7])
            if filename == '.':
                # Skip this one
                continue
            paths.append(Path(ftype, size, filename, date))

        wx.CallAfter(pub.sendMessage,
                     'update',
                     paths=paths)

class DownloadThread(Thread):

    def __init__(self, ftp, local_folder, paths):
        super().__init__()
        self.ftp = ftp
        self.output = local_folder
        self.paths = paths
        self.start()

    def run(self):
        for path in self.paths:
            try:
                with open(self.output, 'wb') as local_file:
                    ftp.retrbinary('RETR ' + path, local_file.write)
                    message = f'Downloaded: {path}'
                    send_status(message)
            except ftplib.error_perm:
                message = f'ERROR: Unable to download {path}'
                send_status(message)

class UploadFileThread(Thread):

    def __init__(self, ftp, local_folder, paths):
        super().__init__()
        self.ftp = ftp
        self.output = local_folder
        self.paths = paths
        self.start()

    def run(self):
        txt_files = [".txt", ".htm", ".html"]
        for path in paths:
            _, ext = os.path.splitext(path)

            if ext in txt_files:
                with open(path) as fobj:
                    self.ftp.storlines('STOR ' + path, fobj)
            else:
                with open(path, 'rb') as fobj:
                    self.ftp.storbinary('STOR ' + path, fobj, 1024)
