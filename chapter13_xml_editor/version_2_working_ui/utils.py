import hashlib
import os
import wx

from io import StringIO


wildcard = "XML (*.xml)|*.xml|" \
    "All files (*.*)|*.*"


def open_file(self, default_dir=os.path.expanduser('~')):
    """
    A utility function for opening a file dialog to allow the user
    to open an XML file of their choice
    """
    path = None
    dlg = wx.FileDialog(
        self, message="Choose a file",
        defaultDir=default_dir,
        defaultFile="",
        wildcard=wildcard,
        style=wx.FD_OPEN | wx.FD_CHANGE_DIR
    )
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()

    dlg.Destroy()

    if path:
        return path


def save_file(self):
    """
    A utility function that allows the user to save their XML file
    to a specific location using a file dialog
    """
    path = None
    dlg = wx.FileDialog(
        self, message="Save file as ...",
        defaultDir=self.current_directory,
        defaultFile="", wildcard=wildcard,
        style=wx.FD_SAVE
    )
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    dlg.Destroy()

    if path:
        return path


def warn_nothing_to_save():
    """
    Warns the user that there is nothing to save
    """
    msg = "No Files Open! Nothing to save."
    dlg = wx.MessageDialog(
        parent=None,
        message=msg,
        caption='Warning',
        style=wx.OK|wx.ICON_EXCLAMATION
    )
    dlg.ShowModal()
    dlg.Destroy()