#!/bin/python3

# :::::::::::::::[]::::::::::::: #
# :::: /_> |U_U| || /_> /_> :::: #
# :::: <=/ |T-T| || <=/ <=/ :::: #
# ::::::::SHISS DOTFILES:::::::: #
# https://github.com/gzygmanski: #
# gzygmanski@hotmail.com:::::::: #

import os, sys, curses
from snr.reader import ConfigReader, StateReader, FileReader
from snr.parser import BookContent
from snr.screen import Screen, Pager, Quickmarks

def main():

    # :::: APP INFO :::::::::::::::: #

    VERSION = 'v0.4.46-alpha'
    APP = 'Simple Novel Reader'

    # :::: KEYBINDINGS ::::::::::::: #

    PAGE_UP = [ord('n'), ord('j'), ord(' ')]
    PAGE_DOWN = [ord('p'), ord('k')]
    NEXT_CHAPTER = [ord('N'), ord('l')]
    PREVIOUS_CHAPTER = [ord('P'), ord('h')]
    START_OF_CHAPTER = [ord('g'), ord('0')]
    END_OF_CHAPTER = [ord('G'), ord('$')]
    DARK_MODE = [ord('r')]
    HIGHLIGHT = [ord('v')]
    PADDING_UP = [ord('>')]
    PADDING_DOWN = [ord('<')]
    TOC = [ord('t'), 9]
    SELECT = [curses.KEY_ENTER, ord('o'), 13]
    HELP = [ord('?')]
    QUICKMARK = [ord('m')]
    QUICKMARK_SLOT = [ord(str(x)) for x in range(1, 10)]
    QUICKMARK_CLEAR = [ord('c')]
    QUICKMARK_ALL = [ord('a')]
    ESCAPE = [curses.KEY_BACKSPACE, 8, 27]
    QUIT = [ord('q')]

    # :::: BOOK INIT ::::::::::::::: #

    state = StateReader()
    try:
        fileinput = sys.argv[1]
    except IndexError:
        fileinput = state.get_path()
        default = True
    else:
        default = False

    reader = FileReader(fileinput)
    toc_file = reader.get_toc_file()
    content_file = reader.get_content_file()
    path = reader.get_directory_path(toc_file)
    book = BookContent(path, toc_file, content_file)
    book_title = book.get_document_title()

    # :::: CURSES CONFIG ::::::::::: #

    init_screen = Screen(book_title, VERSION, APP)
    screen = init_screen.get_screen()
    curses.noecho()
    curses.cbreak()
    curses.nonl()
    curses.curs_set(0)

    # :::: READER CONFIG ::::::::::: #

    config = ConfigReader()
    dark_mode = config.get_dark_mode()
    highlight = config.get_highlight()
    h_padding = config.get_horizontal_padding()
    v_padding = config.get_vertical_padding()
    number_of_chapters = book.get_number_of_chapters()

    # :::: VARS :::::::::::::::::::: #

    escape = False
    init_screen_update = True
    init_chapter_update = False

    if default:
        current_chapter = state.get_chapter()
        page_index = state.get_index()
        quickmarks = Quickmarks(state.get_quickmarks())
    elif state.exists(book_title):
        current_chapter = state.get_chapter(book_title)
        page_index = state.get_index(book_title)
        quickmarks = Quickmarks(state.get_quickmarks(book_title))
    else:
        current_chapter = 0
        page_index = 0
        quickmarks = Quickmarks()

    page = Pager(screen, book, current_chapter, dark_mode, highlight, \
        v_padding, h_padding)
    current_page = page.get_page_by_index(page_index)

    while escape == False:
        if current_chapter == number_of_chapters:
            curses.endwin()
            break

        if init_screen_update:
            init_screen.redraw(dark_mode)
            init_screen_update = False

        if init_chapter_update:
            page = Pager(screen, book, current_chapter, dark_mode, highlight, \
                v_padding, h_padding)
            init_chapter_update = False

        page.print_page(current_page, quickmarks)

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
                    v_padding, h_padding)
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
            if v_padding < 6 and h_padding < 12:
                v_padding += 1
                h_padding += 1
                init_screen_update = True
                init_chapter_update = True

        if x in PADDING_DOWN:
            if v_padding > 1 and h_padding > 1:
                v_padding -= 1
                h_padding -= 1
                init_screen_update = True
                init_chapter_update = True

        if x in QUICKMARK_SLOT:
            if quickmarks.is_set(chr(x)):
                current_chapter = quickmarks.get_chapter(chr(x))
                page = Pager(screen, book, current_chapter, dark_mode, highlight, \
                    v_padding, h_padding)
                current_page = page.get_page_by_index(quickmarks.get_index(chr(x)))

        if x in QUICKMARK_CLEAR:
            y = screen.getch()

            if y in QUICKMARK_SLOT:
                quickmarks.set_quickmark(
                    chr(y),
                    None,
                    None
                )

            if y in QUICKMARK_ALL:
                quickmarks = Quickmarks()

        if x in QUICKMARK:
            page.print_page(current_page, quickmarks, True)

            y = screen.getch()

            if y in QUICKMARK_SLOT:
                quickmarks.set_quickmark(
                    chr(y),
                    current_chapter,
                    page.get_current_page_index(current_page)
                )

        if x in TOC:
            escape_toc = False
            current_toc_page = 0
            current_toc_pos = 0
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

                if y in TOC or y in ESCAPE:
                    escape_toc = True

                if y in QUIT:
                    escape = True
                    escape_toc = True
                    state.save(
                        fileinput,
                        book_title,
                        current_chapter,
                        page.get_current_page_index(current_page),
                        quickmarks.get_quickmarks()
                    )
                    curses.endwin()
                elif y == curses.KEY_RESIZE:
                    init_screen = Screen(book_title, VERSION, APP)
                    screen = init_screen.get_screen()
                    init_screen.redraw(dark_mode)
                    page = Pager(screen, book, current_chapter, dark_mode, highlight, \
                        padding, padding)

        if x in HELP:
            escape_help = False
            current_help_page = 0
            while escape_help == False:
                page.print_help_page(current_help_page)

                y = screen.getch()

                if y in PAGE_UP:
                    current_help_page += 1
                    if current_help_page == page.get_number_of_help_pages():
                        current_help_page = 0

                if y in PAGE_DOWN:
                    current_help_page -= 1
                    if current_help_page <= 0:
                        current_help_page = page.get_number_of_help_pages() - 1

                if y in HELP or y in ESCAPE:
                    escape_help = True

                if y in QUIT:
                    escape = True
                    escape_help = True
                    curses.endwin()
                    state.save(
                        fileinput,
                        book_title,
                        current_chapter,
                        page.get_current_page_index(current_page),
                        quickmarks.get_quickmarks()
                    )
                elif y == curses.KEY_RESIZE:
                    init_screen = Screen(book_title, VERSION, APP)
                    screen = init_screen.get_screen()
                    init_screen.redraw(dark_mode)
                    page = Pager(screen, book, current_chapter, dark_mode, highlight, \
                        padding, padding)
        if x in QUIT:
            escape = True
            curses.endwin()
            state.save(
                fileinput,
                book_title,
                current_chapter,
                page.get_current_page_index(current_page),
                quickmarks.get_quickmarks()
            )
        elif x == curses.KEY_RESIZE:
            init_screen = Screen(book_title, VERSION, APP)
            screen = init_screen.get_screen()
            init_screen_update = True
            init_chapter_update = True

if __name__ == '__main__':
    main()
