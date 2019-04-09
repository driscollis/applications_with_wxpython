# search_thread.py

import os
import subprocess
import time

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
            if '/home/mdriscoll/py/boomslang' in line:
                current_key = line
                results[line] = []
            else:
                results[current_key].append(line)
        end = time.time()
        wx.CallAfter(pub.sendMessage, 'status', search_time=end-start)

