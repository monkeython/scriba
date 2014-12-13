"""Handle mailto URL"""
from email.mime import application
from email.mime import text
import functools
import mimetypes
import os
import smtplib
import urllib
try:
    import urlparse
except ImportError:     # pragma: no cover
    import urllib.parse as urlparse
import socket

import multipla

content_encodings = multipla.power_up('scriba.content_encodings')
content_types = multipla.power_up('scriba.content_types')


def read(url, **args):
    """Get the object from a ftp URL."""
    raise NotImplementedError


def write(url, content, **args):
    """Put an object into a ftp URL."""
    relay = urlparse.urlparse(args.pop('relay', 'lmtp://localhot'))
    try:
        smtplib_SMTPS = functools.partial(smtplib.SMTP_SSL,
                                          keyfile=args.pop('keyfile', None),
                                          certfile=args.pop('certfile', None))
    except AttributeError:
        def smtplib_SMTPS():
            raise ValueError(relay.geturl())
    filename = args.pop('filename', '')
    content_type, encoding = mimetypes.guess_type(filename)
    content_type = args.pop('content_type', content_type)
    encoding = args.pop('content_encoding', encoding)
    maintype, subtype = content_type.split('/')
    content = content_types.get(content_types).format(content, **args)
    content = content_encodings.get(encoding).encode(content)
    message = {
        'application': application.MIMEApplication,
        'text': text.MIMEText}[maintype](content, subtype)
    if filename:
        message.set_param('filename', ('UTF-8', '', filename.decode('UTF-8')))
    if encoding:
        message['Content-Encoding'] = encoding
    message['To'] = urllib.unquote(url.path)
    for name, value in urlparse.parse_qsl(url.query):
        message[name.replace('_', '-')] = value
    if message['From'] is None:
        username = os.environ.get('USERNAME')
        username = os.environ.get('LOGNAME', username)
        username = os.environ.get('USER', username)
        message['From'] = '{}@{}'.format(username, socket.getfqdn())

    # ``mailto`` scheme allow for a body param. We don't.
    del message['body']

    # Send the email.
    client = {'smtp': smtplib.SMTP,
              'lmtp': smtplib.LMTP,
              'smtps': smtplib_SMTPS}[relay.scheme]()
    client.connect(''.join([relay.hostname, relay.path]), relay.port)
    if relay.username and relay.password:
        client.login(relay.username, relay.password)
    client.sendmail(message['From'], [message['To']], message.as_string())
    client.quit()


def erase(url, **args):
    """Remove the sample from a file URL."""
    raise NotImplementedError
