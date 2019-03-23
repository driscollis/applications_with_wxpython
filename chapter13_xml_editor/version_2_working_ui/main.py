import os
import sys
import time
import utils
import wx
import wx.adv
import wx.lib.agw.flatnotebook as fnb

from editor_page import NewPage
from pubsub import pub
from wx.lib.wordwrap import wordwrap


class MainFrame(wx.Frame):

    def __init__(self):
        self.size = (800, 600)
        wx.Frame.__init__(self, parent=None, title='XML Editor',
                          size=(800, 600))

        self.full_tmp_path = ''
        self.full_saved_path = ''
        self.changed = False
        self.notebook = None
        self.opened_files = []
        self.last_opened_file = None
        self.current_page = None

        self.current_directory = os.path.expanduser('~')
        self.app_location = os.path.dirname(os.path.abspath( sys.argv[0] ))
        self.recent_files_path = os.path.join(
            self.app_location, 'recent_files.txt')

        pub.subscribe(self.save, 'save')

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self)
        self.panel.SetSizer(self.main_sizer)

        self.create_menu_and_toolbar()

        self.Bind(wx.EVT_CLOSE, self.on_exit)

        self.Show()

    def create_new_editor(self, xml_path):
        """
        Create the tree and xml editing widgets when the user loads
        an XML file
        """
        if not self.notebook:
            self.notebook = fnb.FlatNotebook(
                self.panel)
            self.main_sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
            style = self.notebook.GetAGWWindowStyleFlag()
            style |= fnb.FNB_X_ON_TAB
            self.notebook.SetAGWWindowStyleFlag(style)
            self.notebook.Bind(
                fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.on_page_closing)

        if xml_path not in self.opened_files:
            self.current_page = NewPage(self.notebook, xml_path, self.size,
                                        self.opened_files)
            self.notebook.AddPage(self.current_page,
                                  os.path.basename(xml_path),
                                  select=True)
            self.last_opened_file = xml_path

            self.opened_files.append(self.last_opened_file)

        self.panel.Layout()

    def create_menu_and_toolbar(self):
        """
        Creates the menu bar, menu items, toolbar and accelerator table
        for the main frame
        """
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        help_menu = wx.Menu()

        # add menu items to the file menu
        open_menu_item = file_menu.Append(
            wx.NewId(), 'Open', '')
        self.Bind(wx.EVT_MENU, self.on_open, open_menu_item)

        save_menu_item = file_menu.Append(
            wx.NewId(), 'Save', '')
        self.Bind(wx.EVT_MENU, self.on_save, save_menu_item)

        exit_menu_item = file_menu.Append(
            wx.NewId(), 'Quit', '')
        self.Bind(wx.EVT_MENU, self.on_exit, exit_menu_item)
        menu_bar.Append(file_menu, "&File")

        self.SetMenuBar(menu_bar)

    def open_xml_file(self, xml_path):
        """
        Open the specified XML file and load it in the application
        """
        self.create_new_editor(xml_path)

    def save(self):
        """
        Update the frame with save status
        """
        if self.current_page is None:
            utils.warn_nothing_to_save()
            return

        pub.sendMessage('save_{}'.format(self.current_page.page_id))

        self.changed = False

    def on_open(self, event):
        """
        Event handler that is called when you need to open an XML file
        """
        xml_path = utils.open_file()

        if xml_path:
            self.last_opened_file = xml_path
            self.open_xml_file(xml_path)

    def on_page_closing(self, event):
        """
        Event handler that is called when a page in the notebook is closing
        """
        page = self.notebook.GetCurrentPage()
        page.Close()
        if not self.opened_files:
            wx.CallAfter(self.notebook.Destroy)
            self.notebook = None

    def on_save(self, event):
        """
        Event handler that saves the data to disk
        """
        self.save()

    def on_exit(self, event):
        """
        Event handler that closes the application
        """
        self.Destroy()

# ------------------------------------------------------------------------------
# Run the program!
if __name__ == '__main__':
    xml_path = 'books.xml'
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.MainLoop()
