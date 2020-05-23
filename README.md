# Simple Novel Reader
This is an CLI light novel reader written in Python for Linux.

## Dependencies:
* BeautifulSoup4
* lxml

## Setup/Usage:
```bash
pip3 install simple-novel-reader
```
To run program: `snr \path\to\epub\file`. On the first run you need to specify a file, next time the file will be opened as default.

## Features:
* save reading progress and quickmarks of a book upon exit,
* starting program without argument will open last read book,
* quickmarks,
* colored dialogs.

## Todo:
* Features:
  + configurable colors from config.ini,
  + bookmarks,
  + dual page view,
  + speed reading view (the same as in koreader perception expander).
* Chores:
  + refactor and clean up code,
  + split main function to multiple files for better readability,
  + error handling.

## Screenshots:
![screen](https://raw.githubusercontent.com/gzygmanski/simple-novel-reader/master/screen.png "screen")
![screen2](https://raw.githubusercontent.com/gzygmanski/simple-novel-reader/master/screen2.png "screen2")
