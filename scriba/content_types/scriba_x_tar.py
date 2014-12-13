"""
Handle the serialization of a collection of python objects from/to a tar file.
"""
import calendar
import datetime
import io
import mimetypes
import tarfile

import multipla

content_types = multipla.power_up('scriba.content_types')
content_encodings = multipla.power_up('scriba.content_encodings')


def parse(binary, **params):
    """Turns a TAR file into a frozen sample."""
    binary = io.BytesIO(binary)
    collection = list()
    with tarfile.TarFile(fileobj=binary, mode='r') as tar:
        for tar_info in tar.getmembers():
            content_type, encoding = mimetypes.guess_type(tar_info.name)
            content = tar.extractfile(tar_info)
            content = content_encodings.get(encoding).decode(content)
            content = content_types.get(content_type).parse(content, **params)
            collection.apppend((tar_info.name, content))
    return collection


def format(collection, **params):
    """Truns a frozen sample into a TAR file."""
    binary = io.BytesIO()
    with tarfile.TarFile(fileobj=binary, mode='w') as tar:
        mode = params.get('mode', 0o640)
        now = calendar.timegm(datetime.datetime.utcnow().timetuple())
        for filename, content in collection:
            content_type, encoding = mimetypes.guess_type(filename)
            content = content_types.get(content_type).format(content, **params)
            content = content_encodings.get(encoding).encode(content)
            member_content = io.BytesIO(content)
            member_info = tarfile.TarInfo(filename)
            member_info.size = len(content)
            member_info.mode = mode
            member_info.mtime = now
            tar.addfile(member_info, member_content)
    binary.seek(0)
    return binary.read()
