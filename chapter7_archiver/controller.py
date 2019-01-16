import os
import tarfile
import zipfile

from functools import partial
from pathlib import Path

def create_archive(path, archive_objects, archive_type):
    if archive_type == 'Tar':
        create_tar(path, archive_objects)
    elif archive_type == 'Zip':
        create_zip(path, archive_objects)
        
        
def create_tar(path, archive_objects):
    with tarfile.open(path, 'w') as tar:
        for archive_object in archive_objects:
            tar.add(archive_object.path, 
                    arcname=archive_object.path.name)
        

def create_zip(path, archive_objects):
    with zipfile.ZipFile(path, 'w') as archive:
        for archive_object in archive_objects:
            if archive_object.path.is_file():
                archive.write(
                    archive_object.path.absolute(), 
                    arcname=archive_object.path.name)
            elif archive_object.path.is_dir():
                zip_folder(archive, archive_object.path)
                
def zip_folder(archive, path):
    for root, dirs, files in os.walk(path):
        dirname = Path(root)
        archive.write(
            dirname.absolute(),
            arcname=dirname.name)
        for f in files:
            file_path = dirname / f
            arcname = Path(dirname.name) / Path(file_path.name)
            archive.write(
                file_path.absolute(),
                arcname=arcname)
