#!/bin/python3

import curses
from textwrap import wrap

class Screen:
    def __init__(self, title, version='2020', app_name='Simple Novel Reader'):
        self.title = title
        self.version = version
        self.app_name = app_name
        self._set_screen()

    def _set_screen(self):
        self.screen = curses.initscr()
        self.screen.keypad(1)
        self.max_y, self.max_x = self.screen.getmaxyx()

    def _get_colors(self, dark_mode):
        curses.start_color()
        if dark_mode:
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        else:
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
        return curses.color_pair(2)

    def get_screen(self):
        return self.screen

    def redraw(self, dark_mode):
        self.screen.erase()
        self.screen.bkgd(' ', self._get_colors(dark_mode))
        try:
            self.print_info(dark_mode)
        except:
            pass
        self.screen.refresh()

    def print_info(self, dark_mode):
        app_text = self.app_name + ' ' + self.version
        title_text = '[' + self.title + ']'
        keys = 'quit:[q] help:[?]'
        self.screen.addstr(0, 2, app_text, self._get_colors(dark_mode))
        if self.max_x > len(keys) + len(app_text) + 4:
            self.screen.addstr(0, self.max_x - len(keys) - 2, \
                keys, self._get_colors(dark_mode))
        self.screen.addstr(self.max_y - 1, 2, title_text, self._get_colors(dark_mode))

class Pager:
    def __init__(self, screen, book, chapter, dark_mode=False, highlight=False, \
        v_padding=2, h_padding=2):
        self.screen = screen
        self.book = book
        self.chapter = chapter
        self.dark_mode = dark_mode
        self.highlight = highlight
        self.v_padding = v_padding
        self.h_padding = h_padding * 2
        self.static_padding = 2
        self.screen_max_y, self.screen_max_x = screen.getmaxyx()
        self._set_page_max_y()
        self._set_page_max_x()
        self._set_page_pos_y()
        self._set_page_pos_x()
        self._set_page_lines()
        self._set_page_columns()
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

    def _set_page_pos_y(self):
        self.page_pos_y = 2

    def _set_page_pos_x(self):
        self.page_pos_x = int(self.screen_max_x / 2 - self.page_max_x / 2)

    def _set_page_lines(self):
        self.page_lines = self.page_max_y - (self.v_padding * 2)

    def _set_page_columns(self):
        self.page_columns = self.page_max_x - (self.h_padding * 2)

    def _set_page(self):
        self.page = self.screen.subwin(
            self.page_max_y,
            self.page_max_x,
            self.page_pos_y,
            self.page_pos_x
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
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        else:
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_WHITE)
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_WHITE)
        self.normal_colors = curses.color_pair(1)
        self.info_colors = curses.color_pair(2)
        self.speech_colors = curses.color_pair(3)
        self.select_colors = curses.color_pair(4)

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
                'HIGHLIGHT': 'v',
                'INCREASE PAGE PADDING': '>',
                'DECREASE PAGE PADDING': '<',
                'TABLE OF CONTENTS': 't, Tab',
                'ESCAPE': 'Esc, BackSpace',
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
        self.help_sections = {}
        page = []
        lines = 0
        for section in navigation.keys():
            self.help_sections[len(self.help_pages) - 1] = section
            for command in navigation[section].keys():
                command_text = wrap(command + ': ' + navigation[section][command],
                    self.page_columns - self.static_padding)
                lines += len(command_text)
                if lines <= self.page_lines:
                    for line_of_text in command_text:
                        page.append(line_of_text)
                else:
                    self.help_pages.append(page)
                    page = []
                    lines = 0
            if len(page) != 0:
                self.help_pages.append(page)
                page = []

    def _set_toc(self):
        toc = self.book.get_toc()
        self.toc_pages = []
        page = []
        lines = 0
        for key in toc.keys():
            chapter = wrap(toc[key], self.page_max_x - self.toc_id_margin)
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
                if len(lines_of_text) + len(on_page) + 1 <= self.page_lines:
                    for text in lines_of_text:
                        on_page.append([index, text])
                    if len(on_page) != 0:
                        on_page.append([index, ''])
                else:
                    for _ in range(len(on_page), self.page_lines):
                        on_page.append([index, lines_of_text[0]])
                        lines_of_text.pop(0)
                    self.pages.append(on_page)
                    on_page = []
                    for text in lines_of_text:
                        on_page.append([index, text])
                    if len(on_page) != 0:
                        on_page.append([index, ''])
            if len(on_page) != 0:
                self.pages.append(on_page)
        else:
            content = self.book.get_chapter_title(self.chapter)
            for line_of_text in wrap(content, self.page_columns):
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

    def get_current_page_index(self, current_page):
        if len(self.pages) != 1:
            return self.pages[current_page][0][0] + 1
        else:
            return self.pages[current_page][0][0]

    # :::::::::::::::::::::::::::::: #
    # :::: OTHER ::::::::::::::::::: #
    # :::::::::::::::::::::::::::::: #

    def shorten_title(self, title):
        if len(title) >= self.page_max_x - self.static_padding * 2:
            return title[:self.page_max_x - self.static_padding * 2 - 4] + '...]'
        else:
            return title

    # :::: PRINTERS :::::::::::::::: #

    def print_help_content(self, current_page):
        for y, line_of_text in enumerate(self.help_pages[current_page]):
            self.page.addstr(
                y + self.static_padding,
                self.static_padding,
                line_of_text,
                self.normal_colors
            )

    def print_help_header(self, current_page):
        help_title = '[HELP][' + self.help_sections[current_page - 1] + ']'
        self.toc_page.addstr(
            0,
            self.static_padding,
            self.shorten_title(help_title),
            self.info_colors
        )

    def print_help_footer(self, current_page):
        current_page += 1
        page_number = '[' + str(current_page) + '/' + str(self.get_number_of_help_pages()) + ']'
        pos_y = self.page_max_y - 1
        pos_x = self.page_max_x - len(page_number) - self.static_padding
        self.page.addstr(pos_y, pos_x, page_number, self.info_colors)


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
        self.page.addstr(pos_y, pos_x, page_number, self.info_colors)

    def print_toc_header(self):
        toc_title = '[Table of Contents]'
        self.toc_page.addstr(
            0,
            self.static_padding,
            self.shorten_title(toc_title),
            self.info_colors
        )

    def print_page_content(self, current_page):
        is_open = False
        is_speech = False
        is_info = False
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
                            character, curses.A_NORMAL)
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

    def print_page_footer(self, current_page, quickmarks, quickmark_change):
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
        pos_x = self.page_max_x - len(mark_tag) - self.static_padding
        self.page.addstr(pos_y, pos_x, mark_tag, self.info_colors)
        self.page.addstr(pos_y, pos_x - len(page_number), page_number, self.info_colors)

    def print_page_header(self):
        chapter_title = self.book.get_chapter_title(self.chapter)
        chapter_id = self.book.get_id(self.chapter)
        page_title = '[' +  str(chapter_id) + '][' + chapter_title + ']'
        self.page.addstr(
            0,
            self.static_padding,
            self.shorten_title(page_title),
            self.info_colors
        )

    # :::: SPAWNERS :::::::::::::::: #

    def print_help_page(self, current_page):
        self.help_page.erase()
        self.page.clear()
        self.help_page.bkgd(' ', self.info_colors)
        self.help_page.box()
        self.print_help_header(current_page)
        self.print_help_content(current_page)
        self.print_help_footer(current_page)
        self.help_page.refresh()

    def print_page(self, current_page, quickmarks, quickmark_change=False):
        self.page.erase()
        self.page.bkgd(' ', self.normal_colors)
        self.page.box()
        self.print_page_header()
        self.print_page_content(current_page)
        self.print_page_footer(current_page, quickmarks, quickmark_change)
        self.page.refresh()

    def print_toc_page(self, current_page, pointer_pos):
        self.toc_page.erase()
        self.page.clear()
        self.toc_page.bkgd(' ', self.info_colors)
        self.toc_page.box()
        self.print_toc_header()
        self.print_toc_content(current_page, pointer_pos)
        self.print_toc_footer(current_page)
        self.toc_page.refresh()

class Quickmarks:
    def __init__(self, quickmarks=None):
        self.quickmarks = self._set_quickmarks(quickmarks)

    def _set_quickmarks(self, quickmarks):
        if quickmarks is None:
            quickmarks = {}
            for mark in range(1, 10):
                quickmarks[str(mark)] = {
                    'chapter': None,
                    'index': None
                }
            return quickmarks
        else:
            return quickmarks

    def set_quickmark(self, mark, chapter, index):
        for slot in self.get_slots():
            if self.get_chapter(slot) == chapter \
                and self.get_index(slot) == index:
                    self.quickmarks[str(slot)]['chapter'] = None
                    self.quickmarks[str(slot)]['index'] = None
        self.quickmarks[str(mark)]['chapter'] = chapter
        self.quickmarks[str(mark)]['index'] = index

    def get_quickmarks(self):
        return self.quickmarks

    def get_slots(self):
        return self.quickmarks.keys()

    def get_chapter(self, mark):
        if self.quickmarks[str(mark)]['chapter'] is not None:
            return self.quickmarks[str(mark)]['chapter']

    def get_index(self, mark):
        if self.quickmarks[str(mark)]['index'] is not None:
            return self.quickmarks[str(mark)]['index']

    def is_set(self, mark):
        if self.quickmarks[str(mark)]['chapter'] is None:
            return False
        else:
            return True
