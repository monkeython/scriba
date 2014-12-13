"""Handle ftp URL"""

import ftplib
import io
import netrc
import socket

import multipla

import scriba.schemes.file as file_scheme

content_encodings = multipla.power_up('scriba.content_encodings')
content_types = multipla.power_up('scriba.content_types')

_netrc = dict()
try:
    _locked_netrc = __import__('thread').allocate_lock()
except ImportError:     # pragma: no cover
    try:
        _locked_netrc = __import__('_thread').allocate_lock()
    except ImportError:
        try:
            _locked_netrc = __import__('dummy_thread').allocate_lock()
        except ImportError:
            _locked_netrc = __import__('_dummy_thread').allocate_lock()


def authenticators(netrc_path, host):
    global _netrc, _locked_netrc
    netrc_path = None if netrc_path is True else netrc_path
    with _locked_netrc:
        try:
            netrc_file = _netrc[netrc_path]
        except KeyError:
            _netrc[netrc_path] = netrc_file = netrc.netrc(netrc_path)
    auth = netrc_file.authenticators(host)
    return ('', '', '') if auth is None else auth


class FTPResource(file_scheme.FileResource):

    def __init__(self, url, **params):
        self.url = url
        self.params = params
        self.client = ftplib.FTP()

    def _connect(self, port):
        timeout = self.params.pop('timeout', socket._GLOBAL_DEFAULT_TIMEOUT)
        self.client.connect(self.url.hostname, port, timeout)
        try:
            netrc_file = self.params.pop('netrc')
        except KeyError:
            self.client.login(self.url.username, self.url.password, '')
        else:
            self.client.login(*authenticators(netrc_file, self.url.host))

    def __enter__(self):
        self._connect(self.url.port or ftplib.FTP_PORT)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.quit()

    def read(self):
        content = io.BytesIO()
        self.client.retrbinary('RETR {}'.format(self.url.path), content.write)
        content.seek(0)
        return self._read(content.read())

    def write(self, content):
        content = io.BytesIO(self._write(content))
        self.client.storbinary('STOR {}'.format(self.url.path), content)

    def erase(self):
        self.client.delete(self.url.path)


def read(url, **args):
    """Get the object from a ftp URL."""
    with FTPResource(url, **args) as resource:
        return resource.read()


def write(url, content, **args):
    """Put an object into a ftp URL."""
    with FTPResource(url, **args) as resource:
        resource.write(content)


def erase(url, **args):
    """Remove the sample from a file URL."""
    with FTPResource(url, **args) as resource:
        resource.erase()
