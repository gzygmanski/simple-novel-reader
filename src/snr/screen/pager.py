#!/bin/python3

import curses
from textwrap import wrap

class Pager:
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
        pe_multiplier=.2
    ):
        self.screen = screen
        self.book = book
        self.chapter = chapter
        self.dark_mode = dark_mode
        self.speed_mode = speed_mode
        self.highlight = highlight
        self.double_page = double_page
        self.justify_full = justify_full
        self.screen_max_y, self.screen_max_x = screen.getmaxyx()
        self._set_page_max_y()
        self._set_page_max_x()
        self.static_padding = 2
        self.pe_multiplier = pe_multiplier
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
        self._set_page()
        self._set_toc_page()
        self._set_help_page()
        self._set_selector()
        self._set_colors()
        self._set_toc()
        self._set_help()
        self._set_pages()
        self._set_speech_map()
        self._set_info_map()

    # :::::::::::::::::::::::::::::: #
    # :::: SETTERS ::::::::::::::::: #
    # :::::::::::::::::::::::::::::: #

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

    def _set_page(self):
        if not self.double_page:
            self.page = self.screen.subwin(
                self.page_max_y,
                self.page_max_x,
                self.page_pos_y,
                self.page_pos_x
            )
        else:
            self.page_left = self.screen.subwin(
                self.page_max_y,
                self.page_max_x,
                self.page_pos_y,
                self.page_pos_x_left
            )
            self.page_right = self.screen.subwin(
                self.page_max_y,
                self.page_max_x,
                self.page_pos_y,
                self.page_pos_x_right
            )

    def _set_toc_page(self):
        self.toc_page = self.screen.subwin(
            self.page_max_y,
            self.page_max_x,
            self.page_pos_y,
            self.page_pos_x
        )

    def _set_help_page(self):
        self.help_page = self.screen.subwin(
            self.page_max_y,
            self.page_max_x,
            self.page_pos_y,
            self.page_pos_x
        )

    def _set_selector(self):
        self.pointer = '->'
        self.index_suffix = ': '
        max_index = 3
        self.pointer_margin = len(self.pointer)
        self.toc_id_margin = self.pointer_margin + self.static_padding + max_index \
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
        self.help_pages = []
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
                    self.help_pages.append(page)
                    page = []
                    lines = 0
            if len(page) != 0:
                self.help_pages.append(page)
                page = []
                lines = 0

    def _set_toc(self):
        toc = self.book.get_toc()
        self.toc_pages = []
        page = []
        lines = 0
        for key in toc.keys():
            chapter = wrap(
                toc[key],
                self.page_max_x - self.toc_id_margin - self.static_padding
            )
            if lines + len(chapter) <= self.page_lines:
                page.append({
                    'id': key,
                    'name': chapter
                })
                lines += len(chapter)
            else:
                self.toc_pages.append(page)
                page = []
                lines = 0
        if len(page) != 0:
            self.toc_pages.append(page)

    def _set_pages(self):
        self.pages = []
        on_page = []
        if self.book.has_text(self.chapter):
            content = self.book.get_chapter_text(self.chapter)
            for index, paragraph in enumerate(content):
                lines_of_text = wrap(paragraph, self.page_columns)
                while len(lines_of_text) > 0:
                    if len(lines_of_text) + len(on_page) + 1 <= self.page_lines:
                        for text in lines_of_text:
                            if self.justify_full:
                                on_page.append([index, self._justify_line(text)])
                            else:
                                on_page.append([index, text])
                        if len(on_page) != 0:
                            on_page.append([index, ''])
                        lines_of_text = []
                    else:
                        for _ in range(len(on_page), self.page_lines):
                            if self.justify_full:
                                on_page.append([index, self._justify_line(lines_of_text[0])])
                            else:
                                on_page.append([index, lines_of_text[0]])
                            lines_of_text.pop(0)
                        self.pages.append(on_page)
                        on_page = []
            if len(on_page) != 0:
                self.pages.append(on_page)
        else:
            content = self.book.get_chapter_title(self.chapter)
            for line_of_text in wrap(content, self.page_columns):
                if self.justify_full:
                    on_page.append([0, self._justify_line(line_of_text)])
                else:
                    on_page.append([0, line_of_text])
            on_page.append([1, '* * *'])
            self.pages.append(on_page)

    def _set_speech_map(self):
        speech_open = ['\'', '"', '‘', '“']
        speech_close = ['\'', '"', '’', '”']
        speech_after = [' ', '.', ',',  ';', ':', '!', '?', '-', '—', speech_close]
        self.speech_map = self._get_coordinates_map(speech_open, speech_close, \
            speech_after)

    def _set_info_map(self):
        info_open = ['<', '(', '[', '{']
        info_close = ['>', ')', ']', '}']
        info_after = [' ', '.', ',',  ';', ':', '!', '?', '-', '—', info_close]
        self.info_map = self._get_coordinates_map(info_open, info_close, \
            info_after)

    # :::::::::::::::::::::::::::::: #
    # :::: GETTERS ::::::::::::::::: #
    # :::::::::::::::::::::::::::::: #

    def _get_coordinates_map(self, opening_marks, closing_marks, closing_after):
        coordinates_map = {}
        is_opened = False
        for index, page in enumerate(self.pages):
            coordinates_map[index] = {
                'opening_coordinates': [],
                'closing_coordinates': []
            }
            for y, line in enumerate(page):
                if is_opened and y == 0:
                    coordinates_map[index]['opening_coordinates'].append([y, 0])
                for x, character in enumerate(line[1]):
                    try:
                        if character in opening_marks \
                            and not is_opened \
                            and (x == 0 or line[1][x - 1] == ' '):
                            is_opened = True
                            current_mark = opening_marks.index(character)
                            coordinates_map[index]['opening_coordinates'].append([y, x])
                    except IndexError:
                        pass
                    if is_opened and character == closing_marks[current_mark]:
                        if x == len(line[1]) - 1 or line[1][x + 1] in closing_after:
                            is_opened = False
                            coordinates_map[index]['closing_coordinates'].append([y, x])
                if is_opened and y == len(page) - 1:
                    coordinates_map[index]['closing_coordinates'].append([y, len(line[1]) - 1])
        return coordinates_map

    def get_number_of_help_pages(self):
        return len(self.help_pages)

    def get_number_of_toc_pages(self):
        return len(self.toc_pages)

    def get_number_of_toc_positions(self, current_page):
        return len(self.toc_pages[current_page])

    def get_toc_position_id(self, current_page, current_pos):
        return self.toc_pages[current_page][current_pos]['id']

    def get_number_of_pages(self):
        return len(self.pages)

    def get_page_by_index(self, index):
        for current_page, page in enumerate(self.pages):
            for line in page:
                if index == line[0]:
                    return current_page
        return 0

    def get_current_page_index(self, current_page):
        if len(self.pages) != 1:
            return self.pages[current_page][0][0] + 1
        else:
            return self.pages[current_page][0][0]

    # :::::::::::::::::::::::::::::: #
    # :::: OTHER ::::::::::::::::::: #
    # :::::::::::::::::::::::::::::: #

    def _shorten_title(self, title):
        if len(title) >= self.page_max_x - self.static_padding * 2:
            return title[:self.page_max_x - self.static_padding * 2 - 4] + '...]'
        else:
            return title

    def increase_v_padding(self, padding):
        if padding < self.v_padding_max:
            padding += 1
        return padding

    def increase_h_padding(self, padding):
        if padding + 1 < self.h_padding_max:
            padding += 2
        return padding

    def decrease_v_padding(self, padding):
        if padding > self.v_padding_min:
            padding -= 1
        return padding

    def decrease_h_padding(self, padding):
        if padding - 1 > self.h_padding_min:
            padding -= 2
        return padding

    def increase_pe_multiplier(self):
        if self.pe_multiplier < .4:
            self.pe_multiplier += .1
        return self.pe_multiplier

    def decrease_pe_multiplier(self):
        if self.pe_multiplier >= .2:
            self.pe_multiplier -= .1
        return self.pe_multiplier

    def _justify_line(self, line):
        just_line = []
        words = line.split(" ")
        words_len = sum(len(word) for word in words)
        if words_len < int(self.page_columns / 1.8):
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

    # :::: PRINTERS :::::::::::::::: #

    def print_help_content(self, current_page):
        for y, line_of_text in enumerate(self.help_pages[current_page]):
            self.help_page.addstr(
                y + self.static_padding,
                self.static_padding,
                line_of_text,
                self.normal_colors
            )

    def print_help_header(self, current_page):
        help_title = '[HELP][' + self.help_sections[current_page] + ']'
        self.help_page.addstr(
            0,
            self.static_padding,
            self._shorten_title(help_title),
            self.info_colors
        )

    def print_help_footer(self, current_page):
        current_page += 1
        page_number = '[' + str(current_page) + '/' + str(self.get_number_of_help_pages()) + ']'
        pos_y = self.page_max_y - 1
        pos_x = self.page_max_x - len(page_number) - self.static_padding
        self.help_page.addstr(pos_y, pos_x, page_number, self.info_colors)


    def print_toc_content(self, current_page, pointer_pos):
        pos_y = self.static_padding
        for y, chapter in enumerate(self.toc_pages[current_page]):
            if pointer_pos == y:
                self.toc_page.addstr(
                    pos_y,
                    self.static_padding,
                    self.pointer,
                    self.select_colors
                )
                chapter_index = ' ' * abs((len(str(chapter['id'])) - 3) * -1) \
                    + str(chapter['id']) + self.index_suffix
                self.toc_page.addstr(
                    pos_y,
                    self.static_padding + self.pointer_margin,
                    chapter_index,
                    self.select_colors
                )
                for line in chapter['name']:
                    self.toc_page.addstr(
                        pos_y,
                        self.toc_id_margin,
                        line,
                        self.select_colors
                    )
                    pos_y += 1
            else:
                chapter_index = ' ' * abs((len(str(chapter['id'])) - 3) * -1) \
                    + str(chapter['id']) + ':'
                self.toc_page.addstr(
                    pos_y,
                    self.static_padding + self.pointer_margin,
                    chapter_index,
                    self.info_colors
                )
                for line in chapter['name']:
                    self.toc_page.addstr(
                        pos_y,
                        self.toc_id_margin,
                        line,
                        self.normal_colors
                    )
                    pos_y += 1

    def print_toc_footer(self, current_page):
        current_page += 1
        page_number = '[' + str(current_page) + '/' + str(self.get_number_of_toc_pages()) + ']'
        pos_y = self.page_max_y - 1
        pos_x = self.page_max_x - len(page_number) - self.static_padding
        self.toc_page.addstr(pos_y, pos_x, page_number, self.info_colors)

    def print_toc_header(self):
        toc_title = '[Table of Contents]'
        self.toc_page.addstr(
            0,
            self.static_padding,
            self._shorten_title(toc_title),
            self.info_colors
        )

    def print_page_content(self, current_page):
        is_open = False
        is_speech = False
        is_info = False
        if not self.double_page:
            for y, line in enumerate(self.pages[current_page]):
                for x, character in enumerate(line[1]):
                    if not is_open:
                        if [y, x] in self.speech_map[current_page]['opening_coordinates'] \
                            and self.highlight:
                            self.page.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.speech_colors)
                            is_open = True
                            is_speech = True
                        if [y, x] in self.info_map[current_page]['opening_coordinates'] \
                            and self.highlight:
                            self.page.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.info_colors)
                            is_open = True
                            is_info = True
                        if not is_info and not is_speech:
                            self.page.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.normal_colors)
                    else:
                        if is_info and not is_speech:
                            self.page.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.info_colors)
                            if [y, x] in self.info_map[current_page]['closing_coordinates']:
                                is_open = False
                                is_info = False
                        elif is_speech and not is_info:
                            self.page.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.speech_colors)
                            if [y, x] in self.speech_map[current_page]['closing_coordinates']:
                                is_open = False
                                is_speech = False
                        else:
                            self.page.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.info_colors)
                            if [y, x] in self.info_map[current_page]['closing_coordinates']:
                                is_open = False
                                is_speech = False
                                is_info = False
        else:
            for y, line in enumerate(self.pages[current_page]):
                for x, character in enumerate(line[1]):
                    if not is_open:
                        if [y, x] in self.speech_map[current_page]['opening_coordinates'] \
                            and self.highlight:
                            self.page_left.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.speech_colors)
                            is_open = True
                            is_speech = True
                        if [y, x] in self.info_map[current_page]['opening_coordinates'] \
                            and self.highlight:
                            self.page_left.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.info_colors)
                            is_open = True
                            is_info = True
                        if not is_info and not is_speech:
                            self.page_left.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.normal_colors)
                    else:
                        if is_info and not is_speech:
                            self.page_left.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.info_colors)
                            if [y, x] in self.info_map[current_page]['closing_coordinates']:
                                is_open = False
                                is_info = False
                        elif is_speech and not is_info:
                            self.page_left.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.speech_colors)
                            if [y, x] in self.speech_map[current_page]['closing_coordinates']:
                                is_open = False
                                is_speech = False
                        else:
                            self.page_left.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.info_colors)
                            if [y, x] in self.info_map[current_page]['closing_coordinates']:
                                is_open = False
                                is_speech = False
                                is_info = False
            try:
                current_page += 1
                for y, line in enumerate(self.pages[current_page]):
                        for x, character in enumerate(line[1]):
                            if not is_open:
                                if [y, x] \
                                    in self.speech_map[current_page]['opening_coordinates'] \
                                    and self.highlight:
                                    self.page_right.addstr(y + self.v_padding, x + self.h_padding, \
                                        character, self.speech_colors)
                                    is_open = True
                                    is_speech = True
                                if [y, x] \
                                    in self.info_map[current_page]['opening_coordinates'] \
                                    and self.highlight:
                                    self.page_right.addstr(y + self.v_padding, x + self.h_padding, \
                                        character, self.info_colors)
                                    is_open = True
                                    is_info = True
                                if not is_info and not is_speech:
                                    self.page_right.addstr(y + self.v_padding, x + self.h_padding, \
                                        character, self.normal_colors)
                            else:
                                if is_info and not is_speech:
                                    self.page_right.addstr(y + self.v_padding, x + self.h_padding, \
                                        character, self.info_colors)
                                    if [y, x] \
                                        in self.info_map[current_page]['closing_coordinates']:
                                        is_open = False
                                        is_info = False
                                elif is_speech and not is_info:
                                    self.page_right.addstr(y + self.v_padding, x + self.h_padding, \
                                        character, self.speech_colors)
                                    if [y, x] \
                                        in self.speech_map[current_page]['closing_coordinates']:
                                        is_open = False
                                        is_speech = False
                                else:
                                    self.page_right.addstr(y + self.v_padding, x + self.h_padding, \
                                        character, self.info_colors)
                                    if [y, x] \
                                        in self.info_map[current_page]['closing_coordinates']:
                                        is_open = False
                                        is_speech = False
                                        is_info = False
            except IndexError:
                pass

    def print_page_footer(self, current_page, quickmarks, quickmark_change):
        if not self.double_page:
            mark_tag = ''
            for mark in quickmarks.get_slots():
                if quickmark_change:
                    mark_tag = '[+]'
                elif quickmarks.get_chapter(mark) == self.chapter \
                    and self.get_page_by_index(quickmarks.get_index(mark)) \
                    == current_page:
                    mark_tag = '[' + str(mark) + ']'
            current_page += 1
            page_number = '[' + str(current_page) + '/' + str(self.get_number_of_pages()) + ']'
            pos_y = self.page_max_y - 1
            pos_x = self.page_max_x - self.static_padding
            self.page.addstr(pos_y, pos_x - len(mark_tag), mark_tag, self.info_colors)
            self.page.addstr(pos_y, pos_x - len(page_number) - len(mark_tag), page_number, self.info_colors)
        else:
            mark_tag = ''
            for mark in quickmarks.get_slots():
                if quickmark_change:
                    mark_tag = '[+]'
                elif quickmarks.get_chapter(mark) == self.chapter \
                    and self.get_page_by_index(quickmarks.get_index(mark)) \
                    == current_page:
                    mark_tag = '[' + str(mark) + ']'
            current_page += 1
            page_number = '[' + str(current_page) + '/' + str(self.get_number_of_pages()) + ']'
            pos_y = self.page_max_y - 1
            pos_x = self.page_max_x - self.static_padding - len(mark_tag)
            self.page_left.addstr(
                pos_y,
                pos_x,
                mark_tag,
                self.info_colors
            )
            self.page_left.addstr(pos_y, self.static_padding, page_number, self.info_colors)
            if current_page + 1 <= self.get_number_of_pages():
                mark_tag = ''
                for mark in quickmarks.get_slots():
                    if quickmark_change:
                        mark_tag = ''
                    elif quickmarks.get_chapter(mark) == self.chapter \
                        and self.get_page_by_index(quickmarks.get_index(mark)) \
                        == current_page:
                        mark_tag = '[' + str(mark) + ']'
                current_page += 1
                page_number = '[' + str(current_page) + '/' + str(self.get_number_of_pages()) + ']'
                pos_x = self.page_max_x - self.static_padding - len(page_number)
                self.page_right.addstr(
                    pos_y,
                    self.static_padding,
                    mark_tag,
                    self.info_colors
                )
                self.page_right.addstr(pos_y, pos_x, page_number, self.info_colors)

    def print_page_header(self):
        chapter_title = self.book.get_chapter_title(self.chapter)
        chapter_id = self.book.get_id(self.chapter)
        page_title = '[' +  str(chapter_id) + '][' + chapter_title + ']'
        if not self.double_page:
            self.page.addstr(
                0,
                self.static_padding,
                self._shorten_title(page_title),
                self.info_colors
            )
        else:
            self.page_left.addstr(
                0,
                self.static_padding,
                self._shorten_title(page_title),
                self.info_colors
            )

    def print_perception_expander(self, page):
        line_pos = int(self.page_columns * self.pe_multiplier)
        for y in range(self.page_lines):
            page.chgat(
                y + self.v_padding,
                self.h_padding + line_pos - 1,
                1,
                self.perception_colors
            )
            page.chgat(
                y + self.v_padding,
                self.page_columns + self.h_padding - line_pos,
                1,
                self.perception_colors
            )

    # :::: SPAWNERS :::::::::::::::: #

    def print_help_page(self, current_page):
        self.help_page.erase()
        if not self.double_page:
            self.page.clear()
        else:
            self.page_right.clear()
        self.help_page.bkgd(' ', self.info_colors)
        self.help_page.box()
        try:
            self.print_help_header(current_page)
            self.print_help_content(current_page)
            self.print_help_footer(current_page)
        except:
            pass
        self.help_page.refresh()

    def print_page(self, current_page, quickmarks, quickmark_change=False):
        if not self.double_page:
            self.page.erase()
            self.page.bkgd(' ', self.normal_colors)
            self.page.box()
            try:
                self.print_page_header()
                self.print_page_content(current_page)
                self.print_page_footer(current_page, quickmarks, quickmark_change)
                if self.speed_mode:
                    self.print_perception_expander(self.page)
            except:
                pass
            self.page.refresh()
        else:
            self.page_left.erase()
            self.page_right.erase()
            self.page_left.bkgd(' ', self.normal_colors)
            self.page_right.bkgd(' ', self.normal_colors)
            self.page_left.box()
            self.page_right.box()
            try:
                self.print_page_header()
                self.print_page_content(current_page)
                self.print_page_footer(current_page, quickmarks, quickmark_change)
                if self.speed_mode:
                    self.print_perception_expander(self.page_left)
                    self.print_perception_expander(self.page_right)
            except:
                pass
            self.page_left.refresh()
            self.page_right.refresh()


    def print_toc_page(self, current_page, pointer_pos):
        self.toc_page.erase()
        if not self.double_page:
            self.page.clear()
        else:
            self.page_right.clear()
        self.toc_page.bkgd(' ', self.info_colors)
        self.toc_page.box()
        try:
            self.print_toc_header()
            self.print_toc_content(current_page, pointer_pos)
            self.print_toc_footer(current_page)
        except:
            pass
        self.toc_page.refresh()

