# search_threads.py

import os
import time
import wx

from pubsub import pub
from threading import Thread


class SearchFolderThread(Thread):

    def __init__(self, folder, search_term, file_type, case_sensitive):
        super().__init__()
        self.folder = folder
        self.search_term = search_term
        self.file_type = file_type
        self.case_sensitive = case_sensitive
        self.start()

    def run(self):
        start = time.time()
        for entry in os.scandir(self.folder):
            if entry.is_file():
                if self.case_sensitive:
                    path = entry.path
                else:
                    path = entry.path.lower()

                if self.search_term in path:
                    _, ext = os.path.splitext(entry.path)
                    if self.file_type and self.file_type == ext.lower():
                        data = (entry.path, entry.stat().st_mtime)
                        wx.CallAfter(pub.sendMessage,
                                     'update', result=data)
                    else:
                        data = (entry.path, entry.stat().st_mtime)
                        wx.CallAfter(pub.sendMessage,
                                     'update', result=data)
        end = time.time()
        wx.CallAfter(pub.sendMessage, 'status', search_time=end-start)


class SearchSubdirectoriesThread(Thread):

    def __init__(self, folder, search_term, file_type, case_sensitive):
        super().__init__()
        self.folder = folder
        self.search_term = search_term
        self.file_type = file_type
        self.case_sensitive = case_sensitive
        self.start()

    def run(self):
        start = time.time()
        for root, dirs, files in os.walk(self.folder):
            for f in files:
                full_path = os.path.join(root, f)
                if not self.case_sensitive:
                    full_path = full_path.lower()

                if self.search_term in full_path and os.path.exists(full_path):
                    _, ext = os.path.splitext(full_path
                                              )
                    if self.file_type and self.file_type == ext.lower():
                        data = (full_path, os.stat(full_path).st_mtime)
                        wx.CallAfter(pub.sendMessage,
                                     'update', result=data)
                    else:
                        data = (full_path, os.stat(full_path).st_mtime)
                        wx.CallAfter(pub.sendMessage,
                                     'update', result=data)
        end = time.time()
        wx.CallAfter(pub.sendMessage, 'status', search_time=end-start)