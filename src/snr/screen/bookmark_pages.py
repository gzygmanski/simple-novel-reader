#!/bin/python3

import curses
from textwrap import wrap
from .pages import Pages

class BookmarkPages(Pages):
    def __init__(
        self,
        screen,
        book,
        chapter,
        bookmarks,
        dark_mode=False,
        speed_mode=False,
        highlight=False,
        double_page=False,
        justify_full=False,
        v_padding=2,
        h_padding=2,
    ):
        super().__init__(
            screen,
            book,
            chapter,
            dark_mode,
            speed_mode,
            highlight,
            double_page,
            justify_full,
            v_padding,
            h_padding,
        )
        self.bookmarks = bookmarks
        self._set_page()
        self._set_pages()

    # :::: SETTERS ::::::::::::::::: #

    def _set_page(self):
        if not self.double_page:
            self.page = self.screen.subwin(
                self.page_max_y,
                self.page_max_x,
                self.page_pos_y,
                self.page_pos_x
            )
        else:
            self.page = self.screen.subwin(
                self.page_max_y,
                self.page_max_x,
                self.page_pos_y,
                self.page_pos_x_right
            )

    def _set_pages(self):
        bookmarks = self.bookmarks.get_bookmarks()
        self.pages = []
        page = []
        lines = 0
        for key in bookmarks.keys():
            bookmark = wrap(
                bookmarks[key]['name'],
                self.page_max_x - self.id_margin - self.static_padding
            )
            if lines + len(bookmark) <= self.page_lines:
                page.append({
                    'id': key,
                    'name': bookmark
                })
                lines += len(bookmark)
            else:
                self.pages.append(page)
                page = []
                lines = 0
        if len(page) != 0:
            self.pages.append(page)

    # :::: GETTERS ::::::::::::::::: #

    def get_number_of_pages(self):
        return len(self.pages)

    def get_number_of_positions(self, current_page):
        return len(self.pages[current_page])

    def get_position_id(self, current_page, current_pos):
        return self.pages[current_page][current_pos]['id']

    # :::: PRINTERS :::::::::::::::: #

    def _print_header(self):
        toc_title = '[Bookmarks]'
        self.page.addstr(
            0,
            self.static_padding,
            self.shorten_title(toc_title),
            self.info_colors
        )

    def _print_content(self, current_page, pointer_pos):
        pos_y = self.static_padding
        for y, bookmark in enumerate(self.pages[current_page]):
            if pointer_pos == y:
                self.page.addstr(
                    pos_y,
                    self.static_padding,
                    self.pointer,
                    self.select_colors
                )
                bookmark_index = ' ' * abs((len(str(bookmark['id'])) - 3) * -1) \
                    + str(bookmark['id']) + self.index_suffix
                self.page.addstr(
                    pos_y,
                    self.static_padding + self.pointer_margin,
                    bookmark_index,
                    self.select_colors
                )
                for line in bookmark['name']:
                    self.page.addstr(
                        pos_y,
                        self.id_margin,
                        line,
                        self.select_colors
                    )
                    pos_y += 1
            else:
                bookmark_index = ' ' * abs((len(str(bookmark['id'])) - 3) * -1) \
                    + str(bookmark['id']) + ':'
                self.page.addstr(
                    pos_y,
                    self.static_padding + self.pointer_margin,
                    bookmark_index,
                    self.info_colors
                )
                for line in bookmark['name']:
                    self.page.addstr(
                        pos_y,
                        self.id_margin,
                        line,
                        self.normal_colors
                    )
                    pos_y += 1

    def _print_footer(self, current_page):
        current_page += 1
        page_number = '[' + str(current_page) + '/' + str(self.get_number_of_pages()) + ']'
        pos_y = self.page_max_y - 1
        pos_x = self.page_max_x - len(page_number) - self.static_padding
        self.page.addstr(pos_y, pos_x, page_number, self.info_colors)

    def print_page(self, current_page, pointer_pos):
        self.page.erase()
        self.page.bkgd(' ', self.info_colors)
        self.page.box()
        try:
            self._print_header()
            self._print_content(current_page, pointer_pos)
            self._print_footer(current_page)
        except:
            pass
        self.page.refresh()
