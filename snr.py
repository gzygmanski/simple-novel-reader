#!/bin/python3

# :::::::::::::::[]::::::::::::: #
# :::: /_> |U_U| || /_> /_> :::: #
# :::: <=/ |T-T| || <=/ <=/ :::: #
# ::::::::SHISS DOTFILES:::::::: #
# https://github.com/gzygmanski: #
# gzygmanski@hotmail.com:::::::: #

import os, sys, curses
from imports.reader import FileReader
from imports.parser import BookContent
from imports.screen import Screen, Pager

# :::: APP INFO :::::::::::::::: #

VERSION = 'v0.2.30-alpha'
APP = 'Simple Novel Reader'

# :::: KEYBINDINGS ::::::::::::: #

PAGE_UP = {ord('n'), ord('j'), ord(' ')}
PAGE_DOWN = {ord('p'), ord('k')}
NEXT_CHAPTER = {ord('N'), ord('l')}
PREVIOUS_CHAPTER = {ord('P'), ord('h')}
START_OF_CHAPTER = {ord('g'), ord('0')}
END_OF_CHAPTER = {ord('G'), ord('$')}
DARK_MODE = {ord('r')}
HIGHLIGHT = {ord('v')}
PADDING_UP = {ord('>')}
PADDING_DOWN = {ord('<')}
TOC = {ord('t'), 9}
SELECT = {curses.KEY_ENTER, ord('o'), 13}
QUIT = {ord('q'), 27}


def main(argv):

    # :::: BOOK INIT ::::::::::::::: #

    fileinput = argv[1]
    reader = FileReader(fileinput)
    toc_file = reader.get_toc_file()
    content_file = reader.get_content_file()
    path = reader.get_directory_path(toc_file)
    book = BookContent(path, toc_file, content_file)

    # :::: CURSES CONFIG ::::::::::: #

    init_screen = Screen(book.get_document_title(), VERSION, APP)
    screen = init_screen.get_screen()
    curses.noecho()
    curses.cbreak()
    curses.nonl()
    curses.curs_set(0)

    # :::: VARS :::::::::::::::::::: #

    escape = False
    init_screen_update = True
    init_chapter_update = True
    dark_mode = True
    highlight = True
    padding = 2
    current_page = 0
    current_chapter = 0
    current_toc_page = 0
    current_toc_pos = 0
    number_of_chapters = book.get_number_of_chapters()

    while escape == False:
        if current_chapter == number_of_chapters:
            curses.endwin()
            break

        if init_screen_update:
            init_screen.redraw(dark_mode)
            init_screen_update = False

        if init_chapter_update:
            page = Pager(screen, book, current_chapter, dark_mode, highlight, \
                padding, padding)
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
                page = Pager(screen, book, current_chapter, dark_mode, highlight, \
                    padding, padding)
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

        if x in START_OF_CHAPTER:
            current_page = 0

        if x in END_OF_CHAPTER:
            current_page = page.get_number_of_pages() - 1

        if x in DARK_MODE:
            dark_mode = not dark_mode
            init_screen_update = True
            init_chapter_update = True

        if x in HIGHLIGHT:
            highlight = not highlight
            init_screen_update = True
            init_chapter_update = True

        if x in PADDING_UP:
            if padding < 6:
                padding += 1
                init_screen_update = True
                init_chapter_update = True

        if x in PADDING_DOWN:
            if padding > 1:
                padding -= 1
                init_screen_update = True
                init_chapter_update = True

        if x in TOC:
            escape_toc = False
            while escape_toc == False:
                page.print_toc_page(current_toc_page, current_toc_pos)

                y = screen.getch()

                if y in PAGE_UP:
                    current_toc_pos += 1
                    if current_toc_pos == \
                        page.get_number_of_toc_positions(current_toc_page):
                        current_toc_pos = 0
                        if current_toc_page < page.get_number_of_toc_pages() - 1:
                            current_toc_page += 1
                        else:
                            current_toc_page = 0

                if y in PAGE_DOWN:
                    current_toc_pos -= 1
                    if current_toc_pos == -1:
                        if current_toc_page > 0:
                            current_toc_page -= 1
                        else:
                            current_toc_page = page.get_number_of_toc_pages() - 1
                        current_toc_pos = \
                            page.get_number_of_toc_positions(current_toc_page) - 1

                if y in SELECT:
                    current_page = 0
                    current_chapter = \
                        page.get_toc_position_id(current_toc_page, current_toc_pos) - 1
                    escape_toc = True
                    init_chapter_update = True

                if y in TOC:
                    escape_toc = True

                if y in QUIT:
                    escape = True
                    escape_toc = True
                    curses.endwin()

        if x in QUIT:
            escape = True
            curses.endwin()
        elif x == curses.KEY_RESIZE:
            init_screen_update = True
            init_chapter_update = True

if __name__ == '__main__':
    main(sys.argv)
