#!/usr/bin/env python3

import os
import tempfile
import shutil
import zipfile
from pathlib import Path
import snr.constants.messages as Msg

class FileReader:
    def __init__(self, file_path, verbose=False, access_rights=0o755):
        self.file_path = file_path
        self.verbose = verbose
        self.access_rights = access_rights
        self._set_path()
        self._set_temp_dir()
        self._unzip_file()

    def _set_path(self):
        self.path = os.path.join(tempfile.gettempdir(), 'snr/')

    def _set_temp_dir(self):
        if not os.path.exists(self.path):
            try:
                if self.verbose:
                    print(Msg.CREATE(self.path))
                os.mkdir(self.path, self.access_rights)
            except OSError:
                print(Msg.HEADER)
                print("Creation of the directory %s failed" % self.path)
                exit()
        else:
            for filename in os.listdir(self.path):
                file_path = os.path.join(self.path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except OSError as e:
                    print(Msg.HEADER)
                    print('Failed to delete %s, because of %s' % (file_path, e))
                    exit()

    def _unzip_file(self):
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                if self.verbose:
                    print(Msg.ZIP_EXTRACT(self.file_path, self.path))
                zip_ref.extractall(self.path)
        except IsADirectoryError as e:
            print(Msg.HEADER)
            print(Msg.ERR_INVALID_PATH)
            exit()

    def get_toc_file(self):
        toc_path = None
        for path in Path(self.path).rglob('*.ncx'):
            toc_path = path
            break
        if toc_path is None:
            print(Msg.HEADER)
            print(Msg.ERR_TOC_NOT_FOUND)
            exit()
        return str(path)

    def get_content_file(self):
        content_path = None
        for path in Path(self.path).rglob('*.opf'):
            content_path = path
            break
        if content_path is None:
            print(Msg.HEADER)
            print(Msg.ERR_CONTENT_NOT_FOUND)
            exit()
        return str(path)

    def get_directory_path(self, toc_path):
        return toc_path[:toc_path.rfind('/')]
