import os
import wx
import wx.adv
import wx.lib.scrolledpanel as scrolled

from lxml import objectify
from pubsub import pub
from wx.lib.wordwrap import wordwrap

wildcard = "XML (*.xml)|*.xml|" \
"All files (*.*)|*.*"

class XmlTree(wx.TreeCtrl):

    def __init__(self, parent, id, pos, size, style):
        super().__init__(parent, id, pos, size, style)
        self.page_id = parent.page_id
        self.expanded= {}

        self.xml_root = objectify.fromstring(parent.xml)

        root = self.AddRoot(self.xml_root.tag)
        self.SetItemData(root, ('key', 'value'))

        wx.CallAfter(pub.sendMessage,
                     'ui_updater_{}'.format(self.page_id),
                     xml_obj=self.xml_root)

        if self.xml_root.getchildren():
            for top_level_item in self.xml_root.getchildren():
                child = self.AppendItem(root, top_level_item.tag)
                if top_level_item.getchildren():
                    self.SetItemHasChildren(child)
                self.SetItemData(child, top_level_item)

        self.Expand(root)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.onItemExpanding)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection)

    def onItemExpanding(self, event):
        item = event.GetItem()
        xml_obj = self.GetItemData(item)

        if id(xml_obj) not in self.expanded and xml_obj is not None:
            for top_level_item in xml_obj.getchildren():
                child = self.AppendItem(item, top_level_item.tag)
                self.SetItemData(child, top_level_item)
                if top_level_item.getchildren():
                    self.SetItemHasChildren(child)

        self.expanded[id(xml_obj)] = ''

    def on_tree_selection(self, event):
        """
        A handler that fires when an item in the tree is selected
        This will cause an update to be sent to the XmlEditorPanel
        to allow editing of the XML
        """
        item = event.GetItem()
        xml_obj = self.GetItemData(item)
        if xml_obj is not None and hasattr(xml_obj, 'getchildren'):
            pub.sendMessage('ui_updater_{}'.format(self.page_id),
                            xml_obj=xml_obj)

class AttributeEditorPanel(wx.Panel):

    def __init__(self, parent, page_id):
        super().__init__(parent)
        self.page_id = page_id
        self.widgets = []
        pub.subscribe(self.update_ui,
                      'ui_updater_{}'.format(self.page_id))
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
        sizer.Add(0, 55, 0)
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

            self.widgets.append(attr_val)
            self.main_sizer.Add(_, 0, wx.EXPAND)

        add_attr_btn = wx.Button(self, label='Add Attribute')
        add_attr_btn.Bind(wx.EVT_BUTTON, self.on_add_attr)
        self.main_sizer.Add(add_attr_btn, 0, wx.ALL|wx.CENTER, 5)
        self.widgets.append(add_attr_btn)

        self.Layout()

    def on_add_attr(self, event):
        pass

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

class XmlEditorPanel(scrolled.ScrolledPanel):
    """
    The panel in the notebook that allows editing of XML
    element values
    """

    def __init__(self, parent, page_id):
        """Constructor"""
        scrolled.ScrolledPanel.__init__(
            self, parent, style=wx.SUNKEN_BORDER)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.widgets = []
        self.page_id = page_id
        pub.subscribe(self.update_ui,
                      'ui_updater_{}'.format(self.page_id))

        self.SetSizer(self.main_sizer)

    def update_ui(self, xml_obj):
        """
        Update the panel's user interface based on the data
        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.clear()

        tag_lbl = wx.StaticText(self, label='Tag', size=(25, 25))
        value_lbl = wx.StaticText(self, label='Value')
        sizer.Add(tag_lbl, 0, wx.ALL, 5)
        sizer.Add(0, 55, 0)
        sizer.Add(value_lbl, 0, wx.ALL, 5)
        self.main_sizer.Add(sizer)

        self.widgets.extend([tag_lbl, value_lbl])

        if xml_obj is not None:
            lbl_size = (75, 25)
            for child in xml_obj.getchildren():
                if child.getchildren():
                    continue
                sizer = wx.BoxSizer(wx.HORIZONTAL)
                tag_txt = wx.StaticText(
                    self, label=child.tag, size=lbl_size)
                sizer.Add(tag_txt, 0, wx.ALL, 5)
                self.widgets.append(tag_txt)

                text = child.text if child.text else ''

                value_txt = wx.TextCtrl(self, value=text)
                sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
                self.widgets.append(value_txt)

                self.main_sizer.Add(sizer, 0, wx.EXPAND)

            if getattr(xml_obj, 'tag') and getattr(xml_obj, 'text'):
                if xml_obj.getchildren() == []:
                    self.add_single_tag_elements(xml_obj, lbl_size)

            add_node_btn = wx.Button(self, label='Add Node')
            add_node_btn.Bind(wx.EVT_BUTTON, self.on_add_node)
            self.main_sizer.Add(add_node_btn, 0, wx.ALL|wx.CENTER, 5)
            self.widgets.append(add_node_btn)

            self.SetAutoLayout(1)
            self.SetupScrolling()

    def add_single_tag_elements(self, xml_obj, lbl_size):
        """
        Adds the single tag elements to the panel
        This function is only called when there should be just one
        tag / value
        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        tag_txt = wx.StaticText(self, label=xml_obj.tag, size=lbl_size)
        sizer.Add(tag_txt, 0, wx.ALL, 5)
        self.widgets.append(tag_txt)

        value_txt = wx.TextCtrl(self, value=xml_obj.text)
        sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
        self.widgets.append(value_txt)
        self.main_sizer.Add(sizer, 0, wx.EXPAND)

    def clear(self):
        """
        Clears the widgets from the panel in preparation for an update
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

    def on_add_node(self, event):
        pub.sendMessage(f'add_node_{self.page_id}')


class TreePanel(wx.Panel):

    def __init__(self, parent, page_id, xml):
        super().__init__(parent)

        self.page_id = page_id
        self.xml = xml

        self.tree = XmlTree(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            wx.TR_HAS_BUTTONS)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND)
        self.SetSizer(sizer)

class EditorPanel(wx.Panel):

    def __init__(self, parent, size):
        super().__init__(parent)
        self.page_id = id(self)
        self.size = size
        pub.subscribe(self.save, 'save_{}'.format(self.page_id))
        pub.subscribe(self.add_node,
                      'add_node_{}'.format(self.page_id))

        self.xml_path = None
        self.open_xml()

    def create_editor(self):
        """
        Create the XML editor widgets
        """
        page_sizer = wx.BoxSizer(wx.VERTICAL)

        splitter = wx.SplitterWindow(self)
        self.tree_panel = TreePanel(splitter, self.page_id, self.xml)

        xml_editor_notebook = wx.Notebook(splitter)
        xml_editor_panel = XmlEditorPanel(xml_editor_notebook,
                                          self.page_id)
        xml_editor_notebook.AddPage(xml_editor_panel, 'Nodes')

        attribute_panel = AttributeEditorPanel(
            xml_editor_notebook, self.page_id)
        xml_editor_notebook.AddPage(attribute_panel, 'Attributes')

        splitter.SplitVertically(self.tree_panel, xml_editor_notebook)
        splitter.SetMinimumPaneSize(int(self.size[0] / 2))
        page_sizer.Add(splitter, 1, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(page_sizer)
        self.Layout()

    def open_xml(self, path='sample.xml'):
        try:
            with open(path) as f:
                self.xml = f.read()
        except IOError:
            print('Bad file')
            return
        except Exception as e:
            print('Really bad error')
            print(e)
            return
        self.create_editor()

    def save(self):
        print('Saving')

    def add_node(self):
        """
        Add a sub-node to the selected item in the tree

        Called by pubsub
        """
        print('Add node')


class MainFrame(wx.Frame):

    def __init__(self):
        size = (800, 600)
        super().__init__(
            None, title="XML Editor",
            size=size)
        self.panel = EditorPanel(self, size)
        self.create_menu()
        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        help_menu = wx.Menu()

        # add menu items to the file menu
        open_menu_item = file_menu.Append(
                wx.NewIdRef(), 'Open', '')
        self.Bind(wx.EVT_MENU, self.on_open, open_menu_item)

        save_menu_item = file_menu.Append(
                wx.NewIdRef(), 'Save', '')
        self.Bind(wx.EVT_MENU, self.on_save, save_menu_item)

        exit_menu_item = file_menu.Append(
                wx.NewIdRef(), 'Quit', '')
        self.Bind(wx.EVT_MENU, self.on_exit, exit_menu_item)
        menu_bar.Append(file_menu, "&File")

        # add menu items to the help menu
        about_menu_item = help_menu.Append(
                wx.NewIdRef(), 'About')
        self.Bind(wx.EVT_MENU, self.on_about_box, about_menu_item)
        menu_bar.Append(help_menu, '&Help')

        self.SetMenuBar(menu_bar)

    def on_save(self, event):
        """
        Event handler that saves the data to disk
        """
        pub.sendMessage('save_{}'.format(self.panel.page_id))

    def on_about_box(self, event):
        """
        Event handler that builds and shows an about box
        """
        info = wx.adv.AboutDialogInfo()
        info.Name = "About XML Editor"
        info.Version = "0.1 Beta"
        info.Copyright = "(C) 2019 Mike Driscoll"
        info.Description = wordwrap(
            "This is a Python-based XML editor ",
            350, wx.ClientDC(self.panel))
        info.WebSite = ("https://mousevspython.com",
                        "Mouse Vs Python")
        info.Developers = ["Mike Driscoll"]
        info.License = wordwrap("wxWindows Library Licence", 500,
                                wx.ClientDC(self.panel))
        # Show the wx.AboutBox
        wx.adv.AboutBox(info)

    def on_open(self, event):
        """
        Event handler that is called when you need to open an XML file
        """
        path = None
        default_dir=os.path.expanduser('~')
        with wx.FileDialog(
            self, message="Choose a file",
            defaultDir=default_dir,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
            ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()

        if path:
            self.panel.open_xml(path)

    def on_exit(self, event):
        """
        Event handler that closes the application
        """
        self.Destroy()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()