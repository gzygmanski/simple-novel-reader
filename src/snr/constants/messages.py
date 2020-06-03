#!/bin/python3

from snr.constants import info

_header_line = '\n' + '-' * (len(info.APP) + len(info.VERSION) + 1) + '\n'

HEADER = _header_line + info.APP + ' ' + info.VERSION + _header_line
CONTACT = _header_line \
    + info.SITE + '\n' \
    + info.EMAIL + '\n'
MISSING_KEY = 'Missing key: '
ERR_NO_PATH = '''\
Path not provided. If this is the first time you start application provide path to the epub file.
USAGE: snr path/to/epub/file
E.G.: snr ~/Book.epub''' + _header_line
ERR_INVALID_CONFIG = '''\
Invalid config file. The key is missing.
Check the wiki to learn more about configuration file:
''' + info.WIKI_CONF + _header_line

