"""Handle the data URI"""

import base64
import re
import urllib

import multipla


content_types = multipla.power_up('scriba.content_types')

data_re = """
    (?P<mediatype>
        (?P<maintype>[^/]+)/(?P<subtype>[^;]+)
            (?P<params>;[^=]+=[^;,]+)*
    )?
    (?P<base64>;base64)?
    ,
    (?P<data>.*)
"""
data_re = re.compile(data_re, re.VERBOSE)

def read(url, **args):
    """Loads an object from a data URI."""
    info, data = url.path.split(',')
    info = data_re.search(info).groupdict()
    mediatype = info.setdefault('mediatype', 'text/plain;charset=US-ASCII')
    if ';' in mediatype:
        mimetype, params = mediatype.split(';', 1)
        params = [p.split('=') for p in params.split(';')]
        params = dict((k.strip(), v.strip()) for k, v in params)
    else:
        mimetype, params = mediatype, dict()
    data = base64.b64decode(data) if info['base64'] else urllib.unquote(data)
    return content_types.get(mimetype).parse(data, **params)


def write(url, object_, **args):
    """Writes an object to a data URI."""
    default_content_type = ('text/plain', {'charset': 'US-ASCII'})
    content_encoding = args.get('content_encoding', 'base64')
    content_type, params = args.get('content_type', default_content_type)
    data = content_types.get(content_type).format(object_, **params)
    args['data'].write('data:{}'.format(content_type))
    for param, value in params.items():
        args['data'].write(';{}={}'.format(param, value))
    if content_encoding == 'base64':
        args['data'].write(';base64,{}'.format(base64.b64decode(data)))
    else:
        args['data'].write(',{}', urllib.quote(data))
    args['data'].seek(0)


def erase(url, **args):
    pass
