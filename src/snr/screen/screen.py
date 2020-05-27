#!/bin/python3

import curses
from snr.reader import ConfigReader

class Screen:
    def __init__(self, title, version='2020', app_name='Simple Novel Reader'):
        self.title = title
        self.version = version
        self.app_name = app_name
        self._set_screen()
        self._set_colors()

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
                int(colors['foreground_dark']),
                int(colors['background_dark'])
            )
            curses.init_pair(
                6,
                int(colors['info_dark']),
                int(colors['background_dark'])
            )
            curses.init_pair(
                7,
                int(colors['speech_dark']),
                int(colors['background_dark'])
            )
            curses.init_pair(
                8,
                int(colors['select_dark']),
                int(colors['background_dark'])
            )
        except:
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_WHITE)
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_WHITE)
            curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)

    def _get_primary(self, dark_mode):
        if dark_mode:
            return curses.color_pair(6)
        else:
            return curses.color_pair(2)

    def get_screen(self):
        return self.screen

    def redraw(self, dark_mode):
        self.screen.erase()
        self.screen.bkgd(' ', self._get_primary(dark_mode))
        try:
            self.print_info(dark_mode)
        except:
            pass
        self.screen.refresh()

    def print_info(self, dark_mode):
        app_text = self.app_name + ' ' + self.version
        title_text = '[' + self.title + ']'
        keys = 'quit:[q] help:[?]'
        self.screen.addstr(0, 2, app_text, self._get_primary(dark_mode))
        if self.max_x > len(keys) + len(app_text) + 4:
            self.screen.addstr(
                0,
                self.max_x - len(keys) - 2,
                keys,
                self._get_primary(dark_mode)
            )
        self.screen.addstr(self.max_y - 1, 2, title_text, self._get_primary(dark_mode))
