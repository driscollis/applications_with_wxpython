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

def get_md5(path):
    """
    Returns the MD5 hash of the given file
    """
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            data = f.read(4096)
            hash_md5.update(data)
            if not data:
                break
    return hash_md5.hexdigest()

def is_save_current(saved_file_path, tmp_file_path):
    """
    Returns a bool that determines if the saved file and the
    tmp file's MD5 hash are the same
    """
    saved_md5 = get_md5(saved_file_path)
    tmp_md5 = get_md5(tmp_file_path)

    return saved_md5 == tmp_md5


def warn_not_saved():
    """
    Shows a dialog to warn the user that they need to save their changes
    """
    msg = 'Do you want to save your changes?'
    dlg = wx.MessageDialog(
        parent=None,
        message=msg,
        caption='Warning',
        style=wx.YES_NO|wx.YES_DEFAULT|wx.ICON_EXCLAMATION
    )
    if dlg.ShowModal() == wx.ID_YES:
        self.save(location=self.full_saved_path)

    dlg.Destroy()


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