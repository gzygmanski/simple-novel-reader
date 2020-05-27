#!/bin/python3

import os
import configparser
import appdirs
from distutils.util import strtobool
from .config import Config

class ConfigReader(Config):
    def __init__(self, config_file=None):
        Config.__init__(self)
        self.general_section = 'DEFAULT'
        self.colors_section = 'COLORS'
        self._set_config_file(config_file)
        self._set_config()

    def _set_config_file(self, config_file):
        if not config_file:
            self.config_file = os.path.join(self.config_dir, 'config.ini')

    def _set_config(self):
        self.config = configparser.ConfigParser()
        if os.path.isfile(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config[self.general_section] = {
                'dark_mode': 'on',
                'highlight': 'on',
                'double_page': 'off',
                'horizontal_padding': '2',
                'vertical_padding': '2'
            }
            self.config[self.colors_section] = {
                'background_light': '15',
                'foreground_light': '0',
                'info_light': '9',
                'speech_light': '2',
                'select_light': '11',
                'background_dark': '0',
                'foreground_dark': '15',
                'info_dark': '12',
                'speech_dark': '11',
                'select_dark': '2'
            }
            with open(self.config_file, 'w') as f:
                self.config.write(f)

    def get_dark_mode(self):
        return bool(strtobool(self.config[self.general_section]['dark_mode']))

    def get_highlight(self):
        return bool(strtobool(self.config[self.general_section]['highlight']))

    def get_double_page(self):
        return bool(strtobool(self.config[self.general_section]['double_page']))

    def get_horizontal_padding(self):
        return int(self.config[self.general_section]['horizontal_padding'])

    def get_vertical_padding(self):
        return int(self.config[self.general_section]['vertical_padding'])

    def get_colors(self):
        return self.config[self.colors_section]
