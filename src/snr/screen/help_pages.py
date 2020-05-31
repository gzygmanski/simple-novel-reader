#!/bin/python3

import curses
from textwrap import wrap
from .pages import Pages

class HelpPages(Pages):
    def __init__(
        self,
        screen,
        book,
        chapter,
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
        self._set_page()
        self._set_help()

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

    def _set_help(self):
        navigation = {
            'READER NAVIGATION': {
                'PAGE UP': 'j, n, Space',
                'PAGE DOWN': 'k, p',
                'NEXT CHAPTER': 'l, N',
                'PREVIOUS CHAPTER': 'h, P',
                'BEGGINING OF CHAPTER': 'g, 0',
                'END OF CHAPTER': 'G, $',
                'DARK MODE': 'r',
                'SPEED READING MODE': 's',
                'HIGHLIGHT': 'v',
                'DOUBLE PAGE': 'd',
                'JUSTIFY TEXT': 'f',
                'INCREASE VERTICAL PADDING': '>',
                'DECREASE VERTICAL PADDING': '<',
                'INCREASE HORIZONTAL PADDING': '.',
                'DECREASE HORIZONTAL PADDING': ',',
                'INCREASE PE LINE POSITON': ']',
                'DECREASE PE LINE POSITON': '[',
                'TABLE OF CONTENTS': 't, Tab',
                'HELP PAGE': '?, F1',
                'ESCAPE': 'Esc, BackSpace',
                'REFRESH': 'R, F5',
                'QUIT': 'q'
            },
            'TABLE OF CONTENTS NAVIGATION': {
                'MOVE UP': 'j, n, Space',
                'MOVE DOWN': 'k, p',
                'SELECT': 'o, Enter',
                'ESCAPE': 't, Tab, Esc'
            },
            'QUICKMARKS NAVIGATION': {
                'SAVE QUICKMARK': 'm, then [1-9]',
                'OPEN QUICKMARK': '[1-9]',
                'CLEAR QUICKMARK': 'c, then [1-9] or a'
            }
        }
        self.pages = []
        self.help_sections = []
        page = []
        lines = 0
        for section in navigation.keys():
            self.help_sections.append(section)
            for command in navigation[section].keys():
                command_text = wrap(command + ': ' + navigation[section][command],
                    self.page_max_x - self.static_padding * 2)
                lines += len(command_text)
                if lines <= self.page_lines:
                    for line_of_text in command_text:
                        page.append(line_of_text)
                else:
                    self.help_sections.append(section)
                    self.pages.append(page)
                    page = []
                    lines = 0
            if len(page) != 0:
                self.pages.append(page)
                page = []
                lines = 0

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
