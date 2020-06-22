#!/usr/bin/env python3

import curses
from textwrap import wrap

class Pages:
    def __init__(
        self,
        screen,
        book,
        chapter,
        modes,
        v_padding=2,
        h_padding=2,
    ):
        self.screen = screen
        self.book = book
        self.chapter = chapter
        self.dark_mode = modes['dark_mode']
        self.speed_mode = modes['speed_mode']
        self.highlight = modes['highlight']
        self.double_page = modes['double_page']
        self.justify_full = modes['justify_full']
        self.hyphenation = modes['hyphenation']
        self.screen_max_y, self.screen_max_x = screen.getmaxyx()
        self._set_page_max_y()
        self._set_page_max_x()
        self.static_padding = 3
        self._set_v_padding_max()
        self._set_v_padding_min()
        self._set_h_padding_max()
        self._set_h_padding_min()
        self.v_padding = self._set_padding(v_padding, self.v_padding_max, self.v_padding_min)
        self.h_padding = self._set_padding(h_padding, self.h_padding_max, self.h_padding_min)
        self._set_double_page()
        self._set_page_pos_y()
        self._set_page_pos_x()
        self._set_page_lines()
        self._set_page_columns()
        self._set_page_pos_x_left()
        self._set_page_pos_x_right()
        self._set_selector()
        self._set_colors()

    # :::: SETTERS ::::::::::::::::: #

    def _set_page_max_y(self):
        self.page_max_y = self.screen_max_y - 4

    def _set_page_max_x(self):
        max_x = int(self.page_max_y * 1.6)
        if max_x > self.screen_max_x:
            self.page_max_x = self.screen_max_x - 2
        else:
            self.page_max_x = max_x

    def _set_v_padding_max(self):
        self.v_padding_max = int(self.page_max_x * .1)

    def _set_v_padding_min(self):
        self.v_padding_min = self.static_padding

    def _set_h_padding_max(self):
        self.h_padding_max = int(self.page_max_x * .1) * 2

    def _set_h_padding_min(self):
        self.h_padding_min = self.static_padding

    def _set_padding(self, padding, padding_max, padding_min):
        if padding > padding_max:
            return padding_max
        elif padding < padding_min:
            return padding_min
        else:
            return padding

    def _set_double_page(self):
        if self.double_page and self.page_max_x * 2 + 1 > self.screen_max_x - 2:
            self.double_page = False

    def _set_page_pos_y(self):
        self.page_pos_y = 2

    def _set_page_pos_x(self):
        if not self.double_page:
            self.page_pos_x = int(self.screen_max_x / 2 - self.page_max_x / 2)
        else:
            self.page_pos_x = int(self.screen_max_x / 2)

    def _set_page_lines(self):
        self.page_lines = self.page_max_y - (self.v_padding * 2)

    def _set_page_columns(self):
        self.page_columns = self.page_max_x - (self.h_padding * 2)

    def _set_page_pos_x_left(self):
        if self.double_page:
            self.page_pos_x_left = self.page_pos_x - self.page_max_x

    def _set_page_pos_x_right(self):
        if self.double_page:
            self.page_pos_x_right = self.page_pos_x

    def _set_selector(self):
        self.pointer = '->'
        self.index_suffix = ': '
        max_index = 3
        self.pointer_margin = len(self.pointer)
        self.id_margin = self.pointer_margin + self.static_padding + max_index \
            + len(self.index_suffix)

    def _set_colors(self):
        curses.start_color()
        if self.dark_mode:
            self.normal_colors = curses.color_pair(6)
            self.info_colors = curses.color_pair(7)
            self.speech_colors = curses.color_pair(8)
            self.select_colors = curses.color_pair(9)
            self.perception_colors = curses.color_pair(10)
        else:
            self.normal_colors = curses.color_pair(1)
            self.info_colors = curses.color_pair(2)
            self.speech_colors = curses.color_pair(3)
            self.select_colors = curses.color_pair(4)
            self.perception_colors = curses.color_pair(5)

    # :::: GETTERS ::::::::::::::::: #

    def get_double_page(self):
        return self.double_page

    # :::: OTHER ::::::::::::::::::: #

    def shorten_title(self, title):
        if len(title) >= self.page_max_x - self.static_padding * 2:
            return title[:self.page_max_x - self.static_padding * 2 - 4] + '...]'
        else:
            return title

    def justify_line(self, line):
        just_line = []
        words = line.split(" ")
        words_len = sum(len(word) for word in words)
        if words_len < int(self.page_columns / 1.6):
            return line
        spaces_number = len(words) - 1
        spaces = [1 for _ in range(spaces_number)]
        index = 0
        if spaces:
            while words_len + spaces_number < self.page_columns:
                spaces[len(spaces) - index - 1] += 1
                spaces_number += 1
                index = (index + 1) % len(spaces)
        for index, word in enumerate(words):
            just_line.append(word)
            if index < len(spaces):
                just_line.append(' ' * spaces[index])
        return ''.join(just_line)
