import lxml.etree as ET
import wx

from add_node_dialog import NodeDialog
from pubsub import pub


class XmlTree(wx.TreeCtrl):
    """
    The class that holds all the functionality for the tree control
    widget
    """

    def __init__(self, parent, wx_id, pos, size, style):
        wx.TreeCtrl.__init__(self, parent, wx_id, pos, size, style)
        self.expanded= {}
        self.xml_root = parent.xml_root
        self.page_id = parent.page_id
        pub.subscribe(self.update_tree,
                      'tree_update_{}'.format(self.page_id))

        root = self.AddRoot(self.xml_root.tag)
        self.expanded[id(self.xml_root)] = ''
        self.SetItemData(root, self.xml_root)
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
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.on_item_expanding)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection)

    def add_elements(self, item, book):
        """
        Add items to the tree control
        """
        for element in book.getchildren():
            child = self.AppendItem(item, element.tag)
            self.SetItemData(child, element)
            if element.getchildren():
                self.SetItemHasChildren(child)

    def on_item_expanding(self, event):
        """
        A handler that fires when a tree item is being expanded

        This will cause the sub-elements of the tree to be created
        and added to the tree
        """
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
        pub.sendMessage('ui_updater_{}'.format(self.page_id),
                        xml_obj=xml_obj)

    def update_tree(self, xml_obj):
        """
        Update the tree with the new data
        """
        selection = self.GetSelection()
        selected_tree_xml_obj = self.GetItemData(selection)

        if id(selected_tree_xml_obj) in self.expanded:
            child = self.AppendItem(selection, xml_obj.tag)
            if xml_obj.getchildren():
                self.SetItemHasChildren(child)
            self.SetItemData(child, xml_obj)

        if selected_tree_xml_obj.getchildren():
            self.SetItemHasChildren(selection)


class BoomTreePanel(wx.Panel):
    """
    The panel class that contains the XML tree control
    """

    def __init__(self, parent, xml_obj, page_id):
        wx.Panel.__init__(self, parent)
        self.xml_root = xml_obj
        self.copied_data = None
        self.page_id = page_id

        pub.subscribe(self.add_node,
                      'add_node_{}'.format(self.page_id))
        pub.subscribe(self.remove_node,
                      'remove_node_{}'.format(self.page_id))

        self.tree = XmlTree(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            wx.TR_HAS_BUTTONS)
        self.tree.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def on_context_menu(self, event):
        """
        Event handler that creates a context menu on right-click
        of a tree control's item
        """
        if not hasattr(self, "add_node_id"):
            self.add_node_id = wx.NewId()
            self.remove_node_id = wx.NewId()
            self.copy_id = wx.NewId()
            self.paste_id = wx.NewId()

            self.Bind(wx.EVT_MENU, self.on_add_remove_node,
                      id=self.add_node_id)
            self.Bind(wx.EVT_MENU, self.on_add_remove_node,
                      id=self.remove_node_id)
            self.Bind(wx.EVT_MENU, self.on_copy, id=self.copy_id)
            self.Bind(wx.EVT_MENU, self.on_paste, id=self.paste_id)

        # Build the context menu
        menu = wx.Menu()
        copy_menu_item = menu.Append(self.copy_id, 'Copy')
        paste_menu_item = menu.Append(self.paste_id, 'Paste')
        menu.AppendSeparator()
        add_node_menu_item = menu.Append(self.add_node_id, 'Add Node')
        remove_node_menu_item = menu.Append(self.remove_node_id, 'Remove Node')

        self.PopupMenu(menu)
        menu.Destroy()

    def on_add_remove_node(self, event):
        """
        Event handler for adding or removing nodes
        """
        evt_id = event.GetId()
        if evt_id == self.add_node_id:
            self.add_node()
        elif evt_id == self.remove_node_id:
            self.remove_node()

    def on_copy(self, event):
        """
        Copy the selected XML object into memory
        """
        node = self.tree.GetSelection()
        self.copied_data = self.tree.GetItemData(node)

    def on_paste(self, event):
        """
        Paste / Append the copied XML data to the selected node
        """
        if self.copied_data:
            node = self.tree.GetSelection()
            parent_xml_node = self.tree.GetItemData(node)

            parent_xml_node.append(self.copied_data)
            pub.sendMessage('tree_update_{}'.format(self.page_id),
                            xml_obj=self.copied_data)
            pub.sendMessage('on_change_{}'.format(self.page_id),
                            event=None)

    def add_node(self):
        """
        Add a sub-node to the selected item in the tree
        """
        node = self.tree.GetSelection()
        data = self.tree.GetItemData(node)
        dlg = NodeDialog(data,
                         page_id=self.page_id,
                         title = 'New Node',
                         label_one = 'Element Tag',
                         label_two = 'Element Value'
                         )
        dlg.Destroy()

    def remove_node(self):
        """
        Remove the selected node from the tree
        """
        node = self.tree.GetSelection()
        xml_node = self.tree.GetItemData(node)

        if node:
            msg = 'Are you sure you want to delete the {node} node'
            dlg = wx.MessageDialog(
                parent=None,
                message=msg.format(node=xml_node.tag),
                caption='Warning',
                style=wx.YES_NO|wx.YES_DEFAULT|wx.ICON_EXCLAMATION
            )
            if dlg.ShowModal() == wx.ID_YES:
                parent = xml_node.getparent()
                parent.remove(xml_node)
                self.tree.DeleteChildren(node)
                self.tree.Delete(node)
                pub.sendMessage('on_change_{}'.format(self.page_id),
                                event=None)
            dlg.Destroy()
