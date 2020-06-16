#!/usr/bin/env python3

import os
import tempfile
import snr.constants.info as info
from subprocess import Popen

class Bookmarks:
    def __init__(self, bookmarks=None):
        self.bookmarks = self._set_bookmarks(bookmarks)
        self._set_editor()
        self._set_template()

    def _set_bookmarks(self, bookmarks):
        if bookmarks is None:
            return {}
        else:
            return bookmarks

    def _set_editor(self):
        self.editor = os.environ.get('EDITOR', 'vim')

    def _set_template(self):
        self.title = 'BOOKMARK TEMPLATE'
        self.app_info = '[' + info.SHORT_APP + ' ' + info.VERSION + ']'
        self.name_tag = '-- Name'
        self.description_tag = '-- Description'
        self.template = self.title + ' ' \
            + self.app_info + '\n' \
            + self.name_tag + '\n\n' \
            + self.description_tag + '\n\n'

    def _set_bookmark(self, name, description, chapter, index):
        self.bookmarks[str(len(self.bookmarks))] = {
            'name': name,
            'description': description,
            'chapter': chapter,
            'index': index
        }

    def get_bookmarks(self):
        return self.bookmarks

    def get_chapter(self, key):
        return self.bookmarks[key]['chapter']

    def get_index(self, key):
        return self.bookmarks[key]['index']

    def get_keys(self):
        return self.bookmarks.keys()

    def create(self, chapter, index):
        with tempfile.NamedTemporaryFile(suffix='.tmp') as f:
            f.write(bytes(self.template, 'utf-8'))
            f.flush()
            edit = Popen([self.editor, f.name], start_new_session=True)
            edit.wait()
            f.seek(0)
            lines = f.readlines()
            name = lines[2].decode('utf-8').strip()
            description = []
            for i, paragraph in enumerate(lines[4:]):
                description.append(paragraph.decode('utf-8').strip())
            if name != '':
                self._set_bookmark(name, description, chapter, index)

    def remove(self, key_to_remove):
        if key_to_remove in self.bookmarks:
            del self.bookmarks[key_to_remove]
        new_bookmarks = {}
        for index, key in enumerate(self.bookmarks.keys()):
            new_bookmarks[str(index)] = self.bookmarks[key]
        self.bookmarks = new_bookmarks

    def edit(self, key):
        with tempfile.NamedTemporaryFile(suffix='.tmp') as f:
            content = self.title + ' ' \
                + self.app_info +  '\n' \
                + self.name_tag + '\n' \
                + self.bookmarks[key]['name'] + '\n' \
                + self.description_tag + '\n'
            for line_of_text in self.bookmarks[key]['description']:
                content += line_of_text + '\n'
            f.write(bytes(content, 'utf-8'))
            f.flush()
            edit = Popen([self.editor, f.name], start_new_session=True)
            edit.wait()
            f.seek(0)
            lines = f.readlines()
            name = lines[2].decode('utf-8').strip()
            description = []
            for i, paragraph in enumerate(lines[4:]):
                if paragraph.decode('utf-8').strip() != '':
                    description.append(paragraph.decode('utf-8').strip())
            if len(name) != 0:
                self.bookmarks[key]['name'] = name
            self.bookmarks[key]['description'] = description

    def has_bookmarks(self):
        return True if len(self.bookmarks) > 0 else False

    def has_description(self, key):
        if len(self.bookmarks[key]['description']) == 1 and self.bookmarks[key]['description'][0] == '':
            return False
        else:
            return True
