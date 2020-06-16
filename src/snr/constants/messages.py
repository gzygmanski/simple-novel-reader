#!/usr/bin/env python3

from snr.constants import info

_header_line = '\n' + '-' * (len(info.APP) + len(info.VERSION) + 1) + '\n'

HEADER = _header_line + info.APP + ' ' + info.VERSION + _header_line
CONTACT = _header_line \
    + info.SITE + '\n' \
    + info.EMAIL + '\n'
MISSING_KEY = 'Missing key: '
SAVE_STATE = 'Saving state ...'
LOAD_STATE = 'Loading state ...'
def DICT_INSTALL(target):
    return 'Downloading dictionary: ' + target + ' ...'
def DICT_INSTALLED(target):
    return target + ': installed'
def DICT_INSTALL_FAILED(target):
    return 'Failed to download: ' + target
def ZIP_EXTRACT(target, destination):
    return 'Extracting file: ' + target + ' to ' + destination + ' ...'
def CREATE(target):
    return 'Creating: ' + target + ' ...'
ERR_NO_PATH = '''\
ERR_NO_PATH:
    Path not provided. If this is the first time you start application or path of book changed provide path to the epub file.

USAGE: snr path/to/epub/file
E.G.: snr ~/Book.epub''' + '\n'
ERR_INVALID_PATH = '''\
ERR_INVALID_PATH:
    Provided path is invalid. You must specify epub file.

USAGE: snr path/to/epub/file
E.G.: snr ~/Book.epub''' + '\n'
ERR_INVALID_CONFIG = '''\
ERR_INVALID_CONFIG:
    Invalid config file. The key is missing.
    Check the wiki to learn more about configuration file:

''' + info.WIKI_CONF + '\n'
ERR_TOC_NOT_FOUND = '''\
ERR_TOC_NOT_FOUND:
    'toc.ncx' file not found.
'''
ERR_CONTENT_NOT_FOUND = '''\
ERR_CONTENT_NOT_FOUND:
    'content.ncx' file not found.
'''
ERR_PARSER_FAILED = '''\
ERR_PARSER_FAILED:
    Parser failed to scrap the book content.'''
ERR_PARSER_NO_TOC= '''\
    Empty toc_list or not found.
'''
ERR_PARSER_NO_REFERENCE = '''\
    Empty toc_reference or not found.
'''
ERR_PARSER_NO_ORDER = '''\
    Empty order_list or not found.
'''
ERR_PARSER_NO_CONTENT = '''\
    Empty content_dict or not found.
'''
