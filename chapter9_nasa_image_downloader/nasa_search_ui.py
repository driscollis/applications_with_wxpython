import wx


class MainPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)


class SearchFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title='NASA Search')
        panel = MainPanel(self)
        self.Show()

if __name__ == '__main__':
    app = wx.App(False)
    frame = SearchFrame()
    app.MainLoop()