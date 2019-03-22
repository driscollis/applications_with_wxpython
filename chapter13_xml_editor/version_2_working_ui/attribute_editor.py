import wx

from attribute_dialog import AttributeDialog
from functools import partial
from pubsub import pub


class State():
    """
    Class for keeping track of the state of the key portion
    of the attribute
    """

    def __init__(self, key, val_widget):
        self.current_key = key
        self.previous_key = None
        self.val_widget = val_widget


class AttributeEditorPanel(wx.Panel):
    """
    A class that holds all UI elements for editing
    XML attribute elements
    """

    def __init__(self, parent, page_id):
        wx.Panel.__init__(self, parent)
        self.page_id = page_id
        self.xml_obj = None
        self.widgets = []

        pub.subscribe(self.update_ui, 'ui_updater_{}'.format(self.page_id))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

    def update_ui(self, xml_obj):
        """
        Update the user interface to have elements for editing
        XML attributes

        Called via pubsub
        """
        self.clear()
        self.xml_obj = xml_obj

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        attr_lbl = wx.StaticText(self, label='Attribute')
        value_lbl = wx.StaticText(self, label='Value')
        sizer.Add(attr_lbl, 0, wx.ALL, 5)
        sizer.Add((133,0))
        sizer.Add(value_lbl, 0, wx.ALL, 5)
        self.widgets.extend([attr_lbl, value_lbl])

        self.main_sizer.Add(sizer)

        for key in xml_obj.attrib:
            _ = wx.BoxSizer(wx.HORIZONTAL)
            attr_name = wx.TextCtrl(self, value=key)
            _.Add(attr_name, 1, wx.ALL|wx.EXPAND, 5)
            self.widgets.append(attr_name)

            val = str(xml_obj.attrib[key])
            attr_val = wx.TextCtrl(self, value=val)
            _.Add(attr_val, 1, wx.ALL|wx.EXPAND, 5)

            # keep track of the attribute text control's state
            attr_state = State(key, attr_val)

            attr_name.Bind(
                wx.EVT_TEXT, partial(
                    self.on_key_change, state=attr_state))
            attr_val.Bind(
                wx.EVT_TEXT, partial(
                    self.on_val_change,
                    attr=attr_name
                ))

            self.widgets.append(attr_val)
            self.main_sizer.Add(_, 0, wx.EXPAND)
        else:
            add_attr_btn = wx.Button(self, label='Add Attribute')
            add_attr_btn.Bind(wx.EVT_BUTTON, self.on_add_attr)
            self.main_sizer.Add(add_attr_btn, 0, wx.ALL|wx.CENTER, 5)
            self.widgets.append(add_attr_btn)

        self.Layout()

    def on_add_attr(self, event):
        """
        Event handler to add an attribute
        """
        dlg = AttributeDialog(
            self.xml_obj,
            page_id=self.page_id,
            title = 'Add Attribute',
            label_one = 'Attribute',
            label_two = 'Value'
        )
        dlg.Destroy()

    def clear(self):
        """
        Clears the panel of widgets
        """
        sizers = {}
        for widget in self.widgets:
            sizer = widget.GetContainingSizer()
            if sizer:
                sizer_id = id(sizer)
                if sizer_id not in sizers:
                    sizers[sizer_id] = sizer
            widget.Destroy()

        for sizer in sizers:
            self.main_sizer.Remove(sizers[sizer])

        self.widgets = []
        self.Layout()

    def on_key_change(self, event, state):
        """
        Event handler that is called on text change in the
        attribute key field
        """
        new_key = event.GetString()
        if new_key not in self.xml_obj.attrib:
            if state.current_key in self.xml_obj.attrib:
                self.xml_obj.attrib.pop(state.current_key)
            self.xml_obj.attrib[new_key] = state.val_widget.GetValue()
            state.previous_key = state.current_key
            state.current_key = new_key

    def on_val_change(self, event, attr):
        """
        Event handler that is called on text change in the
        attribute value field
        """
        new_val = event.GetString()
        self.xml_obj.attrib[attr.GetValue()] = new_val

