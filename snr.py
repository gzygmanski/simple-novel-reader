#!/bin/python3
import os, sys, curses
from textwrap import wrap
from reader import FileReader
from parser import TocContent

def get_page(screen, maxY, maxX):
    nlines = maxY - 3
    ncols = maxX - 40
    begin_y = 2
    begin_x = 20
    page = screen.subwin(nlines, ncols, begin_y, begin_x)
    page.box()
    return page

def get_pages(book, page, chapter, posY=2, posX=2):
    pages = []
    on_page = []
    maxY, maxX = page.getmaxyx()
    max_lines = maxY - (posY * 2)
    max_cols = maxX - (posX * 2)

    if book.has_text(chapter):
        content = book.get_chapter_text(chapter)

        for paragraph in content:
            lines_of_text = wrap(paragraph, max_cols)
            if len(lines_of_text) + len(on_page) + 1 <= max_lines:
                for text in lines_of_text:
                    on_page.append(text)
                on_page.append('')
            else:
                pages.append(on_page)
                on_page = []
        if len(on_page) != 0:
            pages.append(on_page)
        return pages
    else:
        content = book.get_chapter_title(chapter)

        for line_of_text in wrap(content, max_cols):
            on_page.append(line_of_text)

        pages.append(on_page)
        return pages

def print_page_content(page, pages, page_number, posY=2, posX=2):
    try:
        if pages[page_number]:
            for line_of_text in pages[page_number]:
                page.addstr(posY, posX, line_of_text, curses.A_NORMAL)
                posY += 1
    except:
        pass

def print_page_number(page, pages, current):
    maxY, maxX = page.getmaxyx()
    max_pages = len(pages)
    current += 1
    page_num = str(current) + '/' + str(max_pages)
    posY = maxY - 1
    posX = maxX - len(page_num) - 2
    page.addstr(posY, posX, page_num, curses.A_REVERSE)

def print_page_title(book, page, chapter, posX = 2):
    maxY, maxX = page.getmaxyx()
    max_cols = maxX - (posX * 2)
    chapter_title = book.get_chapter_title(chapter)
    chapter_id = book.get_id(chapter)

    page_title = str(chapter_id) + ': ' + chapter_title

    if len(page_title) >= max_cols - 3:
        page_title = page_title[:max_cols - 3] + '...'

    page.addstr(0, 2, page_title, curses.A_REVERSE)


def main(argv):
    escape = False
    # try:
    fileinput = argv[1]
    reader = FileReader(fileinput)
    toc_file = reader.get_toc_file()
    path = reader.get_directory_path(toc_file)
    book = TocContent(path, toc_file)
    # except:
        # print('Something went wrong.')
    # exit()

    VERSION = '0.1-dev'
    APPLICATION = 'Simple Novel Reader'
    screen = curses.initscr()
    # curses.start_color()
    # curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    # highlightText = curses.color_pair(1)
    # normalText = curses.A_NORMAL

    curses.noecho()
    curses.cbreak()
    curses.nonl()
    curses.curs_set(0)
    screen.keypad(1)
    screen.addstr(0, 1, APPLICATION + ' ' + VERSION, curses.A_UNDERLINE)

    init_chapter = True
    current_page = 0
    current_chapter = 0
    number_of_chapters = book.get_number_of_chapters()

    screen.addstr(1, 1, str(number_of_chapters), curses.A_UNDERLINE)

    while escape == False:
        if current_chapter == number_of_chapters:
            curses.endwin()
            break

        maxY, maxX = screen.getmaxyx()
        page = get_page(screen, maxY, maxX)

        if init_chapter:
            pages = get_pages(book, page, current_chapter)
            init_chapter = False

        print_page_title(book, page, current_chapter)
        print_page_number(page, pages, current_page)
        print_page_content(page, pages, current_page)

        x = screen.getch()

        if x == ord('n'):
            if current_page == len(pages) - 1:
                current_chapter += 1
                current_page = 0
                init_chapter = True
            else:
                current_page += 1
            page.erase()
            page.refresh()

        if x == ord('p'):
            if current_page == 0 and current_chapter != 0:
                current_chapter -= 1
                current_page = len(get_pages(book, page, current_chapter)) - 1
                init_chapter = True
            elif current_page == 0 and current_chapter == 0:
                current_page = 0
            else:
                current_page -= 1
            page.erase()
            page.refresh()

        if x == ord('N'):
            if current_chapter != number_of_chapters:
                current_chapter += 1
                current_page = 0
                init_chapter = True
                page.erase()
                page.refresh()

        if x == ord('P'):
            if current_chapter != 0:
                current_chapter -= 1
                current_page = 0
                init_chapter = True
                page.erase()
                page.refresh()

        if x == ord('q'):
            escape = True
            curses.endwin()
        elif x == curses.KEY_RESIZE:
            screen.erase()

if __name__ == '__main__':
    main(sys.argv)
