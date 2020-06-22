#!/usr/bin/env python3

import os
import json
import snr.constants.messages as Msg
from .config import Config

class StateReader(Config):
    def __init__(self, verbose=False):
        Config.__init__(self, verbose)
        self._set_state_file()
        self._set_state()

    def _set_state_file(self):
        self.state_file = os.path.join(self.config_dir, 'state.json')

    def _set_state(self):
        if os.path.isfile(self.state_file):
            with open(self.state_file, 'r') as f:
                if self.verbose:
                    print(Msg.LOAD_STATE)
                self.state = json.load(f)
        else:
            self.state = {'default': {}}

    def save(self, path, title, chapter, index, quickmarks, bookmarks):
        new_key = self.key_parser(title)
        self.state['default']['path'] = path
        self.state['default']['title'] = title
        self.state['default']['chapter'] = chapter
        self.state['default']['index'] = index
        self.state['default']['quickmarks'] = quickmarks
        self.state['default']['bookmarks'] = bookmarks
        self.state[new_key] = {
            'path': path,
            'title': title,
            'chapter': chapter,
            'index': index,
            'quickmarks': quickmarks,
            'bookmarks': bookmarks
        }
        with open (self.state_file, 'w') as f:
            if self.verbose:
                print(Msg.SAVE_STATE)
            json.dump(self.state, f, indent=2)

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

    def get_bookmarks(self, book='default'):
        return self.state[self.key_parser(book)]['bookmarks']
