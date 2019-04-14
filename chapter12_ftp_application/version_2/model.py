class Path:

    def __init__(self, ftype, size, filename, date):
        if 'd' in ftype:
            self.folder = True
        else:
            self.folder = False
        self.size = size
        self.filename = filename
        self.last_modified = f'{date}'