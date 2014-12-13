"""Handle JSON formatting/parsing."""

import json


def parse(binary, **params):
    """Turns a JSON structure into a python object."""
    encoding = params.get('charset', 'UTF-8')
    return json.loads(binary, encoding=encoding)


def format(item, **params):
    """Truns a python object into a JSON structure."""
    encoding = params.get('charset', 'UTF-8')
    return json.dumps(item, encoding=encoding)
