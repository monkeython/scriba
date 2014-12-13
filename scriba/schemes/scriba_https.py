"""Handle http URL"""

import httplib
import socket

import scriba.scheme.scriba_http as http_scheme

import multipla

content_encodings = multipla.power_up('scriba.content_encodings')
content_types = multipla.power_up('scriba.content_types')


class HTTPSResource(http_scheme.HTTPResource):
    def __enter__(self):
        params = (self.url.hostname,
                  self.url.port or httplib.HTTPS_PORT,
                  self.params.get('keyfile'),
                  self.params.get('certfile'),
                  self.params.get('strict', True),
                  self.params.get('timeout', socket._GLOBAL_DEFAULT_TIMEOUT))
        self.client = httplib.HTTPSConnection(*params)
        return self


def read(url, **args):
    """Get the file/direcotry from a file URL."""
    with HTTPSResource(url, **args) as resource:
        return resource.read()


def write(url, content, **args):
    """Put the object/collection into a file URL."""
    with HTTPSResource(url, **args) as resource:
        resource.write(content)


def erase(url, **args):
    """Remove the sample from a file URL."""
    with HTTPSResource(url, **args) as resource:
        resource.erase()
