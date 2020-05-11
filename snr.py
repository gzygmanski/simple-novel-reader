#!/bin/python3

# :::::::::::::::[]::::::::::::: #
# :::: /_> |U_U| || /_> /_> :::: #
# :::: <=/ |T-T| || <=/ <=/ :::: #
# ::::::::SHISS DOTFILES:::::::: #
# https://github.com/gzygmanski: #
# gzygmanski@hotmail.com:::::::: #

import os, sys, curses
from imports.reader import FileReader
from imports.parser import TocContent
from imports.screen import Screen, Pager

# :::: APP INFO :::::::::::::::: #

VERSION = '0.1-dev'
APP = 'Simple Novel Reader'

# :::: KEYBINDINGS ::::::::::::: #

PAGE_UP = {ord('n'), ord('j')}
PAGE_DOWN = {ord('p'), ord('k'), ord(' ')}
NEXT_CHAPTER = {ord('N'), ord('l')}
PREVIOUS_CHAPTER = {ord('P'), ord('h')}
START_OF_CHAPTER = {ord('g'), ord('0')}
END_OF_CHAPTER = {ord('G'), ord('$')}
DARK_MODE = {ord('r')}
QUIT = {ord('q'), 27}


# :::: CURSES CONFIG ::::::::::: #

init_screen = Screen(VERSION, APP)
screen = init_screen.get_screen()
curses.noecho()
curses.cbreak()
curses.nonl()
curses.curs_set(0)


def main(argv):
    escape = False
    fileinput = argv[1]
    reader = FileReader(fileinput)
    toc_file = reader.get_toc_file()
    path = reader.get_directory_path(toc_file)
    book = TocContent(path, toc_file)

    init_screen_update = True
    init_chapter_update = True
    dark_mode = True
    current_page = 0
    current_chapter = 0
    number_of_chapters = book.get_number_of_chapters()

    while escape == False:
        if current_chapter == number_of_chapters:
            curses.endwin()
            break

        if init_screen_update:
            init_screen.redraw()
            init_screen_update = False

        if init_chapter_update:
            page = Pager(screen, book, current_chapter, dark_mode)
            init_chapter_update = False

        page.print_page(current_page)

        x = screen.getch()

        if x in PAGE_UP:
            if current_page == page.get_number_of_pages() - 1:
                current_chapter += 1
                current_page = 0
                init_chapter_update = True
            else:
                current_page += 1

        if x in PAGE_DOWN:
            if current_page == 0 and current_chapter != 0:
                current_chapter -= 1
                page = Pager(screen, book, current_chapter, dark_mode)
                current_page = page.get_number_of_pages() - 1
            elif current_page == 0 and current_chapter == 0:
                current_page = 0
            else:
                current_page -= 1

        if x in NEXT_CHAPTER:
            if current_chapter != number_of_chapters:
                current_chapter += 1
                current_page = 0
                init_chapter_update = True

        if x in PREVIOUS_CHAPTER:
            if current_chapter != 0:
                current_chapter -= 1
                current_page = 0
                init_chapter_update = True

        if x in DARK_MODE:
            dark_mode = not dark_mode
            init_screen_update = True
            init_chapter_update = True

        if x in QUIT:
            escape = True
            curses.endwin()
        elif x == curses.KEY_RESIZE:
            init_screen_update = True
            init_chapter_update = True

if __name__ == '__main__':
    main(sys.argv)
