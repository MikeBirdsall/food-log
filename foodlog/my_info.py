#!/usr/bin/python3
""" Manages the configuration file for the foodlog application.
  
    I used to store the config file in a directory determined by appdirs.user_data_dir()
    but that only allows me a single configuration file for a particular web app.
    I'd like to have development, test, production, and guest instances, each with their 
    own configuration. Each of those environments will be available at a different URL, 
    effectively a directory with it's own index.html and .htaccess files. So, I'm going to 
    keep the configuration file there as well, which means it's going to be in the 
    current working directory when the application is run.

"""

from configparser import ConfigParser
from os import getcwd

import os
from appdirs import user_data_dir

class config_path:
    def __init__(self):

        self.config = config = ConfigParser(inline_comment_prefixes=(';',))
        config.read(self.config_file())


    def config_file(self):
        # path = user_data_dir("foodlog", "MGB")
        path = os.getcwd()

        return os.path.join(path, 'foodlog.cfg')

    def dir(self, which):
        return self.config.get('paths', which)

