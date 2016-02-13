#!/usr/bin/python
"""
Program to create course entry based on a template

This cgi-bin program is one of a group of programs to help me create and
maintain a record of everything I eat. This one writes an html which is a list
of every template as a button, which will create an entry form pre-populated
with the values from the template.

"""
import cgi
import cgitb; cgitb.enable()
import os, sys
import sqlite3
from my_info import config_path
from entry_form import EntryForm

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')
SCRIPT_NAME = os.path.join(os.path.dirname(SCRIPT_NAME), "form.py")

HEAD_TEMPLATE = """\
Content-Type: text/html

<html>
  <head>
    <title>Create course from template</title>
    <meta name="viewport" content="width=device=width, initial-scale=1" />
    <style>
      button {
        max-width: 320px;
        width: 100%;
        background:#db8c47;
      }
    </style>
  </head>
  <body>\
"""

ROW_TEMPLATE = """\
      <button name="choice" type="submit" value=%s>%s</button><br/>\
"""

FORM_HEAD_TEMPLATE = """\
    <h1>Choose Template</h1>
    <form method="get">\
"""

FORM_TAIL_TEMPLATE = """\
    </form>\
"""

TAIL_TEMPLATE = """\
  </body>
</html>\
"""

DB_FILE = config_path().dir('DB_FILE')

class copy_template(object):
    def __init__(self):
        self.form = cgi.FieldStorage()

    def run(self):
        if self.form.keys():
            status = self.form_entry()
            if not status:
                return
            print """<p3>%s</p3>""" % status
        self.create_selection()

    def emit_button(self, row):
        print ROW_TEMPLATE % (row['id'], row['description'])

    def form_entry(self):
        """ Print an entry form with default values from template """
        template_id = self.form['choice'].value

        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('select * from template where id = ?', (template_id, ))
            row = cursor.fetchone()

        form = EntryForm()
        form.create_form(row, script=SCRIPT_NAME)
        if form.status:
            return form.status
        print form.page

    def create_selection(self):
        print HEAD_TEMPLATE
        print FORM_HEAD_TEMPLATE
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            for row in cursor.execute('select * from template'):
                self.emit_button(row)
        print FORM_TAIL_TEMPLATE
        print TAIL_TEMPLATE

if __name__ == '__main__':
    copy_template().run()
