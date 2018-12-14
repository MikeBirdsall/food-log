#!/usr/bin/python3
from configparser import ConfigParser
hack=False

import os
import sys
from appdirs import user_data_dir

class config_path:
    def __init__(self):

        self.config = config = ConfigParser(inline_comment_prefixes=(';',))
        config.read(self.config_file())


    def config_file(self):
        path = user_data_dir("foodlog", "MGB")

        return os.path.join(path, 'foodlog.cfg')

    def dir(self, which):
        return self.config.get('paths', which)

