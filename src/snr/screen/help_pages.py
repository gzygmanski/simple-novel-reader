#!/usr/bin/env python3

import curses
from textwrap import wrap
from .pages import Pages

class HelpPages(Pages):
    def __init__(
        self,
        screen,
        book,
        chapter,
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
        navigation = {
            'READER NAVIGATION': {
                'BASIC MOVEMENT': '',
                'Page/Move up': 'j, n, Space',
                'Page/Move down': 'k, p',
                'Next chapter': 'l, N',
                'Previous chapter': 'h, P',
                'Beginning of chapter': 'g, 0',
                'End of chapter': 'G, $',
                'Select': 'o, Enter',
                'Escape': 'Esc, BackSpace',
                'Refresh': 'R, F5',
                'Quit': 'q',
                'MODES': '',
                'Dark mode': 'r',
                'Speed reading mode': 's',
                'Highlight speech': 'v',
                'Double page': 'd',
                'Justify text': 'f',
                'Hyphenation': 'e',
                'PAGE SPACING': '',
                'Increase vertical padding': '>',
                'Decrease vertical padding': '<',
                'Increase horizontal padding': '.',
                'Decrease horizontal padding': ',',
                'PE - Perception Expander': '',
                'Increase PE line positon': ']',
                'Decrease PE line positon': '[',
                'OPEN MODULES': '',
                'Table of contents': 't, Tab',
                'Bookmark page': 'b',
                'Help page': '?, F1'
            },
            'MARKING': {
                'QUICKMARKS': '',
                'Save quickmark': 'm, then [1-9]',
                'Open quickmark': '[1-9]',
                'Clear quickmark': 'c, then [1-9] or a',
                'BOOKMARKS': '',
                'Create bookmark': 'B, M',
                'Remove bookmark': 'x',
                'Open description': 'd, l',
                'Edit description': 'e',
            }
        }
        self.pages = []
        self.help_sections = []
        page = []
        for section in navigation.keys():
            self.help_sections.append(section)
            for command in navigation[section].keys():
                if navigation[section][command] != '':
                    key_binds = '{' + navigation[section][command] + '}'
                else:
                    key_binds = navigation[section][command]
                space = self.page_max_x - self.static_padding * 2 \
                    - len(command) - 2 - len(key_binds)
                if space > 0:
                    key_binds = ' ' * space + key_binds
                command_text = wrap(command + ': ' + key_binds,
                    self.page_max_x - self.static_padding * 2)
                while len(command_text) > 0:
                    if len(command_text) + len(page) + 1 <= self.page_max_y - self.static_padding * 2:
                        for text in command_text:
                            page.append(text)
                        command_text = []
                    else:
                        for _ in range(len(page), self.page_max_y - self.static_padding * 2):
                            page.append(command_text[0])
                            command_text.pop(0)
                        self.help_sections.append(section)
                        self.pages.append(page)
                        page = []
            if len(page) != 0:
                self.pages.append(page)
                page = []

    # :::: GETTERS ::::::::::::::::: #

    def get_number_of_pages(self):
        return len(self.pages)

    # :::: PRINTERS :::::::::::::::: #

    def _print_header(self, current_page):
        help_title = '[HELP][' + self.help_sections[current_page] + ']'
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
        try:
            self._print_header(current_page)
            self._print_content(current_page)
            self._print_footer(current_page)
        except:
            pass
        self.page.refresh()
