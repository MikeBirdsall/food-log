#!/usr/bin/python3
"""
Program to display a food item - based on Edit with edit not allowed

This cgi-bin program is one of a group of programs to help me create and
maintain a record of everything I eat. This one writes and populates an html
form page which allows the food item fields be edited

Other programs will input new data, prepare output web pages, and to managed
the date in valious ways.

"""
import cgi
import cgitb; cgitb.enable() # pylint: disable=C0321
import os
import sqlite3
from my_info import config_path
from templates import FORM_TOP_TEMPLATE, IMAGE_TEMPLATE, NO_BUTTON_BAR

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')

TEMPLATE_REQUIRED = frozenset('description calories fat protein carbs'.split())
UPDATE_FIELDS = frozenset('description comment size calories number carbs '
    'protein fat servings day time meal'.split())
VALID_FIELDS = UPDATE_FIELDS.union('id ini_id action'.split())

class EditCourse(object):
    """ Main program do create and handle form to edit food items """
    def __init__(self):
        self.old_data = dict()
        self.parser = None
        self.data = dict()
        self.ini_filename = ""

        config = config_path()
        self.menu_url = config.dir('VIEW_MENU_URL')
        self.thumb_dir = config.dir('THUMB_DIR')
        self.thumb_url = config.dir('THUMB_URL')
        self.db_file = config.dir('DB_FILE')
        self.cursor = None

    def process(self):
        """ If form filled, update database. In either case (re)draw form """

        self.data = self.get_form_data()
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            self.cursor = conn.cursor()

            tmp = self.load_record()
            self.old_data = {key: "" if tmp[key] is None
                else str(tmp[key]) for key in tmp}
            self.process_data()

    def process_data(self):

        if 'action' not in self.data:
            status = "------------"
        else:
            status = "Invalid button %s" % self.data['action']

        # If a picture, display
        thumb_id = self.old_data['thumb_id']
        if thumb_id:
            image = IMAGE_TEMPLATE % os.path.join(self.thumb_url,
                                                  thumb_id + ".jpg")
        else:
            image = ''

        print(FORM_TOP_TEMPLATE.format(
                MENU_URL=self.menu_url,
                SCRIPT_NAME=SCRIPT_NAME,
                STATUS=status,
                IMAGE=image,
                TITLE="View Course Info",
                h1="Food Entry",
                BUTTON_BAR=NO_BUTTON_BAR,
                DELETE_BAR=NO_BUTTON_BAR,
                **self.old_data)
        )


    def load_record(self):
        if 'id' in self.data:
            self.cursor.execute('SELECT * from course where id = ?',
                (self.data['id'],))
        elif 'ini_id' in self.data:
            self.cursor.execute('SELECT * from course where ini_id = ?',
                (self.data['ini_id'],))
        else:
            raise RuntimeError('No record selected')

        answer = self.cursor.fetchone()
        if not answer:
            raise RuntimeError('Record not found')

        return dict(answer)

    def get_form_data(self):

        fs = cgi.FieldStorage()

        # We need identity of record we are editing; either "id" or "ini_id"
        if not (fs.keys() and ("id" in fs or "ini_id" in fs)):
            raise RuntimeError("No Input")

        # Don't allow extra fields - protection against misspelling
        invalid_fields = set(fs.keys()).difference(VALID_FIELDS)
        if invalid_fields:
            raise RuntimeError("Bad field names %s" % invalid_fields)

        return dict((x, fs.getfirst(x)) for x in fs)

if __name__ == '__main__':
    EditCourse().process()

