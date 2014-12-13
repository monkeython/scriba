"""Handle http URL"""

import httplib
import mimetypes
import socket

import multipla

content_encodings = multipla.power_up('scriba.content_encodings')
content_types = multipla.power_up('scriba.content_types')


class HTTPBadResponse(httplib.HTTPException):
    pass


class HTTPResource(object):
    def __init__(self, url, **params):
        self.url = url
        self.params = params

    def __enter__(self):
        strict = self.params.get('strict', True)
        timeout = self.params.get('timeout', socket._GLOBAL_DEFAULT_TIMEOUT)
        self.client = httplib.HTTPConnection(self.url.hostname,
                                             self.url.port or None,
                                             strict, timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def _argument(self):
        argument = self.url.path
        if self.url.params:
            argument += ';{}'.format(self.url.params)
        if self.url.query:
            argument += '?{}'.format(self.url.query)
        if self.url.fragment:
            argument += '#{}'.format(self.url.fragment)
        return argument

    def read(self):
        self.client.request('GET', self._argument())
        response = self.client.getresponse()
        if response.status == 200:
            return self._read(response)
        raise HTTPBadResponse(response)

    def _read(self, response):
        params = self.params.copy()
        content_type, encoding = mimetypes.guess_type(self.url.path)
        content_type = response.getheader('Content-Type', content_type)
        content_type = params.pop('content_type', content_type)
        encoding = response.getheader('Content-Encoding', encoding)
        encoding = params.pop('content_encoding', encoding)
        content = response.read()
        content = content_encodings.get(encoding).decode(content)
        return content_types.get(content_type).parse(content, **params)

    def write(self, content):
        self.client.request('PUT', self._argument(), *self._write(content))
        response = self.client.getresponse()
        if response.status not in [200, 201, 204]:
            raise HTTPBadResponse(response)

    def _write(self, content):
        params = self.params.copy()
        content_type, encoding = mimetypes.guess_type(self.url.path)
        content_type = params.pop('content_type', content_type)
        encoding = params.pop('content_encoding', encoding)
        content = content_types.get(content_type).parse(content, **params)
        content = content_encodings.get(encoding).decode(content)
        return content, {'Content-Type': content_type,
                         'Content-Encoding': encoding or 'identity'}

    def erase(self):
        self.client.request('DELETE', self._argument())
        response = self.client.getresponse()
        if response.status not in [200, 202, 204]:
            raise HTTPBadResponse(response)


def read(url, **args):
    """Get the file/direcotry from a file URL."""
    with HTTPResource(url, **args) as resource:
        return resource.read()


def write(url, content, **args):
    """Put the object/collection into a file URL."""
    with HTTPResource(url, **args) as resource:
        resource.write(content)


def erase(url, **args):
    """Remove the sample from a file URL."""
    with HTTPResource(url, **args) as resource:
        resource.erase()
