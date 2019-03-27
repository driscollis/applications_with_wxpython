# controller.py

import tarfile


def create_archive(path, archive_objects, archive_type):
    if archive_type == 'Tar':
        create_tar(path, archive_objects)


def create_tar(path, archive_objects):
    with tarfile.open(path, 'w') as tar:
        for archive_object in archive_objects:
            tar.add(archive_object.path,
                    arcname=archive_object.path.name)