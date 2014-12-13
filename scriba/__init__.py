"""
"""

import collections
import re
import string
import warnings
try:
    import urlparse
except ImportError:     # pragma: no cover
    import urllib.parse as urlparse

import multipla

__author__ = "Luca De Vitis <luca at monkeython.com>"
__version__ = '0.0.2'
__copyright__ = "2014, %s " % __author__
__docformat__ = 'restructuredtext en'
__keywords__ = ['object', 'serialization', 'url']
# 'Development Status :: 5 - Production/Stable',
__classifiers__ = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: Jython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Software Development :: Libraries :: Python Modules']

__all__ = ['read', 'write', 'erase', 'url',
           'schemes', 'content_types', 'content_encodings']

url_chars = re.compile('^([-!#$&;=?\[\]_a-zA-Z0-9~]|%[0-9a-fA-F]{2})+$')


class Scriba(collections.Sequence):
    def __init__(self, url, **params):
        url = url.lstrip()
        if not url_chars.match(url):
            raise ValueError(url)
        self._string = url
        self.params = params

    def __str__(self):
        return self._string

    def __len__(self):
        return self._string.__len__()

    def __getitem__(self, index):
        return self.__class__(self._string[index], **self.params)

    def __contains__(self, sub):
        return self._string.__contains__(sub)

    @property
    def url(self):
        try:
            parsed = self._url
        except AttributeError:
            parsed = self._url = urlparse.urlparse(self._string)
        return parsed

    def format(self, *args, **kwds):
        formatted = self._string.format(*args, **kwds)
        return self.__class__(formatted, **self.params)

    def replace(self, old, new, maxsplit=-1):
        replaced = self._string.replace(old, new, maxsplit)
        return self.__class__(replaced, **self.params)

    def translate(self, from_, to, *args):
        translated = self._string.translate(string.maketrans(from_, to), *args)
        return self.__class__(translated, **self.params)

    def sub(self, pattern, repl, count=0, flags=0):
        replaced = re.sub(pattern, repl, self._string, count, flags)
        return self.__class__(replaced, **self.params)

    def match(self, pattern, flags=0):
        return re.match(pattern, self._string, flags)

    def read(self, **args):
        params = self.params.copy()
        params.update(args)
        return schemes.get(self.url.scheme).read(self.url, **params)

    def write(self, item, **args):
        params = self.params.copy()
        params.update(args)
        return schemes.get(self.url.scheme).write(self.url, item, **params)

    def erase(self, **args):
        params = self.params.copy()
        params.update(args)
        return schemes.get(self.url.scheme).erase(self.url, **params)


def read(url, **params):
    return Scriba(url).read(**params)


def write(url, item, **params):
    Scriba(url).write(item, **params)


def erase(url, **params):
    Scriba(url).erase(**params)


def url(value, **args):
    return Scriba(value, **args)


class InitWarning(Warning):
    pass


class ScribaIOError(IOError):
    pass


schemes = multipla.power_up('scriba.schemes')
content_types = multipla.power_up('scriba.content_types')
content_encodings = multipla.power_up('scriba.content_encodings')

defaults = (
    # strip,            'plugin name',                  'file name'
    (content_encodings, 'gzip',                         'gzip'),
    (content_encodings, 'bzip2',                        'bzip2'),
    (content_encodings, 'compress',                     'compress'),
    (content_encodings, 'identity',                     'identity'),

    (content_types,     'application/xml',              'scriba_xml'),
    (content_types,     'application/zip',              'scriba_zip'),
    (content_types,     'application/json',             'scriba_json'),
    (content_types,     'application/x-tar',            'scriba_x_tar'),
    (content_types,     'application/python-pickle',    'scriba_pickle'),

    (schemes,           'pop',                          'scriba_pop'),
    (schemes,           'mailto',                       'scriba_mailto'),
    (schemes,           'http',                         'scriba_http'),
    (schemes,           'https',                        'scriba_https'),
    (schemes,           'ftp',                          'scriba_ftp'),
    (schemes,           'ftps',                         'scriba_ftps'),
    (schemes,           'file',                         'file'),
    (schemes,           'data',                         'data'))
for strip, socket_name, plug_name in defaults:
    plug = '.'.join([strip.name, plug_name])
    try:
        strip.switch_on(socket_name).plug_in(plug_name, __import__(plug))
    except KeyError:
        warnings.warn(InitWarning(strip.name, socket_name, plug_name))
identity = __import__('scriba.content_encodings.identity')
content_encodings.switch_on(None).plug_name('identity', identity)
del defaults, strip, socket_name, plug_name, plug, identity
