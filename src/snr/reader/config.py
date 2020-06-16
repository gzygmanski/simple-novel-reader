#!/usr/bin/env python3

import os
import appdirs
import snr.constants.messages as Msg

class Config:
    def __init__(self, verbose=False, access_rights=0o755):
        self.verbose = verbose
        self.access_rights = access_rights
        self._set_config_dir()

    def _set_config_dir(self):
        self.config_dir = appdirs.user_config_dir('snr')
        if not os.path.exists(self.config_dir):
            try:
                if self.verbose:
                    print(Msg.CREATE(self.config_dir))
                os.mkdir(self.config_dir, self.access_rights)
            except OSError:
                print ("Creation of the directory %s failed" % self.config_dir)
