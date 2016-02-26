#!/usr/bin/python
from  ConfigParser import ConfigParser
import os, sys

class config_path(object):
    def __init__(self):

        self.config = config = ConfigParser()
        config.read(self.config_file())


    def config_file(self):
        if 'GATEWAY_INTERFACE' in os.environ and 'SCRIPT_FILENAME' in os.environ:
            script_path = os.environ.get('SCRIPT_FILENAME', '')
        else:
            # Allow it to be run from command-line, as well
            script_path = os.path.abspath(sys.argv[0])

        return os.path.join(os.path.dirname(script_path), 'foodlog.cfg')

    def dir(self, which):
        return self.config.get('paths', which)

if __name__ == '__main__':
    if 'GATEWAY_INTERFACE' in os.environ:
        print """Content-Type: text/plain\n\n"""
        print "argv[0]", sys.argv[0]
        print "empty path", os.path.dirname("")
        print "-", os.path.join(os.path.dirname(""), "foodlog.cfg")


        for x in sorted(os.environ.keys()):
            print x, os.environ.get(x, "Unset")
        print

    z = config_path()

    if 'GATEWAY_INTERFACE' in os.environ:
        for x in ('ROOT_DIR DATA_DIR THUMB_DIR THUMB_URL UPLOAD_DIR '
                 ' ARCHIVE_DIR').split():
            print x, z.dir(x)
