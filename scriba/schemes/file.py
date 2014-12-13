"""Handle file URL"""

import mimetypes
import os

try:
    url2pathname = __import__('urllib.request').url2pathname
except ImportError:
    url2pathname = __import__('urllib').url2pathname

import multipla

content_encodings = multipla.power_up('scriba.content_encodings')
content_types = multipla.power_up('scriba.content_types')


class FileResource(object):
    def __init__(self, url, **params):
        self.url = url
        self.params = params

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read(self):
        with open(url2pathname(self.url.path), 'rb') as file_:
            return self._read(file_.read())

    def _read(self, content):
        params = self.params.copy()
        content_type, encoding = mimetypes.guess_type(self.url.path)
        content_type = params.pop('content_type', content_type)
        encoding = params.pop('content_encoding', encoding)
        content = content_encodings.get(encoding).decode(content)
        return content_types.get(content_type).parse(content, **params)

    def write(self, content):
        path = url2pathname(self.url.path)
        with open(path, 'wb') as file_:
            file_.write(self._write(path, content))

    def _write(self, content):
        params = self.params.copy()
        content_type, encoding = mimetypes.guess_type(self.url.path)
        content_type = params.pop('content_type', content_type)
        encoding = params.pop('content_encoding', encoding)
        content = content_types.get(content_type).parse(content, **params)
        content = content_encodings.get(encoding).decode(content)
        return content

    def erase(self):
        os.remove(url2pathname(self.url.path))


def read(url, **args):
    """Get the file/direcotry from a file URL."""
    with FileResource(url, **args) as resource:
        return resource.read()


def write(url, content, **args):
    """Put the object/collection into a file URL."""
    with FileResource(url, **args) as resource:
        resource.write(content)


def erase(url, **args):
    """Remove the sample from a file URL."""
    FileResource(url, **args).erase()
