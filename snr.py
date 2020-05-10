#!/bin/python3
import os, sys, curses
from textwrap import wrap
from reader import FileReader
from parser import TocContent

class Pager:
    def __init__(self, screen, book, chapter, v_padding=2, h_padding=2):
        self.screen = screen
        self.book = book
        self.chapter = chapter
        self.v_padding = v_padding
        self.h_padding = h_padding
        self.screen_max_y, self.screen_max_x = screen.getmaxyx()
        self._set_page_max_y()
        self._set_page_max_x()
        self._set_page_pos_y()
        self._set_page_pos_x()
        self._set_page_lines()
        self._set_page_columns()
        self._set_page()
        self._set_pages()

    def _set_page_max_y(self):
        self.page_max_y = self.screen_max_y - 4

    def _set_page_max_x(self):
        self.page_max_x = int(self.screen_max_x / 2)

    def _set_page_pos_y(self):
        self.page_pos_y = 2

    def _set_page_pos_x(self):
        self.page_pos_x = int(self.page_max_x / 2)

    def _set_page_lines(self):
        self.page_lines = self.page_max_y - (self.v_padding * 2)

    def _set_page_columns(self):
        self.page_columns = self.page_max_x - (self.h_padding * 2)

    def _set_page(self):
        self.page = self.screen.subwin(self.page_max_y, self.page_max_x,
            self.page_pos_y, self.page_pos_x)

    def _set_pages(self):
        pages = []
        on_page = []
        if self.book.has_text(self.chapter):
            content = self.book.get_chapter_text(self.chapter)
            for paragraph in content:
                lines_of_text = wrap(paragraph, self.page_columns)
                if len(lines_of_text) + len(on_page) + 1 <= self.page_lines:
                    for text in lines_of_text:
                        on_page.append(text)
                    on_page.append('')
                else:
                    pages.append(on_page)
                    on_page = []
                    for text in lines_of_text:
                        on_page.append(text)
                    on_page.append('')
            if len(on_page) != 0:
                pages.append(on_page)
            self.pages = pages
        else:
            content = self.book.get_chapter_title(self.chapter)
            for line_of_text in wrap(content, self.page_columns):
                on_page.append(line_of_text)
            pages.append(on_page)
            self.pages = pages

    def get_number_of_pages(self):
        return len(self.pages)

    def print_page_text(self, current_page):
        pos_y = self.v_padding
        try:
            if self.pages[current_page]:
                for line_of_text in self.pages[current_page]:
                    self.page.addstr(pos_y, self.h_padding,
                        line_of_text, curses.A_NORMAL)
                    pos_y += 1
        except:
            pass

    def print_page_number(self, current_page):
        current_page += 1
        page_number = str(current_page) + '/' + str(self.get_number_of_pages())
        pos_y = self.page_max_y - 1
        pos_x = self.page_max_x - len(page_number) - self.h_padding
        self.page.addstr(pos_y, pos_x, page_number, curses.A_REVERSE)

    def print_page_title(self):
        chapter_title = self.book.get_chapter_title(self.chapter)
        chapter_id = self.book.get_id(self.chapter)
        page_title = str(chapter_id) + ' - ' + chapter_title
        if len(page_title) >= self.page_columns - 3:
            page_title = page_title[:self.page_columns - 3] + '...'
        self.page.addstr(0, self.h_padding, page_title, curses.A_REVERSE)

    def print_page(self, current_page):
        self.page.erase()
        self.page.box()
        self.print_page_title()
        self.print_page_text(current_page)
        self.print_page_number(current_page)
        self.page.refresh()

def main(argv):
    escape = False
    fileinput = argv[1]
    reader = FileReader(fileinput)
    toc_file = reader.get_toc_file()
    path = reader.get_directory_path(toc_file)
    book = TocContent(path, toc_file)

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

        if init_chapter:
            page = Pager(screen, book, current_chapter)
            init_chapter = False

        page.print_page(current_page)

        x = screen.getch()

        if x == ord('n'):
            if current_page == page.get_number_of_pages() - 1:
                current_chapter += 1
                current_page = 0
                init_chapter = True
            else:
                current_page += 1

        if x == ord('p'):
            if current_page == 0 and current_chapter != 0:
                current_chapter -= 1
                page = Pager(screen, book, current_chapter)
                current_page = page.get_number_of_pages() - 1
            elif current_page == 0 and current_chapter == 0:
                current_page = 0
            else:
                current_page -= 1

        if x == ord('N'):
            if current_chapter != number_of_chapters:
                current_chapter += 1
                current_page = 0
                init_chapter = True

        if x == ord('P'):
            if current_chapter != 0:
                current_chapter -= 1
                current_page = 0
                init_chapter = True

        if x == ord('q'):
            escape = True
            curses.endwin()
        elif x == curses.KEY_RESIZE:
            screen.erase()

if __name__ == '__main__':
    main(sys.argv)
