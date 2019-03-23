import os
import wx

wildcard = "XML (*.xml)|*.xml|" \
    "All files (*.*)|*.*"


def open_file(default_dir=os.path.expanduser('~')):
    """
    A utility function for opening a file dialog to allow the user
    to open an XML file of their choice
    """
    path = None
    with wx.FileDialog(
        None, message="Choose a file",
        defaultDir=default_dir,
        defaultFile="",
        wildcard=wildcard,
        style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        ) as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

    if path:
        return path


def save_file(default_dir):
    """
    A utility function that allows the user to save their XML file
    to a specific location using a file dialog
    """
    path = None
    with wx.FileDialog(
        None, message="Save file as ...",
        defaultDir=default_dir,
        defaultFile="", wildcard=wildcard,
        style=wx.FD_SAVE
        ) as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

    if path:
        return path


def warn_nothing_to_save():
    """
    Warns the user that there is nothing to save
    """
    msg = "No Files Open! Nothing to save."
    with wx.MessageDialog(
        parent=None,
        message=msg,
        caption='Warning',
        style=wx.OK|wx.ICON_EXCLAMATION
        ) as dlg:
        dlg.ShowModal()
