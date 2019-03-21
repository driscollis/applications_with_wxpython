import wx
import wx.stc as stc

class XmlSTC(stc.StyledTextCtrl):

    def __init__(self, parent, xml_file):
        stc.StyledTextCtrl.__init__(self, parent)

        self.SetLexer(stc.STC_LEX_XML)
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                          "size:12,face:Courier New")
        faces = { 'mono' : 'Courier New',
                  'helv' : 'Arial',
                  'size' : 12,
                  }

        # XML styles
        # Default
        self.StyleSetSpec(stc.STC_H_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)

        # Number
        self.StyleSetSpec(stc.STC_H_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        # Tag
        self.StyleSetSpec(stc.STC_H_TAG, "fore:#007F7F,bold,size:%(size)d" % faces)
        # Value
        self.StyleSetSpec(stc.STC_H_VALUE, "fore:#7F0000,size:%(size)d" % faces)
        # Attribute
        self.StyleSetSpec(stc.STC_H_ATTRIBUTE, "fore:#FF5733,size:%(size)d" % faces)

        with open(xml_file) as fobj:
            text = fobj.read()

        self.SetText(text)


class XmlViewer(wx.Dialog):

    def __init__(self, xml_file):
        wx.Dialog.__init__(self, parent=None, title='XML Viewer',
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.xml_view = XmlSTC(self, xml_file)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.xml_view, 1, wx.EXPAND)
        self.SetSizer(sizer)

