# search_thread.py

import os
import subprocess
import time
import wx

from configparser import ConfigParser
from pubsub import pub
from threading import Thread


class SearchThread(Thread):

    def __init__(self, folder, search_term):
        super().__init__()
        self.folder = folder
        self.search_term = search_term
        module_path = os.path.dirname(os.path.abspath( __file__ ))
        self.config = os.path.join(module_path, 'config.ini')
        self.start()

    def run(self):
        start = time.time()
        config = ConfigParser()
        config.read(self.config)
        grin = config.get("Settings", "grin")
        cmd = [grin, self.search_term, self.folder]
        output = subprocess.check_output(cmd, encoding='UTF-8')
        current_key = ''
        results = {}
        for line in output.split('\n'):
            if self.folder in line:
                # Remove the colon off the end of the line
                current_key = line[:-1]
                results[current_key] = []
            elif not current_key:
                # key not set, so skip it
                continue
            else:
                results[current_key].append(line)
        end = time.time()
        wx.CallAfter(pub.sendMessage,
                     'update',
                     results=results)
        wx.CallAfter(pub.sendMessage, 'status', search_time=end-start)

