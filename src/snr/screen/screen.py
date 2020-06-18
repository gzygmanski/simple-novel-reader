#!/usr/bin/env python3

import curses
import snr.constants.info as Constant
from snr.reader import ConfigReader

class Screen:
    def __init__(
        self,
        title,
        modes,
        is_dict_installed,
        language='-'
    ):
        self.title = title
        self.dark_mode = modes['dark_mode']
        self.speed_mode = modes['speed_mode']
        self.highlight = modes['highlight']
        self.double_page = modes['double_page']
        self.justify_full = modes['justify_full']
        self.hyphenation = modes['hyphenation']
        self.is_dict_installed = is_dict_installed
        self.language = language
        self.padding = 2
        self._set_screen()
        self._set_colors()
        self._set_modes()

    def _set_screen(self):
        self.screen = curses.initscr()
        self.screen.keypad(1)
        self.max_y, self.max_x = self.screen.getmaxyx()

    def _set_colors(self):
        config = ConfigReader()
        colors = config.get_colors()
        curses.start_color()
        curses.use_default_colors()
        try:
            curses.init_pair(
                1,
                int(colors['foreground_light']),
                int(colors['background_light'])
            )
            curses.init_pair(
                2,
                int(colors['info_light']),
                int(colors['background_light'])
            )
            curses.init_pair(
                3,
                int(colors['speech_light']),
                int(colors['background_light'])
            )
            curses.init_pair(
                4,
                int(colors['select_light']),
                int(colors['background_light'])
            )
            curses.init_pair(
                5,
                int(colors['foreground_light']),
                int(colors['speed_mode_line_light'])
            )
            curses.init_pair(
                6,
                int(colors['foreground_dark']),
                int(colors['background_dark'])
            )
            curses.init_pair(
                7,
                int(colors['info_dark']),
                int(colors['background_dark'])
            )
            curses.init_pair(
                8,
                int(colors['speech_dark']),
                int(colors['background_dark'])
            )
            curses.init_pair(
                9,
                int(colors['select_dark']),
                int(colors['background_dark'])
            )
            curses.init_pair(
                10,
                int(colors['foreground_dark']),
                int(colors['speed_mode_line_dark'])
            )
        except:
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_WHITE)
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_WHITE)
            curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW)
            curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(8, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(9, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_RED)

    def _set_modes(self):
        self.modes = {
            'r': self.dark_mode,
            's': self.speed_mode,
            'v': self.highlight,
            'd': self.double_page,
            'f': self.justify_full,
            'e': self.hyphenation
        }

    def _get_primary(self):
        if self.dark_mode:
            return curses.color_pair(6)
        else:
            return curses.color_pair(1)

    def _get_modes_info(self):
        modes_info = '['
        for mode in self.modes.keys():
            if self.modes[mode]:
                modes_info += mode
            else:
                modes_info += '-'
        modes_info += ']'
        return modes_info

    def get_screen(self):
        return self.screen

    def _shorten(self, text, bracer='', text_after=''):
        text_end = '...' + bracer
        if len(text) >= self.max_x - self.padding * 2 - len(text_after):
            return text[:self.max_x - self.padding * 2 - len(text_end) - len(text_after)] + text_end
        else:
            return text

    def _print_info(self):
        app_text = Constant.APP + ' ' + Constant.VERSION
        title_text = '[' + self.title + ']'
        if not self.is_dict_installed:
            language_text = '[*' + self.language + ']'
        else:
            language_text = '[' + self.language + ']'
        keys =  'modes:' + self._get_modes_info() + ' quit:[q] help:[?]'
        if self.max_x <= len(keys) + len(app_text) + 4:
            app_text = Constant.SHORT_APP + ' ' + Constant.VERSION
        if self.max_x <= len(keys) + len(app_text) + 4:
            keys = self._get_modes_info() + '[?]'
        if self.max_x > len(keys) + len(app_text) + 4:
            self.screen.addstr(0, 2, self._shorten(app_text), self._get_primary())
            self.screen.addstr(
                0,
                self.max_x - len(keys) - self.padding,
                keys,
                self._get_primary()
            )
        else:
            self.screen.addstr(
                0,
                self.max_x - len(keys) - self.padding,
                keys,
                self._get_primary()
            )
        self.screen.addstr(
            self.max_y - 1,
            self.padding,
            self._shorten(title_text, ']', language_text),
            self._get_primary()
        )
        self.screen.addstr(
            self.max_y - 1,
            self.max_x - len(language_text) - self.padding,
            language_text,
            self._get_primary()
        )

    def redraw(self):
        self.screen.erase()
        self.screen.bkgd(' ', self._get_primary())
        try:
            self._print_info()
        except:
            pass
        self.screen.refresh()
