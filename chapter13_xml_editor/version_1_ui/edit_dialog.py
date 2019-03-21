import wx

class EditDialog(wx.Dialog):
    """
    Super class to derive attribute and element edit
    dialogs from
    """

    def __init__(self, xml_obj, page_id, title, label_one, label_two):
        """
        @param xml_obj: The lxml XML object
        @param page_id: A unique id based on the current page being viewed
        @param title: The title of the dialog
        @param label_one: The label text for the first text control
        @param label_two: The label text for the second text control
        """
        wx.Dialog.__init__(self, None, title=title)
        self.xml_obj = xml_obj
        self.page_id = page_id

        flex_sizer = wx.FlexGridSizer(2, 2, gap=wx.Size(5, 5))
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        attr_lbl = wx.StaticText(self, label=label_one)
        flex_sizer.Add(attr_lbl, 0, wx.ALL, 5)
        value_lbl = wx.StaticText(self, label=label_two)
        flex_sizer.Add(value_lbl, 0, wx.ALL, 5)

        self.value_one = wx.TextCtrl(self)
        flex_sizer.Add(self.value_one, 1, wx.ALL|wx.EXPAND, 5)
        self.value_two = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.value_two.Bind(wx.EVT_KEY_DOWN, self.on_enter)
        flex_sizer.Add(self.value_two, 1, wx.ALL|wx.EXPAND, 5)
        flex_sizer.AddGrowableCol(1, 1)
        flex_sizer.AddGrowableCol(0, 1)

        save_btn = wx.Button(self, label='Save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(save_btn, 0, wx.ALL|wx.CENTER, 5)

        cancel_btn = wx.Button(self, label='Cancel')
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        btn_sizer.Add(cancel_btn, 0, wx.ALL|wx.CENTER, 5)

        main_sizer.Add(flex_sizer, 0, wx.EXPAND)
        main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(main_sizer)

        self.ShowModal()

    def on_enter(self, event):
        """
        Event handler that fires when a key is pressed in the
        attribute value text control
        """
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER:
            self.on_save(event=None)
        event.Skip()

    def on_cancel(self, event):
        """
        Event handler that is called when the Cancel button is
        pressed.

        Will destroy the dialog
        """
        self.Close()
