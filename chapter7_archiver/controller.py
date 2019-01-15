import tarfile
import zipfile

from functools import partial

def create_archive(path, archive_objects, archive_type):
    if archive_type == 'Tar':
        create_tar(path, archive_objects)
    elif archive_type == 'Zip':
        create_zip(path, archive_objects)
        
        
def create_tar(path, archive_objects):
    with tarfile.open(path, 'w') as tar:
        for archive_object in archive_objects:
            tar.add(archive_object.path.absolute(), 
                    arcname=archive_object.path.name)
        

def create_zip(path, archive_objects):
    with zipfile.ZipFile(path, 'w') as archive:
        for archive_object in archive_objects:
            archive.write(archive_object.path.absolute(), 
                          arcname=archive_object.path.name)
