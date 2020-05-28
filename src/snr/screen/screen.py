#!/bin/python3

import curses
from snr.reader import ConfigReader

class Screen:
    def __init__(
        self,
        title,
        dark_mode,
        speed_mode,
        highlight,
        double_page,
        justify_full,
        version='2020',
        app_name='Simple Novel Reader'
    ):
        self.title = title
        self.version = version
        self.app_name = app_name
        self.dark_mode = dark_mode
        self.speed_mode = speed_mode
        self.highlight = highlight
        self.double_page = double_page
        self.justify_full = justify_full
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
            'f': self.justify_full
        }

    def _get_primary(self):
        if self.dark_mode:
            return curses.color_pair(6)
        else:
            return curses.color_pair(1)

    def _get_modes_info(self):
        modes_info = 'modes:['
        for mode in self.modes.keys():
            if self.modes[mode]:
                modes_info += mode
            else:
                modes_info += '-'
        modes_info += ']'
        return modes_info

    def get_screen(self):
        return self.screen

    def _shorten(self, text, bracer=''):
        text_end = '...' + bracer
        if len(text) >= self.max_x - self.padding * 2:
            return text[:self.max_x - self.padding * 2 - len(text_end)] + text_end
        else:
            return text

    def _print_info(self):
        app_text = self.app_name + ' ' + self.version
        title_text = '[' + self.title + ']'
        keys =  self._get_modes_info() + ' quit:[q] help:[?]'
        self.screen.addstr(0, 2, self._shorten(app_text), self._get_primary())
        if self.max_x > len(keys) + len(app_text) + 4:
            self.screen.addstr(
                0,
                self.max_x - len(keys) - self.padding,
                keys,
                self._get_primary()
            )
        else:
            self.screen.addstr(
                1,
                self.padding,
                keys,
                self._get_primary()
            )
        self.screen.addstr(self.max_y - 1,
            self.padding,
            self._shorten(title_text, ']'),
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
