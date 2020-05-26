#!/bin/python3

import os
import tempfile
import shutil
import zipfile
from pathlib import Path

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
