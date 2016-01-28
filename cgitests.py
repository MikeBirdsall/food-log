#!/usr/bin/python
""" Program to test things about the cgi-bin environment

"""
import cgi
import cgitb; cgitb.enable()
import os, sys
from ConfigParser import SafeConfigParser
from datetime import datetime
import my_info


class main():
    def __init__(self):
        pass

    def process(self):
        """ Update file from form or update form from file depending on state """

        self.head()  # Need before any output

        print "<p>Python path"
        for path in sys.path:
            print path, "<br/>"
        print "</p>"

        print "<p>Time = %s</p>" % datetime.now().time()

        fs = cgi.FieldStorage()

        print "<p>Form Fields: %s</p>" % dict((x, fs.getfirst(x)) for x in fs)


        # Show if it comes from CGI
        if 'GATEWAY_INTERFACE' in os.environ:
            print '<p>CGI - %s</p>' % os.environ['GATEWAY_INTERFACE']
        else:
            print "Not CGI. CLI?"

        print "<p>Environment Values</p>"
        for field in sorted(os.environ):
            print "%s = %s<br/>" % (field, os.environ[field])

        self.tail()
           
    def tail(self):
        print """</body></html>"""

    def head(self):
        print """Content-Type: text/html\n\n<html>\n    <head>
        <meta name="viewport" content="width=device=width, initial-scale=1" />\n"""
        print """ </head>
            """

if __name__ == '__main__':
    main().process()

