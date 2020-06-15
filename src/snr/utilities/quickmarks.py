#!/usr/bin/env python3

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
