import ftplib

import scriba.schemes.scriba_ftp as ftp_scheme


class FTPSResource(ftp_scheme.FTPResource):

    def __init__(self, url, **params):
        self.url = url
        self.params = params
        keyfile = self.params.pop('keyfile', None)
        certfile = self.params.pop('certfile', None)
        self.client = ftplib.FTP_TLS(keyfile=keyfile, certfile=certfile)

    def __enter__(self):
        self._connect(self.url.port or 990)
        self.client.prot_p()
        return self


def read(url, **args):
    """Get the object from a ftps URL."""
    with FTPSResource(url, **args) as resource:
        return resource.read()


def write(url, content, **args):
    """Put an object into a ftps URL."""
    with FTPSResource(url, **args) as resource:
        resource.write(content)


def erase(url, **args):
    """Remove the sample from a ftps URL."""
    with FTPSResource(url, **args) as resource:
        resource.erase()
