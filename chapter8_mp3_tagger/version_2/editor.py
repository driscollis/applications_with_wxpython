# editor.py

import wx

class Mp3TagEditorDialog(wx.Dialog):

    def __init__(self, mp3):
        title = f'Editing "{mp3.id3.tag.title}"'
        super().__init__(parent=None, title=title)

        self.mp3 = mp3
        self.create_ui()

    def create_ui(self):
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        size = (200, -1)
        track_num = str(self.mp3.id3.tag.track_num[0])
        year = str(self.mp3.id3.tag.best_release_date.year)

        self.track_number = wx.TextCtrl(
            self, value=track_num, size=size)
        self.create_row('Track Number', self.track_number)

        self.artist = wx.TextCtrl(self, value=self.mp3.id3.tag.artist,
                                  size=size)
        self.create_row('Artist', self.artist)

        self.album = wx.TextCtrl(self, value=self.mp3.id3.tag.album,
                                 size=size)
        self.create_row('Album', self.album)

        self.title = wx.TextCtrl(self, value=self.mp3.id3.tag.title,
                                 size=size)
        self.create_row('Title', self.title)

        btn_sizer = wx.BoxSizer()
        save_btn = wx.Button(self, label="Save")
        save_btn.Bind(wx.EVT_BUTTON, self.save)

        btn_sizer.Add(save_btn, 0, wx.ALL, 5)
        btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)

        self.SetSizerAndFit(self.main_sizer)

    def create_row(self, label, text):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_label = wx.StaticText(self, label=label, size=(50, -1))
        widgets = [(row_label, 0, wx.ALL, 5),
                   (text, 0, wx.ALL, 5)]
        sizer.AddMany(widgets)
        self.main_sizer.Add(sizer)

    def save(self, event):
        current_track_num = self.mp3.id3.tag.track_num
        if current_track_num:
            new_track_num = (int(self.track_number.GetValue()),
                             current_track_num[1])
        else:
            new_track_num = (int(self.track_number.GetValue()), 0)

        artist = self.artist.GetValue()
        album = self.album.GetValue()
        title = self.title.GetValue()

        self.mp3.id3.tag.artist = artist if artist else 'Unknown'
        self.mp3.id3.tag.album = album if album else 'Unknown'
        self.mp3.id3.tag.title = title if title else 'Unknown'
        self.mp3.id3.tag.track_num = new_track_num
        self.mp3.id3.tag.save()
        self.mp3.update()
        self.Close()
