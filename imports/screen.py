#!/bin/python3

import curses
from textwrap import wrap

class Screen:
    def __init__(self, version='2020', app_name='[snr] Simple Novel Reader'):
        self.version = version
        self.app_name = app_name
        self._set_screen()

    def _set_screen(self):
        self.screen = curses.initscr()
        self.screen.keypad(1)

    def get_screen(self):
        return self.screen

    def redraw(self):
        self.screen.erase()
        # self.screen.box()
        self.screen.addstr(0, 2, self.app_name + ' ' + self.version, curses.A_UNDERLINE)
        self.screen.refresh()


class Pager:
    def __init__(self, screen, book, chapter, dark_mode=False, v_padding=2, h_padding=2):
        self.screen = screen
        self.book = book
        self.chapter = chapter
        self.dark_mode = dark_mode
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
        self._set_colors()
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

    def _set_colors(self):
        curses.start_color()
        if self.dark_mode:
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        else:
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
        self.background_colors = curses.color_pair(1)
        self.info_colors = curses.color_pair(2)

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
        page_number = '[' + str(current_page) + '/' + str(self.get_number_of_pages()) + ']'
        pos_y = self.page_max_y - 1
        pos_x = self.page_max_x - len(page_number) - self.h_padding
        self.page.addstr(pos_y, pos_x, page_number, self.info_colors)

    def print_page_title(self):
        chapter_title = self.book.get_chapter_title(self.chapter)
        chapter_id = self.book.get_id(self.chapter)
        page_title = '[' +  str(chapter_id) + '][' + chapter_title + ']'
        if len(page_title) >= self.page_columns - 4:
            page_title = page_title[:self.page_columns - 4] + '...]'
        self.page.addstr(0, self.h_padding, page_title, self.info_colors)

    def print_page(self, current_page):
        self.page.erase()
        self.page.bkgd(' ', self.background_colors)
        self.page.box()
        self.print_page_title()
        self.print_page_text(current_page)
        self.print_page_number(current_page)
        self.page.refresh()

