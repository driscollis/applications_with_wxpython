# controller.py

import tarfile

def create_tar(path, archive_objects):
    with tarfile.open(path, 'w') as tar:
        for archive_object in archive_objects:
            tar.add(archive_object,
                    arcname=archive_object.name)