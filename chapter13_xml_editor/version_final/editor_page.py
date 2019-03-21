import lxml.etree as ET
import os
import sys
import time
import utils
import wx

from boom_attribute_ed import AttributeEditorPanel
from boom_tree import BoomTreePanel
from boom_xml_editor import XmlEditorPanel
from pubsub import pub

class NewPage(wx.Panel):
    """
    Create a new page for each opened XML document. This is the
    top-level widget for the majority of the application
    """

    def __init__(self, parent, xml_path, size, opened_files):
        wx.Panel.__init__(self, parent)
        self.page_id = id(self)
        self.xml_root = None
        self.size = size
        self.opened_files = opened_files
        self.current_file = xml_path
        self.title = os.path.basename(xml_path)

        self.app_location = os.path.dirname(os.path.abspath( sys.argv[0] ))

        self.tmp_location = os.path.join(self.app_location, 'drafts')

        pub.subscribe(self.save, 'save_{}'.format(self.page_id))
        pub.subscribe(self.auto_save, 'on_change_{}'.format(self.page_id))

        self.parse_xml(xml_path)

        current_time = time.strftime('%Y-%m-%d.%H.%M.%S', time.localtime())
        self.full_tmp_path = os.path.join(
            self.tmp_location,
            current_time + '-' + os.path.basename(xml_path))

        if not os.path.exists(self.tmp_location):
            try:
                os.makedirs(self.tmp_location)
            except IOError:
                raise IOError('Unable to create file at {}'.format(
                    self.tmp_location))

        if self.xml_root is not None:
            self.create_editor()

    def create_editor(self):
        """
        Create the XML editor widgets
        """
        page_sizer = wx.BoxSizer(wx.VERTICAL)

        splitter = wx.SplitterWindow(self)
        tree_panel = BoomTreePanel(splitter, self.xml_root, self.page_id)

        xml_editor_notebook = wx.Notebook(splitter)
        xml_editor_panel = XmlEditorPanel(xml_editor_notebook, self.page_id)
        xml_editor_notebook.AddPage(xml_editor_panel, 'Nodes')

        attribute_panel = AttributeEditorPanel(
            xml_editor_notebook, self.page_id)
        xml_editor_notebook.AddPage(attribute_panel, 'Attributes')

        splitter.SplitVertically(tree_panel, xml_editor_notebook)
        splitter.SetMinimumPaneSize(self.size[0] / 2)
        page_sizer.Add(splitter, 1, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(page_sizer)
        self.Layout()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def auto_save(self, event):
        """
        Event handler that is called via pubsub to save the
        current version of the XML to disk in a temporary location
        """
        self.xml_tree.write(self.full_tmp_path)
        pub.sendMessage('on_change_status', save_path=self.full_tmp_path)

    def parse_xml(self, xml_path):
        """
        Parses the XML from the file that is passed in
        """
        self.current_directory = os.path.dirname(xml_path)
        try:
            self.xml_tree = ET.parse(xml_path)
        except IOError:
            print('Bad file')
            return
        except Exception as e:
            print('Really bad error')
            print(e)
            return

        self.xml_root = self.xml_tree.getroot()

    def save(self, location=None):
        """
        Save the XML to disk
        """
        if not location:
            path = utils.save_file(self)
        else:
            path = location

        if path:
            if '.xml' not in path:
                path += '.xml'

            # Save the xml
            self.xml_tree.write(path)
            self.changed = False

    def on_close(self, event):
        """
        Event handler that is called when the panel is being closed
        """
        if self.current_file in self.opened_files:
            self.opened_files.remove(self.current_file)

        if os.path.exists(self.full_tmp_path):
            try:
                os.remove(self.full_tmp_path)
            except IOError:
                print('Unable to delete file: {}'.format(self.full_tmp_path))
