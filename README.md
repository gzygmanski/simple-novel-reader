<img src="https://raw.githubusercontent.com/gzygmanski/simple-novel-reader/0.9.x/images/snr_h.svg">

[![GitHub license](https://img.shields.io/github/license/gzygmanski/simple-novel-reader)](https://github.com/gzygmanski/simple-novel-reader/blob/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/simple-novel-reader.svg)](https://badge.fury.io/py/simple-novel-reader)
[![Downloads](https://pepy.tech/badge/simple-novel-reader)](https://pepy.tech/project/simple-novel-reader)

CLI light novel reader written in Python for Linux.

## Dependencies:
* BeautifulSoup4
* lxml
* langcodes
* PyHyphen

## Setup/Usage:
To install:
```bash
pip3 install simple-novel-reader
```
To run program:
```bash
snr \path\to\epub\file
```
On the first run you need to specify a file, next time the file will be opened as default.

## Features:
* save reading progress and quickmarks of a book upon exit,
* starting program without argument will open last read book,
* quickmarks,
* bookmarks,
* colored dialogs,
* dual page view.

## Screenshots:
<img src="https://raw.githubusercontent.com/gzygmanski/simple-novel-reader/master/images/screen.png" width="70%">
