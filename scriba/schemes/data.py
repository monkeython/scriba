"""Handle the data URI"""

import base64
import re
import urllib

from cereal import content_types


def get(url, **args):
    """Loads an object from a data URI."""
    info_re = '(?P<mediatype>[^/]+/[^;]+(;[^=]+=[^;]+)*)?(?P<base64>;base64)?'
    info, data = url.path.split(',')
    info = re.match(info_re, info).groupdict()
    mediatype = info.setdefault('mediatype', 'text/plain;charset=US-ASCII')
    if ';' in mediatype:
        mimetype, params = mediatype.split(';', 1)
        params = [p.split('=') for p in params.split(';')]
        params = dict((k.strip(), v.strip()) for k, v in params)
    else:
        mimetype, params = mediatype, dict()
    data = base64.b64decode(data) if info['base64'] else urllib.unquote(data)
    return content_types.get(mimetype).parse(data, **params)


def put(url, object_, **args):
    """Writes an object to a data URI."""
    content_encoding = args.get('content_encoding', 'base64')
    default_content_type = ('text/plain', {'charset': 'US-ASCII'})
    content_type, params = args.get('content_type', default_content_type)
    data = content_types.get(content_type).format(object_, **params)
    args['data'].write('data:{}'.format(content_type))
    if params:
        args['data'].write(';{}={}'.format(k, v) for k, v in params.items())
    if content_encoding == 'base64':
        args['data'].write(';base64,{}'.format(base64.b64decode(data)))
    else:
        args['data'].write(',{}', urllib.quote(data)
    args['data'].seek(0)

def delete(url, **args):
    pass
