import ftplib
import os
import wx

from model import Path
from pubsub import pub

def send_status(message, topic='update_status'):
    wx.CallAfter(pub.sendMessage,
                 topic,
                 message=message)


class FTP:

    def __init__(self, folder=None):
        self.folder = folder

    def connect(self, host, port, username, password):
        try:
            self.ftp = ftplib.FTP()
            self.ftp.connect(host, port)
            self.ftp.login(username, password)
            send_status(self.ftp.getwelcome())
            send_status('Connected', topic='update_statusbar')
            self.get_dir_listing()
        except:
            send_status('Disconnected', topic='update_statusbar')

    def disconnect(self):
        self.ftp.quit()

    def change_directory(self, folder):
        self.ftp.cwd(folder)
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

    def delete_file(self, filename):
        try:
            self.ftp.sendcmd(f'DELE {filename}')
            send_status(f'{filename} deleted successfully')
        except:
            send_status(f'Unable to delete {filename}')

    def download_files(self, paths, local_folder):
        for path in paths:
            try:
                full_path = os.path.join(local_folder, path)
                with open(full_path, 'wb') as local_file:
                    ftp.retrbinary('RETR ' + path, local_file.write)
                    message = f'Downloaded: {path}'
                    send_status(message)
            except ftplib.error_perm:
                message = f'ERROR: Unable to download {path}'
                send_status(message)

    def upload_files(self, paths):
        txt_files = [".txt", ".htm", ".html"]
        for path in paths:
            _, ext = os.path.splitext(path)

            if ext in txt_files:
                with open(path) as fobj:
                    self.ftp.storlines('STOR ' + path, fobj)
            else:
                with open(path, 'rb') as fobj:
                    self.ftp.storbinary('STOR ' + path, fobj, 1024)
            send_status(f'Uploaded {path}')
        count = len(paths)
        send_status(f'{count} file(s) uploaded successfully')
