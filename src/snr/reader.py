#!/bin/python3

import os, tempfile, shutil, zipfile, configparser, json, tempfile
from distutils.util import strtobool
from gi.repository import GLib
from pathlib import Path

class Config:
    def __init__(self, access_rights=0o755):
        self.access_rights = access_rights
        self._set_config_dir()

    def _set_config_dir(self):
        self.config_dir = os.path.join(GLib.get_user_config_dir(), 'snr/')
        if not os.path.exists(self.config_dir):
            try:
                os.mkdir(self.config_dir, self.access_rights)
            except OSError:
                print ("Creation of the directory %s failed" % self.config_dir)


class ConfigReader(Config):
    def __init__(self, config_file=None):
        Config.__init__(self)
        self.general_section = 'DEFAULT'
        self._set_config_file(config_file)
        self._set_config()

    def _set_config_file(self, config_file):
        if not config_file:
            self.config_file = os.path.join(self.config_dir + 'config.ini')

    def _set_config(self):
        self.config = configparser.ConfigParser()
        if os.path.isfile(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config[self.general_section] = {
                'dark_mode': 'on',
                'highlight': 'on',
                'horizontal_padding': '2',
                'vertical_padding': '2'
            }
            with open(self.config_file, 'w') as f:
                self.config.write(f)

    def get_dark_mode(self):
        return bool(strtobool(self.config[self.general_section]['dark_mode']))

    def get_highlight(self):
        return bool(strtobool(self.config[self.general_section]['highlight']))

    def get_horizontal_padding(self):
        return int(self.config[self.general_section]['horizontal_padding'])

    def get_vertical_padding(self):
        return int(self.config[self.general_section]['vertical_padding'])

class StateReader(Config):
    def __init__(self):
        Config.__init__(self)
        self._set_state_file()
        self._set_state()

    def _set_state_file(self):
        self.state_file = os.path.join(self.config_dir + 'state.json')

    def _set_state(self):
        if os.path.isfile(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {'default': {}}

    def save(self, path, title, chapter, index, quickmarks):
        new_key = self.key_parser(title)
        self.state['default']['path'] = path
        self.state['default']['title'] = title
        self.state['default']['chapter'] = chapter
        self.state['default']['index'] = index
        self.state['default']['quickmarks'] = quickmarks
        self.state[new_key] = {
            'path': path,
            'title': title,
            'chapter': chapter,
            'index': index,
            'quickmarks': quickmarks
        }
        with open (self.state_file, 'w') as f:
            json.dump(self.state, f)

    def exists(self, title):
        if self.key_parser(title) in self.state.keys():
            return True

    def key_parser(self, key):
        return ''.join(x for x in key if x.isalnum()).lower()

    def get_path(self, book='default'):
        return self.state[self.key_parser(book)]['path']

    def get_title(self, book='default'):
        return self.state[self.key_parser(book)]['title']

    def get_chapter(self, book='default'):
        return self.state[self.key_parser(book)]['chapter']

    def get_index(self, book='default'):
        return self.state[self.key_parser(book)]['index']

    def get_quickmarks(self, book='default'):
        return self.state[self.key_parser(book)]['quickmarks']

class FileReader:
    def __init__(self, file_path, access_rights=0o755):
        self.file_path = file_path
        self.access_rights = access_rights
        self._set_path()
        self._set_temp_dir()
        self._unzip_file()

    def _set_path(self):
        self.path = os.path.join(tempfile.gettempdir(), 'snr/')

    def _set_temp_dir(self):
        if not os.path.exists(self.path):
            try:
                os.mkdir(self.path, self.access_rights)
            except OSError:
                print ("Creation of the directory %s failed" % self.path)
        else:
            for filename in os.listdir(self.path):
                file_path = os.path.join(self.path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except OSError as e:
                    print('Failed to delete %s, because of %s' % (file_path, e))

    def _unzip_file(self):
        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.path)

    def get_toc_file(self):
        for path in Path(self.path).rglob('*.ncx'):
            return str(path)

    def get_content_file(self):
        for path in Path(self.path).rglob('*.opf'):
            return str(path)

    def get_directory_path(self, toc_path):
        return toc_path[:toc_path.rfind('/')]
