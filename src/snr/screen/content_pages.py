#!/usr/bin/env python3

import curses
from textwrap import wrap
from textwrap2 import wrap as wrap2
from .pages import Pages

class ContentPages(Pages):
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
        hyphenation=False,
        v_padding=2,
        h_padding=2,
        pe_multiplier=.2
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
        self.hyphenation = hyphenation
        self.pe_multiplier = pe_multiplier
        self._set_page()
        self._set_pages()
        self._set_speech_map()
        self._set_info_map()

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

    def _set_pages(self):
        self.pages = []
        on_page = []
        if self.book.has_text(self.chapter):
            content = self.book.get_chapter_text(self.chapter)
            for index, paragraph in enumerate(content):
                if self.book.has_dict() and self.hyphenation:
                    try:
                        lines_of_text = wrap2(paragraph, self.page_columns, use_hyphenator=self.book.get_lang_dict())
                    except:
                        lines_of_text = wrap(paragraph, self.page_columns)
                else:
                    lines_of_text = wrap(paragraph, self.page_columns)
                while len(lines_of_text) > 0:
                    if len(lines_of_text) + len(on_page) + 1 <= self.page_lines:
                        for text in lines_of_text:
                            if self.justify_full:
                                on_page.append([index, self.justify_line(text)])
                            else:
                                on_page.append([index, text])
                        if len(on_page) != 0:
                            on_page.append([index, ''])
                        lines_of_text = []
                    else:
                        for _ in range(len(on_page), self.page_lines):
                            if self.justify_full:
                                on_page.append([index, self.justify_line(lines_of_text[0])])
                            else:
                                on_page.append([index, lines_of_text[0]])
                            lines_of_text.pop(0)
                        self.pages.append(on_page)
                        on_page = []
            if len(on_page) != 0:
                self.pages.append(on_page)
        else:
            content = self.book.get_chapter_title(self.chapter)
            if self.book.has_dict() and self.hyphenation:
                try:
                    lines_of_text = wrap2(content, self.page_columns, use_hyphenator=self.book.get_lang_dict())
                except:
                    lines_of_text = wrap(content, self.page_columns)
            else:
                lines_of_text = wrap(content, self.page_columns)
            for text in lines_of_text:
                if self.justify_full:
                    on_page.append([0, self.justify_line(text)])
                else:
                    on_page.append([0, text])
            on_page.append([1, '* * *'])
            self.pages.append(on_page)

    def _set_speech_map(self):
        self._speech_open = ['\'', '"', '‘', '“']
        self._speech_close = ['\'', '"', '’', '”']
        self._speech_after = ['\n', ' ', '.', ',',  ';', ':', '!', '?', '-', '—']
        self._speech_after.extend(self._speech_close)
        self.speech_map = self._get_coordinates_map(self._speech_open, self._speech_close, \
            self._speech_after)

    def _set_info_map(self):
        self._info_open = ['<', '(', '[', '{']
        self._info_close = ['>', ')', ']', '}']
        self._info_after = ['\n', ' ', '.', ',',  ';', ':', '!', '?', '-', '—']
        self._info_after.extend(self._info_close)
        self._info_after.extend(self._speech_close)
        self.info_map = self._get_coordinates_map(self._info_open, self._info_close, \
            self._info_after)

    # :::: GETTERS ::::::::::::::::: #

    def _get_coordinates_map(self, opening_marks, closing_marks, closing_after):
        coordinates_map = {}
        previous_index = 0
        is_opened = False
        for index, page in enumerate(self.pages):
            coordinates_map[index] = {
                'opening_coordinates': [],
                'closing_coordinates': []
            }
            for y, line in enumerate(page):
                if is_opened and line[0] > previous_index:
                    is_opened = False
                    coordinates_map[index]['closing_coordinates'].append([y - 2, len(page[y - 2][1]) - 1])
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
                        if is_opened and character == closing_marks[current_mark]:
                            if x == len(line[1]) - 1 or line[1][x + 1] in closing_after:
                                is_opened = False
                                coordinates_map[index]['closing_coordinates'].append([y, x])
                    except IndexError:
                        pass
                if is_opened and y == len(page) - 1:
                    if line[1] != '':
                        coordinates_map[index]['closing_coordinates'].append([y, len(line[1]) - 1])
                    else:
                        coordinates_map[index]['closing_coordinates'].append([y, len(line[1])])
                previous_index = line[0]
        return coordinates_map

    def _get_page_content(self, current_page, page, quickmark_change, index):
        is_open = False
        is_speech = False
        is_info = False
        if self.highlight:
            try:
                for y, line in enumerate(self.pages[current_page]):
                    for x, character in enumerate(line[1]):
                        if quickmark_change and line[0] == index:
                            page.addstr(y + self.v_padding, x + self.h_padding, \
                                character, self.select_colors)
                        else:
                            if not is_open:
                                if [y, x] in self.speech_map[current_page]['opening_coordinates']:
                                    page.addstr(y + self.v_padding, x + self.h_padding, \
                                        character, self.speech_colors)
                                    is_open = True
                                    is_speech = True
                                elif [y, x] in self.info_map[current_page]['opening_coordinates']:
                                    page.addstr(y + self.v_padding, x + self.h_padding, \
                                        character, self.info_colors)
                                    is_open = True
                                    is_info = True
                                else:
                                    page.addstr(y + self.v_padding, x + self.h_padding, \
                                        character, self.normal_colors)
                            else:
                                if is_speech:
                                    page.addstr(y + self.v_padding, x + self.h_padding, \
                                        character, self.speech_colors)
                                    if [y, x] in self.speech_map[current_page]['closing_coordinates']:
                                        is_open = False
                                        is_speech = False
                                elif is_info:
                                    page.addstr(y + self.v_padding, x + self.h_padding, \
                                        character, self.info_colors)
                                    if [y, x] in self.info_map[current_page]['closing_coordinates']:
                                        is_open = False
                                        is_info = False
            except IndexError:
                pass
        else:
            try:
                for y, line in enumerate(self.pages[current_page]):
                    if quickmark_change and line[0] == index:
                        page.addstr(y + self.v_padding, self.h_padding, \
                            line[1], self.select_colors)
                    else:
                        page.addstr(y + self.v_padding, self.h_padding, \
                            line[1], self.normal_colors)
            except IndexError:
                pass

    def _get_quickmark_tag(self, current_page, quickmarks, quickmark_change, tag=''):
        mark_tag = ''
        for mark in quickmarks.get_slots():
            if quickmark_change:
                mark_tag = tag
            elif quickmarks.get_chapter(mark) == self.chapter \
                and self.get_page_by_index(quickmarks.get_index(mark)) \
                == current_page:
                mark_tag = '[Q:' + str(mark) + ']'
        return mark_tag

    def _get_bookmark_tag(self, current_page, bookmarks):
        mark_tag = ''
        keys = []
        bookmarks = bookmarks.get_bookmarks()
        for bookmark in bookmarks.keys():
            if self.chapter == bookmarks[bookmark]['chapter'] \
                and current_page == self.get_page_by_index(bookmarks[bookmark]['index']):
                keys.append(bookmark)
        if len(keys) == 0:
            return mark_tag
        else:
            mark_tag = '[B:'
            for index, key in enumerate(keys):
                if index == len(keys) - 1:
                    mark_tag += key + ']'
                else:
                    mark_tag += key + ','
            return mark_tag

    def get_number_of_pages(self):
        return len(self.pages)

    def get_page_by_index(self, index):
        for current_page, page in enumerate(self.pages):
            for line in page:
                if index == line[0]:
                    return current_page
        return 0

    def get_current_page_index(self, current_page):
        return self.pages[current_page][0][0]

    def get_current_page_last_index(self, current_page):
        return self.pages[current_page][-1][0]

    # :::: OTHER ::::::::::::::::::: #

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

    def increase_index(self, index, page):
        if not self.double_page and index < self.get_current_page_last_index(page):
            return index + 1
        elif self.double_page:
            try:
                if index < self.get_current_page_last_index(page + 1):
                    return index + 1
            except IndexError:
                if index < self.get_current_page_last_index(page):
                    return index + 1
        return index

    def decrease_index(self, index, page):
        if index > self.get_current_page_index(page):
            return index - 1
        return index

    # :::: PRINTERS :::::::::::::::: #

    def _print_header(self):
        chapter_title = self.book.get_chapter_title(self.chapter)
        chapter_id = self.book.get_id(self.chapter)
        page_title = '[' +  str(chapter_id) + '][' + chapter_title + ']'
        if not self.double_page:
            self.page.addstr(
                0,
                self.static_padding,
                self.shorten_title(page_title),
                self.info_colors
            )
        else:
            self.page_left.addstr(
                0,
                self.static_padding,
                self.shorten_title(page_title),
                self.info_colors
            )

    def _print_content(self, current_page, quickmark_change, index):
        if not self.double_page:
            self._get_page_content(current_page, self.page, quickmark_change, index)
        else:
            self._get_page_content(current_page, self.page_left, quickmark_change, index)
            self._get_page_content(current_page + 1, self.page_right, quickmark_change, index)

    def _print_footer(self, current_page, bookmarks, quickmarks, quickmark_change):
        if not self.double_page:
            mark_tag = self._get_quickmark_tag(current_page, quickmarks, quickmark_change, '[Q:+]') \
                + self._get_bookmark_tag(current_page, bookmarks)
            current_page += 1
            page_number = '[' + str(current_page) + '/' + str(self.get_number_of_pages()) + ']'
            pos_y = self.page_max_y - 1
            pos_x = self.page_max_x - self.static_padding
            self.page.addstr(pos_y, pos_x - len(mark_tag), mark_tag, self.info_colors)
            self.page.addstr(pos_y, pos_x - len(page_number) - len(mark_tag), page_number, self.info_colors)
        else:
            mark_tag = self._get_quickmark_tag(current_page, quickmarks, quickmark_change, '[Q:+]') \
                + self._get_bookmark_tag(current_page, bookmarks)
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
                mark_tag = self._get_bookmark_tag(current_page, bookmarks) \
                    + self._get_quickmark_tag(current_page, quickmarks, quickmark_change)
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

    def print_page(self, current_page, bookmarks, quickmarks, quickmark_change=False, index=None):
        if index is None:
            index = self.get_current_page_index(current_page)
        if not self.double_page:
            self.page.erase()
            self.page.bkgd(' ', self.normal_colors)
            self.page.box()
            try:
                self._print_header()
                self._print_content(current_page, quickmark_change, index)
                self._print_footer(current_page, bookmarks, quickmarks, quickmark_change)
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
                self._print_header()
                self._print_content(current_page, quickmark_change, index)
                self._print_footer(current_page, bookmarks, quickmarks, quickmark_change)
                if self.speed_mode:
                    self.print_perception_expander(self.page_left)
                    self.print_perception_expander(self.page_right)
            except:
                pass
            self.page_left.refresh()
            self.page_right.refresh()
