import pathlib
import time
import wx

from ObjectListView import ObjectListView, ColumnDefn

class Items:
    
    def __init__(self, path, name, size, item_type, 
                 modified):
        self.path = path
        self.name = name
        self.size = size
        self.item_type = item_type
        self.modified = modified


class DropTarget(wx.FileDropTarget):
    
    def __init__(self, window):
        super().__init__()
        self.window = window
        
    def OnDropFiles(self, x, y, filenames):
        self.window.update_display(filenames)
        return True

class ArchivePanel(wx.Panel):
    
    
    def __init__(self, parent):
        super().__init__(parent)
        drop_target = DropTarget(self)
        self.archive_items = []
        
        self.archive_olv = ObjectListView(
            self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.archive_olv.SetEmptyListMsg("Add Files / Folders here")
        self.archive_olv.SetDropTarget(drop_target)
        self.update_archive()
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.archive_olv, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)
        
    def update_archive(self):
        self.archive_olv.SetColumns([
                            ColumnDefn("Name", "left", 350, "name"),
                            ColumnDefn("Size", "left", 75, "size"),
                            ColumnDefn("Type", "right", 75, "item_type"),
                            ColumnDefn("Modified", "left", 150, "modified")
                        ])
        self.archive_olv.SetObjects(self.archive_items)
        
    def update_display(self, items):
        paths = [pathlib.Path(item) for item in items]
        for path in paths:
            basename = path.name
            size = self.get_size(path)
            if path.is_dir():
                item_type = 'folder'
            else:
                item_type = 'file'
            last_modified = time.ctime(path.stat().st_mtime)
            item = Items(path, basename, size, item_type, 
                         last_modified)
            self.archive_items.append(item)
        
        self.update_archive()
            
    def get_size(self, path):
        size = path.stat().st_size
        
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
        index = 0
        while size > 1024:
            index += 1
            size = size / 1024.0
        
        suffix = suffixes[index]
        return f'{size:.1f} {suffix}'
        

class MainFrame(wx.Frame):
    
    def __init__(self):
        """Constructor"""
        super().__init__(
            None, title="PyArchiver",
            size=(800, 600))
        panel = ArchivePanel(self)
        
        self.Show()
        
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
