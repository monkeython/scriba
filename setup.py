import os
import sys

NAME = 'scriba'
PACKAGE = __import__(NAME)
AUTHOR, EMAIL = PACKAGE.__author__.rsplit(' ', 1)


with open('docs/index.rst', 'r') as INDEX:
    DESCRIPTION = INDEX.readline()

with open(os.path.join(WD, 'README.rst'), 'r') as README:
    LONG_DESCRIPTION = README.read()

URL = 'https://github.com/monkeython/%s' % NAME

EGG = {
    'name': NAME,
    'version': PACKAGE.__version__,
    'author': AUTHOR,
    'author_email': EMAIL.strip('<>'),
    'url': URL,
    'description': DESCRIPTION,
    'long_description': LONG_DESCRIPTION,
    'classifiers': PACKAGE.__classifiers__,
    'license': 'BSD',
    'keywords': PACKAGE.__keywords__,
    'packages': [NAME],
    'namespace_packages': [
        'scriba.schemes',
        'scriba.content_types',
        'scriba.content_encodings'],
    'install_requires': ['multipla'],
    'test_suite': 'tests.suite'
}

if __name__ == '__main__':
    import setuptools
    setuptools.setup(**EGG)
