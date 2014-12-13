"""Handle mailto URL"""

import email
import os
import poplib
import socket

import multipla

content_encodings = multipla.power_up('scriba.content_encodings')
content_types = multipla.power_up('scriba.content_types')
email_mimes = multipla.power_up('scriba.email_mimes')


class BadPOP3Response(Exception):
    pass


def read(url, **args):
    """Get the object from a ftp URL."""
    all_ = args.pop('all', False)
    password = args.pop('password', '')
    if not password:
        raise ValueError('password')
    try:
        username, __ = url.username.split(';')
    except ValueError:
        username = url.username
    if not username:
        username = os.environ.get('USERNAME')
        username = os.environ.get('LOGNAME', username)
        username = os.environ.get('USER', username)
    client = poplib.POP3(url.hostname, url.port or poplib.POP3_PORT,
                         args.pop('timeout', socket._GLOBAL_DEFAULT_TIMEOUT))
    response, count, __ = client.apop(username, password)
    if 'OK' not in response:
        raise BadPOP3Response(response)
    if count == 0:
        raise ValueError('count: 0')
    collection = []
    for id_ in range(count if all_ is True else 1):
        response, lines, __ = client.retr(id_ + 1)
        if 'OK' not in response:
            raise BadPOP3Response(response)
        client.dele(id_ + 1)
        message = email.message_from_string('\n'.join(lines))
        content_type = message.get_content_type()
        filename = message.get_filename('')
        encoding = message['Content-Encoding']
        content = message.get_payload(decode=True)
        content = content_encodings.get(encoding).decode(content)
        content = content_types.get(content_type).parse(content)
        collection.append((filename, content))
    client.quit()
    return collection if len(collection) > 0 else collection[0][1]

#    01612147400
#    07443866622


def write(url, collection, **args):
    """Put an object into a ftp URL."""
    raise NotImplementedError


def erase(url, **args):
    """Remove the sample from a file URL."""
    raise NotImplementedError
