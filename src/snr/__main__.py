#!/bin/python3

# :::::::::::::::[]::::::::::::: #
# :::: /_> |U_U| || /_> /_> :::: #
# :::: <=/ |T-T| || <=/ <=/ :::: #
# ::::::::SHISS DOTFILES:::::::: #
# https://github.com/gzygmanski: #
# gzygmanski@hotmail.com:::::::: #

import os
import sys
import curses
import snr.reader as Reader
import snr.parser as Parser
import snr.screen as Screen
import snr.utilities as Utilities

def main():


    # :::: APP INFO :::::::::::::::: #

    VERSION = 'v0.7.106-alpha'
    APP = 'Simple Novel Reader'

    # :::: KEYBINDINGS ::::::::::::: #

    PAGE_UP = [ord('n'), ord('j'), ord(' ')]
    PAGE_DOWN = [ord('p'), ord('k')]
    NEXT_CHAPTER = [ord('N'), ord('l')]
    PREVIOUS_CHAPTER = [ord('P'), ord('h')]
    START_OF_CHAPTER = [ord('g'), ord('0')]
    END_OF_CHAPTER = [ord('G'), ord('$')]
    DARK_MODE = [ord('r')]
    SPEED_MODE = [ord('s')]
    HIGHLIGHT = [ord('v')]
    DOUBLE_PAGE = [ord('d')]
    JUSTIFY_FULL = [ord('f')]
    V_PADDING_UP = [ord('>')]
    H_PADDING_UP = [ord('.')]
    V_PADDING_DOWN = [ord('<')]
    H_PADDING_DOWN = [ord(',')]
    PE_LINE_UP = [ord(']')]
    PE_LINE_DOWN = [ord('[')]
    TOC = [ord('t'), 9]
    SELECT = [curses.KEY_ENTER, ord('o'), 13]
    HELP = [ord('?'), curses.KEY_F1]
    QUICKMARK = [ord('m')]
    QUICKMARK_SLOT = [ord(str(x)) for x in range(1, 10)]
    QUICKMARK_CLEAR = [ord('c')]
    QUICKMARK_ALL = [ord('a')]
    BOOKMARK = [ord('b')]
    BOOKMARK_NEW = [ord('B')]
    BOOKMARK_REMOVE = [ord('x')]
    BOOKMARK_EDIT = [ord('e')]
    BOOKMARK_DESCRIBE = [ord('l'), ord('d')]
    ESCAPE = [curses.KEY_BACKSPACE, 8, 27]
    REFRESH = [ord('R'), curses.KEY_F5]
    QUIT = [ord('q')]

    # :::: BOOK INIT ::::::::::::::: #

    state = Reader.StateReader()
    try:
        fileinput = os.path.abspath(sys.argv[1])
    except IndexError:
        fileinput = state.get_path()
        default = True
    else:
        default = False

    reader = Reader.FileReader(fileinput)
    toc_file = reader.get_toc_file()
    content_file = reader.get_content_file()
    path = reader.get_directory_path(toc_file)
    book = Parser.BookContent(path, toc_file, content_file)
    book_title = book.get_document_title()

    # :::: READER CONFIG ::::::::::: #

    config = Reader.ConfigReader()
    dark_mode = config.get_dark_mode()
    speed_mode = config.get_speed_mode()
    highlight = config.get_highlight()
    double_page = config.get_double_page()
    justify_full = config.get_justify_full()
    h_padding = config.get_horizontal_padding()
    v_padding = config.get_vertical_padding()
    pe_line = config.get_pe_multiplier()
    number_of_chapters = book.get_number_of_chapters()

    # :::: CURSES CONFIG ::::::::::: #

    std_screen = Screen.Screen(
        book_title,
        dark_mode,
        speed_mode,
        highlight,
        double_page,
        justify_full,
        VERSION,
        APP
    )
    screen = std_screen.get_screen()
    curses.noecho()
    curses.cbreak()
    curses.nonl()
    curses.curs_set(0)

    # :::: VARS :::::::::::::::::::: #

    escape = False
    screen_update = True
    content_update = False

    if default:
        current_chapter = state.get_chapter()
        page_index = state.get_index()
        quickmarks = Utilities.Quickmarks(state.get_quickmarks())
        bookmarks = Utilities.Bookmarks(state.get_bookmarks())
    elif state.exists(book_title):
        current_chapter = state.get_chapter(book_title)
        page_index = state.get_index(book_title)
        quickmarks = Utilities.Quickmarks(state.get_quickmarks(book_title))
        bookmarks = Utilities.Bookmarks(state.get_bookmarks(book_title))
    else:
        current_chapter = 0
        page_index = 0
        quickmarks = Utilities.Quickmarks()
        bookmarks = Utilities.Bookmarks()

    content_pages = Screen.ContentPages(
        screen,
        book,
        current_chapter,
        dark_mode,
        speed_mode,
        highlight,
        double_page,
        justify_full,
        v_padding,
        h_padding,
        pe_line
    )
    toc_pages = Screen.TocPages(
        screen,
        book,
        current_chapter,
        dark_mode,
        speed_mode,
        highlight,
        double_page,
        justify_full,
        v_padding,
        h_padding
    )
    help_pages = Screen.HelpPages(
        screen,
        book,
        current_chapter,
        dark_mode,
        speed_mode,
        highlight,
        double_page,
        justify_full,
        v_padding,
        h_padding
    )
    bookmark_pages = Screen.BookmarkPages(
        screen,
        book,
        current_chapter,
        bookmarks,
        dark_mode,
        speed_mode,
        highlight,
        double_page,
        justify_full,
        v_padding,
        h_padding
    )

    current_page = content_pages.get_page_by_index(page_index)

    while escape == False:
        if current_chapter == number_of_chapters:
            curses.endwin()
            state.save(
                fileinput,
                book_title,
                current_chapter - 1,
                content_pages.get_current_page_index(current_page - 1),
                quickmarks.get_quickmarks(),
                bookmarks.get_bookmarks()
            )
            break

        if screen_update:
            curses.endwin()
            std_screen = Screen.Screen(
                book_title,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                VERSION,
                APP
            )
            screen = std_screen.get_screen()
            std_screen.redraw()
            screen_update = False

        if content_update:
            content_pages = Screen.ContentPages(screen,
                book,
                current_chapter,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                v_padding,
                h_padding,
                pe_line
            )
            toc_pages = Screen.TocPages(
                screen,
                book,
                current_chapter,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                v_padding,
                h_padding
            )
            help_pages = Screen.HelpPages(
                screen,
                book,
                current_chapter,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                v_padding,
                h_padding
            )
            bookmark_pages = Screen.BookmarkPages(
                screen,
                book,
                current_chapter,
                bookmarks,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                v_padding,
                h_padding,
            )
            content_update = False

        content_pages.print_page(current_page, quickmarks)

        x = screen.getch()

        if x in PAGE_UP:
                if not double_page:
                    current_page += 1
                else:
                    current_page += 2
                if current_page >= content_pages.get_number_of_pages():
                    current_chapter += 1
                    current_page = 0
                    content_update = True

        if x in PAGE_DOWN:
            if not double_page:
                current_page -= 1
            else:
                current_page -= 2
            if current_page < 0 and current_chapter != 0:
                current_chapter -= 1
                content_pages = Screen.ContentPages(screen, book, current_chapter, dark_mode, speed_mode, highlight, \
                    double_page, justify_full, v_padding, h_padding, pe_line)
                if not double_page or content_pages.get_number_of_pages() < 2:
                    current_page = content_pages.get_number_of_pages() - 1
                else:
                    current_page = content_pages.get_number_of_pages() - 2
            elif current_page < 0 and current_chapter == 0:
                current_page = 0

        if x in NEXT_CHAPTER:
            if current_chapter != number_of_chapters:
                current_chapter += 1
                current_page = 0
                content_update = True

        if x in PREVIOUS_CHAPTER:
            if current_chapter != 0:
                current_chapter -= 1
                current_page = 0
                content_update = True

        if x in START_OF_CHAPTER:
            current_page = 0

        if x in END_OF_CHAPTER:
            current_page = content_pages.get_number_of_pages() - 1

        if x in DARK_MODE:
            dark_mode = not dark_mode
            screen_update = True
            content_update = True

        if x in SPEED_MODE:
            speed_mode = not speed_mode
            screen_update = True
            content_update = True

        if x in HIGHLIGHT:
            highlight = not highlight
            screen_update = True
            content_update = True

        if x in DOUBLE_PAGE:
            double_page = not double_page
            screen_update = True
            content_update = True

        if x in JUSTIFY_FULL:
            justify_full = not justify_full
            screen_update = True
            content_update = True

        if x in V_PADDING_UP:
            v_padding = content_pages.increase_v_padding(v_padding)
            index = content_pages.get_current_page_index(current_page)
            content_pages = Screen.ContentPages(
                screen,
                book,
                current_chapter,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                v_padding,
                h_padding,
                pe_line
            )
            current_page = content_pages.get_page_by_index(index)
            del index
            screen_update = True

        if x in H_PADDING_UP:
            h_padding = content_pages.increase_h_padding(h_padding)
            index = content_pages.get_current_page_index(current_page)
            content_pages= Screen.ContentPages(
                screen,
                book,
                current_chapter,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                v_padding,
                h_padding,
                pe_line
            )
            current_page = content_pages.get_page_by_index(index)
            del index
            screen_update = True

        if x in V_PADDING_DOWN:
            v_padding = content_pages.decrease_v_padding(v_padding)
            index = content_pages.get_current_page_index(current_page)
            content_pages = Screen.ContentPages(screen,
                book,
                current_chapter,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                v_padding,
                h_padding,
                pe_line
            )
            current_page = content_pages.get_page_by_index(index)
            del index
            screen_update = True

        if x in H_PADDING_DOWN:
            h_padding = content_pages.decrease_h_padding(h_padding)
            index = content_pages.get_current_page_index(current_page)
            content_pages = Screen.ContentPages(
                screen,
                book,
                current_chapter,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                v_padding,
                h_padding,
                pe_line
            )
            current_page = content_pages.get_page_by_index(index)
            del index
            screen_update = True

        if x in PE_LINE_UP:
            pe_line = content_pages.increase_pe_multiplier()

        if x in PE_LINE_DOWN:
            pe_line = content_pages.decrease_pe_multiplier()

        if x in QUICKMARK_SLOT:
            if quickmarks.is_set(chr(x)):
                current_chapter = quickmarks.get_chapter(chr(x))
                content_pages = Screen.ContentPages(
                    screen,
                    book,
                    current_chapter,
                    dark_mode,
                    speed_mode,
                    highlight,
                    double_page,
                    justify_full,
                    v_padding,
                    h_padding,
                    pe_line
                )
                current_page = content_pages.get_page_by_index(quickmarks.get_index(chr(x)))

        if x in QUICKMARK_CLEAR:
            y = screen.getch()

            if y in QUICKMARK_SLOT:
                quickmarks.set_quickmark(
                    chr(y),
                    None,
                    None
                )

            if y in QUICKMARK_ALL:
                quickmarks = Utilities.Quickmarks()

        if x in QUICKMARK:
            content_pages.print_page(current_page, quickmarks, True)

            y = screen.getch()

            if y in QUICKMARK_SLOT:
                quickmarks.set_quickmark(
                    chr(y),
                    current_chapter,
                    content_pages.get_current_page_index(current_page)
                )

        if x in BOOKMARK_NEW:
            index = content_pages.get_current_page_index(current_page)
            bookmarks.create(current_chapter, index)
            screen_update = True
            content_update = True
            del index

        if x in BOOKMARK:
            escape_bookmark = False
            current_bookmark_page = 0
            current_bookmark_pos = 0
            while escape_bookmark == False:
                bookmark_pages.print_page(current_bookmark_page, current_bookmark_pos)

                y = screen.getch()

                if y in PAGE_UP:
                    if bookmarks.has_bookmarks():
                        current_bookmark_pos += 1
                        if current_bookmark_pos == \
                            bookmark_pages.get_number_of_positions(current_bookmark_page):
                            current_bookmark_pos = 0
                            if current_bookmark_page < bookmark_pages.get_number_of_pages() - 1:
                                current_bookmark_page += 1
                            else:
                                current_bookmark_page = 0

                if y in PAGE_DOWN:
                    if bookmarks.has_bookmarks():
                        current_bookmark_pos -= 1
                        if current_bookmark_pos == -1:
                            if current_bookmark_page > 0:
                                current_bookmark_page -= 1
                            else:
                                current_bookmark_page = bookmark_pages.get_number_of_pages() - 1
                            current_bookmark_pos = \
                                bookmark_pages.get_number_of_positions(current_bookmark_page) - 1

                if y in SELECT:
                    if bookmarks.has_bookmarks():
                        bookmark_key = \
                            bookmark_pages.get_position_id(current_bookmark_page, current_bookmark_pos)
                        current_chapter = bookmarks.get_chapter(bookmark_key)
                        content_pages = Screen.ContentPages(
                            screen,
                            book,
                            current_chapter,
                            dark_mode,
                            speed_mode,
                            highlight,
                            double_page,
                            justify_full,
                            v_padding,
                            h_padding,
                            pe_line
                        )
                        current_page = content_pages.get_page_by_index(bookmarks.get_index(bookmark_key))
                    escape_bookmark = True
                    content_update = True

                if y in BOOKMARK_REMOVE:
                    if bookmarks.has_bookmarks():
                        bookmark_key = \
                            bookmark_pages.get_position_id(current_bookmark_page, current_bookmark_pos)
                        bookmarks.remove(bookmark_key)
                        bookmark_pages = Screen.BookmarkPages(
                            screen,
                            book,
                            current_chapter,
                            bookmarks,
                            dark_mode,
                            speed_mode,
                            highlight,
                            double_page,
                            justify_full,
                            v_padding,
                            h_padding
                        )
                        if bookmarks.has_bookmarks():
                            if current_bookmark_page > bookmark_pages.get_number_of_pages() - 1:
                                current_bookmark_page = bookmark_pages.get_number_of_pages() - 1
                            if current_bookmark_pos > bookmark_pages.get_number_of_positions(current_bookmark_page) - 1:
                                current_bookmark_pos = bookmark_pages.get_number_of_positions(current_bookmark_page) - 1

                if y in BOOKMARK_EDIT:
                    if bookmarks.has_bookmarks():
                        bookmark_key = \
                            bookmark_pages.get_position_id(current_bookmark_page, current_bookmark_pos)
                        bookmarks.edit(bookmark_key)
                        bookmark_pages = Screen.BookmarkPages(
                            screen,
                            book,
                            current_chapter,
                            bookmarks,
                            dark_mode,
                            speed_mode,
                            highlight,
                            double_page,
                            justify_full,
                            v_padding,
                            h_padding
                        )
                        curses.endwin()
                        std_screen = Screen.Screen(
                            book_title,
                            dark_mode,
                            speed_mode,
                            highlight,
                            double_page,
                            justify_full,
                            VERSION,
                            APP
                        )
                        screen = std_screen.get_screen()
                        std_screen.redraw()
                        index = content_pages.get_current_page_index(current_page)
                        content_pages = Screen.ContentPages(
                            screen,
                            book,
                            current_chapter,
                            dark_mode,
                            speed_mode,
                            highlight,
                            double_page,
                            justify_full,
                            v_padding,
                            h_padding,
                            pe_line
                        )
                        current_page = content_pages.get_page_by_index(index)
                        current_description_page = 0
                        content_pages.print_page(current_page, quickmarks)
                        del index

                if y in BOOKMARK_DESCRIBE:
                    if bookmarks.has_bookmarks():
                        escape_description = False
                        current_description_page = 0
                        bookmark_key = \
                            bookmark_pages.get_position_id(current_bookmark_page, current_bookmark_pos)
                        bookmark_description_pages = Screen.BookmarkDescribePages(
                            screen,
                            book,
                            current_chapter,
                            bookmarks,
                            bookmark_key,
                            dark_mode,
                            speed_mode,
                            highlight,
                            double_page,
                            justify_full,
                            v_padding,
                            h_padding
                        )

                        while escape_description == False:
                            bookmark_description_pages.print_page(current_description_page)

                            z = screen.getch()

                            if z in PAGE_UP:
                                current_description_page += 1
                                if current_description_page == bookmark_description_pages.get_number_of_pages():
                                    current_description_page = 0

                            if z in PAGE_DOWN:
                                current_description_page -= 1
                                if current_description_page < 0:
                                    current_description_page = bookmark_description_pages.get_number_of_pages() - 1

                            if z in BOOKMARK_DESCRIBE or y in ESCAPE:
                                escape_description = True

                            if z in REFRESH:
                                screen_update = True
                                content_update = True
                                escape_description = True

                            if z in QUIT:
                                escape = True
                                escape_description = True
                                curses.endwin()
                                state.save(
                                    fileinput,
                                    book_title,
                                    current_chapter,
                                    content_pages.get_current_page_index(current_page),
                                    quickmarks.get_quickmarks(),
                                    bookmarks.get_bookmarks()
                                )

                            if z == curses.KEY_RESIZE:
                                curses.endwin()
                                std_screen = Screen.Screen(
                                    book_title,
                                    dark_mode,
                                    speed_mode,
                                    highlight,
                                    double_page,
                                    justify_full,
                                    VERSION,
                                    APP
                                )
                                screen = std_screen.get_screen()
                                std_screen.redraw()
                                index = content_pages.get_current_page_index(current_page)
                                content_pages = Screen.ContentPages(
                                    screen,
                                    book,
                                    current_chapter,
                                    dark_mode,
                                    speed_mode,
                                    highlight,
                                    double_page,
                                    justify_full,
                                    v_padding,
                                    h_padding,
                                    pe_line
                                )
                                current_page = content_pages.get_page_by_index(index)
                                current_description_page = 0
                                del index

                if y in BOOKMARK or y in ESCAPE:
                    escape_bookmark = True

                if y in REFRESH:
                    screen_update = True
                    content_update = True
                    escape_bookmark = True

                if y in QUIT:
                    escape = True
                    escape_bookmark = True
                    state.save(
                        fileinput,
                        book_title,
                        current_chapter,
                        content_pages.get_current_page_index(current_page),
                        quickmarks.get_quickmarks(),
                        bookmarks.get_bookmarks()
                    )
                    curses.endwin()

                if y == curses.KEY_RESIZE:
                    curses.endwin()
                    std_screen = Screen.Screen(
                        book_title,
                        dark_mode,
                        speed_mode,
                        highlight,
                        double_page,
                        justify_full,
                        VERSION,
                        APP
                    )
                    screen = std_screen.get_screen()
                    std_screen.redraw()
                    index = content_pages.get_current_page_index(current_page)
                    content_pages = Screen.ContentPages(
                        screen,
                        book,
                        current_chapter,
                        dark_mode,
                        speed_mode,
                        highlight,
                        double_page,
                        justify_full,
                        v_padding,
                        h_padding,
                        pe_line
                    )
                    current_page = content_pages.get_page_by_index(index)
                    current_bookmark_page = 0
                    del index

        if x in TOC:
            escape_toc = False
            current_toc_page = 0
            current_toc_pos = 0
            while escape_toc == False:
                toc_pages.print_page(current_toc_page, current_toc_pos)

                y = screen.getch()

                if y in PAGE_UP:
                    current_toc_pos += 1
                    if current_toc_pos == \
                        toc_pages.get_number_of_positions(current_toc_page):
                        current_toc_pos = 0
                        if current_toc_page < toc_pages.get_number_of_pages() - 1:
                            current_toc_page += 1
                        else:
                            current_toc_page = 0

                if y in PAGE_DOWN:
                    current_toc_pos -= 1
                    if current_toc_pos == -1:
                        if current_toc_page > 0:
                            current_toc_page -= 1
                        else:
                            current_toc_page = toc_pages.get_number_of_pages() - 1
                        current_toc_pos = \
                            toc_pages.get_number_of_positions(current_toc_page) - 1

                if y in SELECT:
                    current_page = 0
                    current_chapter = \
                        toc_pages.get_position_id(current_toc_page, current_toc_pos) - 1
                    escape_toc = True
                    content_update = True

                if y in TOC or y in ESCAPE:
                    escape_toc = True

                if y in REFRESH:
                    screen_update = True
                    content_update = True
                    escape_toc = True

                if y in QUIT:
                    escape = True
                    escape_toc = True
                    state.save(
                        fileinput,
                        book_title,
                        current_chapter,
                        content_pages.get_current_page_index(current_page),
                        quickmarks.get_quickmarks(),
                        bookmarks.get_bookmarks()
                    )
                    curses.endwin()

                if y == curses.KEY_RESIZE:
                    curses.endwin()
                    std_screen = Screen.Screen(
                        book_title,
                        dark_mode,
                        speed_mode,
                        highlight,
                        double_page,
                        justify_full,
                        VERSION,
                        APP
                    )
                    screen = std_screen.get_screen()
                    std_screen.redraw()
                    index = content_pages.get_current_page_index(current_page)
                    content_pages = Screen.ContentPages(
                        screen,
                        book,
                        current_chapter,
                        dark_mode,
                        speed_mode,
                        highlight,
                        double_page,
                        justify_full,
                        v_padding,
                        h_padding,
                        pe_line
                    )
                    current_page = content_pages.get_page_by_index(index)
                    current_toc_page = 0
                    del index

        if x in HELP:
            escape_help = False
            current_help_page = 0
            while escape_help == False:
                help_pages.print_page(current_help_page)

                y = screen.getch()

                if y in PAGE_UP:
                    current_help_page += 1
                    if current_help_page == help_pages.get_number_of_pages():
                        current_help_page = 0

                if y in PAGE_DOWN:
                    current_help_page -= 1
                    if current_help_page < 0:
                        current_help_page = help_pages.get_number_of_pages() - 1

                if y in HELP or y in ESCAPE:
                    escape_help = True

                if y in REFRESH:
                    screen_update = True
                    content_update = True
                    escape_help = True

                if y in QUIT:
                    escape = True
                    escape_help = True
                    curses.endwin()
                    state.save(
                        fileinput,
                        book_title,
                        current_chapter,
                        content_pages.get_current_page_index(current_page),
                        quickmarks.get_quickmarks(),
                        bookmarks.get_bookmarks()
                    )

                if y == curses.KEY_RESIZE:
                    curses.endwin()
                    std_screen = Screen.Screen(
                        book_title,
                        dark_mode,
                        speed_mode,
                        highlight,
                        double_page,
                        justify_full,
                        VERSION,
                        APP
                    )
                    screen = std_screen.get_screen()
                    std_screen.redraw()
                    index = content_pages.get_current_page_index(current_page)
                    content_pages = Screen.ContentPages(
                        screen,
                        book,
                        current_chapter,
                        dark_mode,
                        speed_mode,
                        highlight,
                        double_page,
                        justify_full,
                        v_padding,
                        h_padding,
                        pe_line
                    )
                    current_page = content_pages.get_page_by_index(index)
                    current_help_page = 0
                    del index

        if x in REFRESH:
            curses.endwin()
            std_screen = Screen.Screen(
                book_title,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                VERSION,
                APP
            )
            screen = std_screen.get_screen()
            screen_update = True
            content_update = True

        if x in QUIT:
            escape = True
            curses.endwin()
            state.save(
                fileinput,
                book_title,
                current_chapter,
                content_pages.get_current_page_index(current_page),
                quickmarks.get_quickmarks(),
                bookmarks.get_bookmarks()
            )

        if x == curses.KEY_RESIZE:
            curses.endwin()
            std_screen = Screen.Screen(
                book_title,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                VERSION,
                APP
            )
            screen = std_screen.get_screen()
            screen_update = True
            index = content_pages.get_current_page_index(current_page)
            content_pages = Screen.ContentPages(
                screen,
                book,
                current_chapter,
                dark_mode,
                speed_mode,
                highlight,
                double_page,
                justify_full,
                v_padding,
                h_padding,
                pe_line
            )
            current_page = content_pages.get_page_by_index(index)
            del index

if __name__ == '__main__':
    main()
