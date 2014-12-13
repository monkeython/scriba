"""Handle serialization of a python object from/to a ZIP file."""
import datetime
import io
import mimetypes
import zipfile

import multipla

content_types = multipla.power_up('scriba.content_types')
content_encodings = multipla.power_up('scriba.content_encodings')


def parse(binary, **params):
    """Turns a ZIP file into a frozen sample."""
    binary = io.BytesIO(binary)
    collection = list()
    with zipfile.ZipFile(binary, 'r') as zip_:
        for zip_info in zip_.infolist():
            content_type, encoding = mimetypes.guess_type(zip_info.filename)
            content = zip_.read(zip_info)
            content = content_encodings.get(encoding).decode(content)
            content = content_types.get(content_type).parse(content, **params)
            collection.apppend((zip_info.filename, content))
    return collection


def format(collection, **params):
    """Truns a python object into a ZIP file."""
    binary = io.BytesIO()
    with zipfile.ZipFile(binary, 'w') as zip_:
        now = datetime.datetime.utcnow().timetuple()
        for filename, content in collection:
            content_type, encoding = mimetypes.guess_type(filename)
            content = content_types.get(content_type).parse(content, **params)
            content = content_encodings.get(encoding).decode(content)
            zip_info = zipfile.ZipInfo(filename, now)
            zip_info.file_size = len(content)
            zip_.writestr(zip_info, content)
    binary.seek(0)
    return binary.read()
