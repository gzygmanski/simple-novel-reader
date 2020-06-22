#!/bin/python3

import curses
from textwrap import wrap
from .pages import Pages

class BookmarkDescribePages(Pages):
    def __init__(
        self,
        screen,
        book,
        chapter,
        bookmarks,
        bookmark,
        modes,
        v_padding=2,
        h_padding=2,
    ):
        super().__init__(
            screen,
            book,
            chapter,
            modes,
            v_padding,
            h_padding,
        )
        self.bookmarks = bookmarks
        self.bookmark = bookmark
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
        on_page = []
        on_page.append('Chapter: ' + str(bookmarks[self.bookmark]['chapter'] + 1))
        on_page.append('Index: ' + str(bookmarks[self.bookmark]['index']))
        on_page.append('* * *')
        if self.bookmarks.has_description(self.bookmark):
            content = bookmarks[self.bookmark]['description']
            for paragraph in content:
                lines_of_text = wrap(paragraph, self.page_max_x - self.static_padding * 2)
                while len(lines_of_text) > 0:
                    if len(lines_of_text) + len(on_page) + 1 <= self.page_lines:
                        for text in lines_of_text:
                            on_page.append(text)
                        if len(on_page) != 0:
                            on_page.append('')
                        lines_of_text = []
                    else:
                        for _ in range(len(on_page), self.page_lines):
                            on_page.append(lines_of_text[0])
                            lines_of_text.pop(0)
                        self.pages.append(on_page)
                        on_page = []
            if len(on_page) != 0:
                self.pages.append(on_page)
        else:
            content = bookmarks[self.bookmark]['name']
            for line_of_text in wrap(content, self.page_max_x - self.static_padding * 2):
                on_page.append(line_of_text)
            self.pages.append(on_page)

    # :::: GETTERS ::::::::::::::::: #

    def get_number_of_pages(self):
        return len(self.pages)

    # :::: PRINTERS :::::::::::::::: #

    def _print_header(self, current_page):
        help_title = '[Bookmarks][' + \
            self.bookmarks.get_bookmarks()[self.bookmark]['name'] + ']'
        self.page.addstr(
            0,
            self.static_padding,
            self.shorten_title(help_title),
            self.info_colors
        )

    def _print_content(self, current_page):
        for y, line_of_text in enumerate(self.pages[current_page]):
            self.page.addstr(
                y + self.static_padding,
                self.static_padding,
                line_of_text,
                self.normal_colors
            )

    def _print_footer(self, current_page):
        current_page += 1
        page_number = '[' + str(current_page) + '/' + str(self.get_number_of_pages()) + ']'
        pos_y = self.page_max_y - 1
        pos_x = self.page_max_x - len(page_number) - self.static_padding
        self.page.addstr(pos_y, pos_x, page_number, self.info_colors)

    def print_page(self, current_page):
        self.page.erase()
        self.page.bkgd(' ', self.info_colors)
        self.page.box()
        self._print_header(current_page)
        try:
            self._print_content(current_page)
            self._print_footer(current_page)
        except:
            pass
        self.page.refresh()
