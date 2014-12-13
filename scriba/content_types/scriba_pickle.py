"""Handle PICKLE formatting/parsing of a frozen sample."""

import cPickle
import mimetypes

mimetypes.add_type('application/python-pickle', '.pickle')


def parse(binary, **params):
    """Turns a PICKLE structure into a python object."""
    return cPickle.loads(binary)


def format(item, **params):
    """Truns a python object into a PICKLE structure."""
    return cPickle.dumps(item)
