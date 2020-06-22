#!/usr/bin/env python3

import curses
import snr.constants.keybinds as Key
import snr.constants.messages as Msg
import snr.reader as Reader
import snr.parser as Parser
import snr.screen as Screen
import snr.utilities as Utilities

def snr(state, fileinput, args, default):

    # :::: READER CONFIG ::::::::::: #

    config = Reader.ConfigReader(args.verbose)

    try:
        dark_mode = args.dark_mode or config.get_dark_mode()
        speed_mode = args.speed_mode or config.get_speed_mode()
        highlight = args.highlight or config.get_highlight()
        double_page = args.double_page or config.get_double_page()
        justify_full = args.justify_full or config.get_justify_full()
        hyphenation = args.hyphenation or config.get_hyphenation()
        dict_download = args.dict_download or config.get_dict_download()
        h_padding = config.get_horizontal_padding()
        v_padding = config.get_vertical_padding()
        pe_line = config.get_pe_multiplier()
    except KeyError as err:
        print(Msg.HEADER)
        print(Msg.MISSING_KEY + str(err))
        print(Msg.ERR_INVALID_CONFIG)
        exit()

    modes = {
        'dark_mode': dark_mode,
        'speed_mode': speed_mode,
        'highlight': highlight,
        'double_page': double_page,
        'justify_full': justify_full,
        'hyphenation': hyphenation
    }

    # :::: BOOK INIT ::::::::::::::: #

    reader = Reader.FileReader(fileinput, args.verbose)
    toc_file = reader.get_toc_file()
    content_file = reader.get_content_file()
    path = reader.get_directory_path(toc_file)
    book = Parser.BookContent(path, toc_file, content_file, dict_download, args.lang, args.verbose)
    book_title = book.get_document_title()
    book_language = book.get_document_language()
    is_dict_installed = book.is_dict_installed()
    number_of_chapters = book.get_number_of_chapters()

    # :::: CURSES CONFIG ::::::::::: #

    std_screen = Screen.Screen(
        book_title,
        modes,
        is_dict_installed,
        book_language
    )
    screen = std_screen.get_screen()
    curses.noecho()
    curses.cbreak()
    curses.nonl()
    curses.curs_set(0)

    # :::: VARS :::::::::::::::::::: #

    escape = False
    screen_update = True
    content_update = True

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

    content_pages = Screen.ContentPages(screen,
        book,
        current_chapter,
        modes,
        v_padding,
        h_padding,
        pe_line
    )
    current_page = content_pages.get_page_by_index(page_index)
    index = None

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
                modes,
                is_dict_installed,
                book_language
            )
            screen = std_screen.get_screen()
            std_screen.redraw()
            screen_update = False

        if content_update:
            content_pages = Screen.ContentPages(screen,
                book,
                current_chapter,
                modes,
                v_padding,
                h_padding,
                pe_line
            )
            toc_pages = Screen.TocPages(
                screen,
                book,
                current_chapter,
                modes,
                v_padding,
                h_padding
            )
            help_pages = Screen.HelpPages(
                screen,
                book,
                current_chapter,
                modes,
                v_padding,
                h_padding
            )
            bookmark_pages = Screen.BookmarkPages(
                screen,
                book,
                current_chapter,
                bookmarks,
                modes,
                v_padding,
                h_padding,
            )
            if index is not None:
                current_page = content_pages.get_page_by_index(index)
                index = None
            content_update = False

        content_pages.print_page(current_page, bookmarks, quickmarks)

        x = screen.getch()

        if x in Key.PAGE_UP:
                if not content_pages.get_double_page():
                    current_page += 1
                else:
                    current_page += 2
                if current_page >= content_pages.get_number_of_pages():
                    current_chapter += 1
                    current_page = 0
                    content_update = True

        if x in Key.PAGE_DOWN:
            if not content_pages.get_double_page():
                current_page -= 1
            else:
                current_page -= 2
            if current_page < 0 and current_chapter != 0:
                current_chapter -= 1
                content_pages = Screen.ContentPages(
                    screen,
                    book,
                    current_chapter,
                    modes,
                    v_padding,
                    h_padding,
                    pe_line
                )
                if not content_pages.get_double_page() or content_pages.get_number_of_pages() < 2:
                    current_page = content_pages.get_number_of_pages() - 1
                else:
                    current_page = content_pages.get_number_of_pages() - 2
            elif current_page < 0 and current_chapter == 0:
                current_page = 0

        if x in Key.NEXT_CHAPTER:
            if current_chapter != number_of_chapters:
                current_chapter += 1
                current_page = 0
                content_update = True

        if x in Key.PREVIOUS_CHAPTER:
            if current_chapter != 0:
                current_chapter -= 1
                current_page = 0
                content_update = True

        if x in Key.START_OF_CHAPTER:
            current_page = 0

        if x in Key.END_OF_CHAPTER:
            current_page = content_pages.get_number_of_pages() - 1

        if x in Key.DARK_MODE:
            modes['dark_mode'] = not modes['dark_mode']
            screen_update = True
            content_update = True

        if x in Key.SPEED_MODE:
            modes['speed_mode'] = not modes['speed_mode']
            screen_update = True
            content_update = True

        if x in Key.HIGHLIGHT:
            modes['highlight'] = not modes['highlight']
            screen_update = True
            content_update = True

        if x in Key.DOUBLE_PAGE:
            modes['double_page'] = not modes['double_page']
            screen_update = True
            content_update = True

        if x in Key.JUSTIFY_FULL:
            modes ['justify_full'] = not modes['justify_full']
            screen_update = True
            content_update = True

        if x in Key.HYPHENATION:
            modes['hyphenation'] = not modes['hyphenation']
            screen_update = True
            content_update = True

        if x in Key.V_PADDING_UP:
            v_padding = content_pages.increase_v_padding(v_padding)
            index = content_pages.get_current_page_index(current_page)
            content_pages = Screen.ContentPages(
                screen,
                book,
                current_chapter,
                modes,
                v_padding,
                h_padding,
                pe_line
            )
            current_page = content_pages.get_page_by_index(index)
            screen_update = True

        if x in Key.H_PADDING_UP:
            h_padding = content_pages.increase_h_padding(h_padding)
            index = content_pages.get_current_page_index(current_page)
            content_pages= Screen.ContentPages(
                screen,
                book,
                current_chapter,
                modes,
                v_padding,
                h_padding,
                pe_line
            )
            current_page = content_pages.get_page_by_index(index)
            screen_update = True

        if x in Key.V_PADDING_DOWN:
            v_padding = content_pages.decrease_v_padding(v_padding)
            index = content_pages.get_current_page_index(current_page)
            content_pages = Screen.ContentPages(screen,
                book,
                current_chapter,
                modes,
                v_padding,
                h_padding,
                pe_line
            )
            current_page = content_pages.get_page_by_index(index)
            screen_update = True

        if x in Key.H_PADDING_DOWN:
            h_padding = content_pages.decrease_h_padding(h_padding)
            index = content_pages.get_current_page_index(current_page)
            content_pages = Screen.ContentPages(
                screen,
                book,
                current_chapter,
                modes,
                v_padding,
                h_padding,
                pe_line
            )
            current_page = content_pages.get_page_by_index(index)
            screen_update = True

        if x in Key.PE_LINE_UP:
            pe_line = content_pages.increase_pe_multiplier()

        if x in Key.PE_LINE_DOWN:
            pe_line = content_pages.decrease_pe_multiplier()

        if x in Key.QUICKMARK_SLOT:
            if quickmarks.is_set(chr(x)):
                current_chapter = quickmarks.get_chapter(chr(x))
                content_pages = Screen.ContentPages(
                    screen,
                    book,
                    current_chapter,
                    modes,
                    v_padding,
                    h_padding,
                    pe_line
                )
                current_page = content_pages.get_page_by_index(quickmarks.get_index(chr(x)))

        if x in Key.QUICKMARK_CLEAR:
            y = screen.getch()

            if y in Key.QUICKMARK_SLOT:
                quickmarks.set_quickmark(
                    chr(y),
                    None,
                    None
                )

            if y in Key.QUICKMARK_ALL:
                quickmarks = Utilities.Quickmarks()

        if x in Key.QUICKMARK:
            escape_quickmark = False
            current_index = content_pages.get_current_page_index(current_page)
            while escape_quickmark == False:
                content_pages.print_page(
                    current_page,
                    bookmarks,
                    quickmarks,
                    quickmark_change=True,
                    index=current_index
                )

                y = screen.getch()

                if y in Key.PAGE_UP:
                    current_index = content_pages.increase_index(current_index, current_page)

                if y in Key.PAGE_DOWN:
                    current_index = content_pages.decrease_index(current_index, current_page)

                if y in Key.QUICKMARK_SLOT:
                    quickmarks.set_quickmark(
                        chr(y),
                        current_chapter,
                        current_index
                    )
                    escape_quickmark = True

                if y in Key.QUIT:
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

                if y not in [*Key.PAGE_UP, *Key.PAGE_DOWN]:
                    escape_quickmark = True

        if x in Key.BOOKMARK_NEW:
            escape_bookmark = False
            current_index = content_pages.get_current_page_index(current_page)
            while escape_bookmark == False:
                content_pages.print_page(
                    current_page,
                    bookmarks,
                    quickmarks,
                    bookmark_change=True,
                    index=current_index
                )

                y = screen.getch()

                if y in Key.PAGE_UP:
                    current_index = content_pages.increase_index(current_index, current_page)

                if y in Key.PAGE_DOWN:
                    current_index = content_pages.decrease_index(current_index, current_page)

                if y in Key.SELECT:
                    bookmarks.create(current_chapter, current_index)
                    escape_bookmark = True
                    screen_update = True
                    content_update = True

                if y in Key.QUIT:
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

                if y not in [*Key.PAGE_UP, *Key.PAGE_DOWN]:
                    escape_bookmark = True

        if x in Key.BOOKMARK:
            escape_bookmark = False
            current_bookmark_page = 0
            current_bookmark_pos = 0
            while escape_bookmark == False:
                bookmark_pages.print_page(current_bookmark_page, current_bookmark_pos)

                y = screen.getch()

                if y in Key.PAGE_UP:
                    if bookmarks.has_bookmarks():
                        current_bookmark_pos += 1
                        if current_bookmark_pos == \
                            bookmark_pages.get_number_of_positions(current_bookmark_page):
                            current_bookmark_pos = 0
                            if current_bookmark_page < bookmark_pages.get_number_of_pages() - 1:
                                current_bookmark_page += 1
                            else:
                                current_bookmark_page = 0

                if y in Key.PAGE_DOWN:
                    if bookmarks.has_bookmarks():
                        current_bookmark_pos -= 1
                        if current_bookmark_pos == -1:
                            if current_bookmark_page > 0:
                                current_bookmark_page -= 1
                            else:
                                current_bookmark_page = bookmark_pages.get_number_of_pages() - 1
                            current_bookmark_pos = \
                                bookmark_pages.get_number_of_positions(current_bookmark_page) - 1

                if y in Key.SELECT:
                    if bookmarks.has_bookmarks():
                        bookmark_key = \
                            bookmark_pages.get_position_id(current_bookmark_page, current_bookmark_pos)
                        current_chapter = bookmarks.get_chapter(bookmark_key)
                        content_pages = Screen.ContentPages(
                            screen,
                            book,
                            current_chapter,
                            modes,
                            v_padding,
                            h_padding,
                            pe_line
                        )
                        current_page = content_pages.get_page_by_index(bookmarks.get_index(bookmark_key))
                    escape_bookmark = True
                    content_update = True

                if y in Key.BOOKMARK_REMOVE:
                    if bookmarks.has_bookmarks():
                        bookmark_key = \
                            bookmark_pages.get_position_id(current_bookmark_page, current_bookmark_pos)
                        bookmarks.remove(bookmark_key)
                        bookmark_pages = Screen.BookmarkPages(
                            screen,
                            book,
                            current_chapter,
                            bookmarks,
                            modes,
                            v_padding,
                            h_padding
                        )
                        if bookmarks.has_bookmarks():
                            if current_bookmark_page > bookmark_pages.get_number_of_pages() - 1:
                                current_bookmark_page = bookmark_pages.get_number_of_pages() - 1
                            if current_bookmark_pos > bookmark_pages.get_number_of_positions(current_bookmark_page) - 1:
                                current_bookmark_pos = bookmark_pages.get_number_of_positions(current_bookmark_page) - 1

                if y in Key.BOOKMARK_EDIT:
                    if bookmarks.has_bookmarks():
                        bookmark_key = \
                            bookmark_pages.get_position_id(current_bookmark_page, current_bookmark_pos)
                        bookmarks.edit(bookmark_key)
                        bookmark_pages = Screen.BookmarkPages(
                            screen,
                            book,
                            current_chapter,
                            bookmarks,
                            modes,
                            v_padding,
                            h_padding
                        )
                        curses.endwin()
                        std_screen = Screen.Screen(
                            book_title,
                            modes,
                            is_dict_installed,
                            book_language
                        )
                        screen = std_screen.get_screen()
                        std_screen.redraw()
                        index = content_pages.get_current_page_index(current_page)
                        content_pages = Screen.ContentPages(
                            screen,
                            book,
                            current_chapter,
                            modes,
                            v_padding,
                            h_padding,
                            pe_line
                        )
                        current_page = content_pages.get_page_by_index(index)
                        current_description_page = 0
                        content_pages.print_page(current_page, bookmarks, quickmarks)

                if y in Key.BOOKMARK_DESCRIBE:
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
                            modes,
                            v_padding,
                            h_padding
                        )

                        while escape_description == False:
                            bookmark_description_pages.print_page(current_description_page)

                            z = screen.getch()

                            if z in Key.PAGE_UP:
                                current_description_page += 1
                                if current_description_page == bookmark_description_pages.get_number_of_pages():
                                    current_description_page = 0

                            if z in Key.PAGE_DOWN:
                                current_description_page -= 1
                                if current_description_page < 0:
                                    current_description_page =  \
                                        bookmark_description_pages.get_number_of_pages() - 1

                            if z in Key.BOOKMARK_DESCRIBE or z in Key.ESCAPE:
                                content_update = True
                                escape_description = True

                            if z in Key.REFRESH:
                                screen_update = True
                                content_update = True
                                escape_description = True

                            if z in Key.QUIT:
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
                                    modes,
                                    is_dict_installed,
                                    book_language
                                )
                                screen = std_screen.get_screen()
                                std_screen.redraw()
                                index = content_pages.get_current_page_index(current_page)
                                content_pages = Screen.ContentPages(
                                    screen,
                                    book,
                                    current_chapter,
                                    modes,
                                    v_padding,
                                    h_padding,
                                    pe_line
                                )
                                bookmark_description_pages = Screen.BookmarkDescribePages(
                                    screen,
                                    book,
                                    current_chapter,
                                    bookmarks,
                                    bookmark_key,
                                    modes,
                                    v_padding,
                                    h_padding
                                )
                                bookmark_pages = Screen.BookmarkPages(
                                    screen,
                                    book,
                                    current_chapter,
                                    bookmarks,
                                    modes,
                                    v_padding,
                                    h_padding
                                )
                                content_pages.print_page(current_page, bookmarks, quickmarks)
                                current_page = content_pages.get_page_by_index(index)
                                current_description_page = 0

                if y in Key.BOOKMARK or y in Key.ESCAPE:
                    content_update = True
                    escape_bookmark = True

                if y in Key.REFRESH:
                    screen_update = True
                    content_update = True
                    escape_bookmark = True

                if y in Key.QUIT:
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
                        modes,
                        is_dict_installed,
                        book_language
                    )
                    screen = std_screen.get_screen()
                    std_screen.redraw()
                    index = content_pages.get_current_page_index(current_page)
                    content_pages = Screen.ContentPages(
                        screen,
                        book,
                        current_chapter,
                        modes,
                        v_padding,
                        h_padding,
                        pe_line
                    )
                    bookmark_pages = Screen.BookmarkPages(
                        screen,
                        book,
                        current_chapter,
                        bookmarks,
                        modes,
                        v_padding,
                        h_padding
                    )
                    content_pages.print_page(current_page, bookmarks, quickmarks)
                    current_page = content_pages.get_page_by_index(index)
                    current_bookmark_page = 0

        if x in Key.TOC:
            escape_toc = False
            current_toc_page = 0
            current_toc_pos = 0
            while escape_toc == False:
                toc_pages.print_page(current_toc_page, current_toc_pos)

                y = screen.getch()

                if y in Key.PAGE_UP:
                    current_toc_pos += 1
                    if current_toc_pos == \
                        toc_pages.get_number_of_positions(current_toc_page):
                        current_toc_pos = 0
                        if current_toc_page < toc_pages.get_number_of_pages() - 1:
                            current_toc_page += 1
                        else:
                            current_toc_page = 0

                if y in Key.PAGE_DOWN:
                    current_toc_pos -= 1
                    if current_toc_pos == -1:
                        if current_toc_page > 0:
                            current_toc_page -= 1
                        else:
                            current_toc_page = toc_pages.get_number_of_pages() - 1
                        current_toc_pos = \
                            toc_pages.get_number_of_positions(current_toc_page) - 1

                if y in Key.SELECT:
                    current_page = 0
                    current_chapter = \
                        toc_pages.get_position_id(current_toc_page, current_toc_pos) - 1
                    escape_toc = True
                    content_update = True

                if y in Key.TOC or y in Key.ESCAPE:
                    content_update = True
                    escape_toc = True

                if y in Key.REFRESH:
                    screen_update = True
                    content_update = True
                    escape_toc = True

                if y in Key.QUIT:
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
                        modes,
                        is_dict_installed,
                        book_language
                    )
                    screen = std_screen.get_screen()
                    std_screen.redraw()
                    index = content_pages.get_current_page_index(current_page)
                    content_pages = Screen.ContentPages(
                        screen,
                        book,
                        current_chapter,
                        modes,
                        v_padding,
                        h_padding,
                        pe_line
                    )
                    toc_pages = Screen.TocPages(
                        screen,
                        book,
                        current_chapter,
                        modes,
                        v_padding,
                        h_padding
                    )
                    content_pages.print_page(current_page, bookmarks, quickmarks)
                    current_page = content_pages.get_page_by_index(index)
                    current_toc_page = 0

        if x in Key.HELP:
            escape_help = False
            current_help_page = 0
            while escape_help == False:
                help_pages.print_page(current_help_page)

                y = screen.getch()

                if y in Key.PAGE_UP:
                    current_help_page += 1
                    if current_help_page == help_pages.get_number_of_pages():
                        current_help_page = 0

                if y in Key.PAGE_DOWN:
                    current_help_page -= 1
                    if current_help_page < 0:
                        current_help_page = help_pages.get_number_of_pages() - 1

                if y in Key.HELP or y in Key.ESCAPE:
                    content_update = True
                    escape_help = True

                if y in Key.REFRESH:
                    screen_update = True
                    content_update = True
                    escape_help = True

                if y in Key.QUIT:
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
                        modes,
                        is_dict_installed,
                        book_language
                    )
                    screen = std_screen.get_screen()
                    std_screen.redraw()
                    index = content_pages.get_current_page_index(current_page)
                    content_pages = Screen.ContentPages(
                        screen,
                        book,
                        current_chapter,
                        modes,
                        v_padding,
                        h_padding,
                        pe_line
                    )
                    help_pages = Screen.HelpPages(
                        screen,
                        book,
                        current_chapter,
                        modes,
                        v_padding,
                        h_padding
                    )
                    content_pages.print_page(current_page, bookmarks, quickmarks)
                    current_page = content_pages.get_page_by_index(index)
                    current_help_page = 0

        if x in Key.REFRESH:
            curses.endwin()
            std_screen = Screen.Screen(
                book_title,
                modes,
                is_dict_installed,
                book_language
            )
            screen = std_screen.get_screen()
            screen_update = True
            content_update = True

        if x in Key.QUIT:
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
                modes,
                is_dict_installed,
                book_language
            )
            screen = std_screen.get_screen()
            index = content_pages.get_current_page_index(current_page)
            screen_update = True
            content_update = True
