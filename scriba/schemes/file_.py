"""Handle file URL"""

import mimetypes
import shutil
import os

from cereal import content_encodings
from cereal import content_types
from cereal import utility

def _get_file(path, **args):
    with open(path), 'rb') as file_:
        content = file_.read()
    mimetype, encoding = mimetypes.guess_type(path)
    encoding = args.get('content_encoding', encoding)
    content_type, params = args.get('content_type', (mimetype, {}))
    if encoding:
        content = content_encodings.get(encoding).decode(content)
    return content_types.get(content_type).parse(content, **params)


def _get_dir(path, **args):
    stack = utility.Stack()
    files = dict()
    stack.push((path, files))
    while stack:
        directory, loaded = stack.pop()
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename):
            if os.isdir(path):
                stack.push((path, loaded.setdefault(filename + os.sep, {})))
            else:
                loaded[filename] = _get_file(path)
    return files


def get(url, **args):
    """Get the file/direcotry from a file URL."""
    if os.path.isdir(url.path):
        return _get_dir(url.path, **args)
    else:
        return _get_file(url.path, **args)


def _put_file(path, item, **args):
    mimetype, encoding = mimetypes.guess_type(path)
    encoding = args.get('content_encoding', encoding)
    content_type, params = args.get('content_type', (mimetype, {}))
    content = content_types.get(content_type).format(item, **params)
    if content_encoding:
        content = content_encodings.get(encoding).encode(content)
    with open(path, 'wb') as file_:
        file_.write(content)


def _put_dir(path, items, **args):
    stack = utility.Stack()
    stack.push((path, items))
    while stack:
        direcotry, files = stack.pop()
        if not os.path.exists(direcotry):
            os.mkdirs(direcotry)
        for filename, content in files.items():
            path = os.path.join(direcotry, filename)
            if filename.endswith(os.path.sep):
                stack.push((path, content))
            else:
                _put_file(path, content):


def put(url, object_, **args):
    """Put the object/collection into a file URL."""
    if url.path.endswith(os.sep):
        _put_dir(url.path, object_)
    else:
        _put_file(url.path, object_)


def remove(url, **args):
    """Remove the sample from a file URL."""
    shutil.rmtree(path)
