# ftp_client.py

import wx

class FtpPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

    def create_ui(self):
        # host, username, password, port, connect button or combo

        # split for local vs remote
        pass


class FtpFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title='PythonFTP')
        panel = FtpPanel(self)
        self.Show()

if __name__ == '__main__':
    app = wx.App(False)
    frame = FtpFrame()
    app.MainLoop()