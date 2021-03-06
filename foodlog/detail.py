#!/usr/bin/python3
"""
Program to display a food item - based on Edit with edit not allowed

This cgi-bin program is one of a group of programs to help me create and
maintain a record of everything I eat. This one writes and populates an html
form page which allows the food item fields be edited

Other programs will input new data, prepare output web pages, and to managed
the date in valious ways.

"""
import cgitb; cgitb.enable() # pylint: disable=C0321
import os
import sys
import sqlite3
from jinja2 import Environment, FileSystemLoader
from foodlog.my_info import config_path

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')

UPDATE_FIELDS = frozenset('description comment size calories number carbs '
    'protein fat servings day time meal'.split())
VALID = frozenset('id action dieter'.split())

config = config_path() # pylint: disable=invalid-name
THUMB_DIR = config.dir('THUMB_DIR')
THUMB_URL = config.dir('THUMB_URL')
DB_FILE = config.dir('DB_FILE')

IGNORE = frozenset('template cmd jinjatemplate'.split())

def print_error(header, text):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('invalid.html')
    print(template.render(dict(h1=header, text=text)))
    sys.exit(0)

def get_args(form):
    params = set(form.keys())
    if "id" not in params:
        raise RuntimeError("No Input")

    params = params - IGNORE
    invalid = params - VALID
    valid = params - invalid
    if invalid:
        print_error("Invalid parameters:", invalid)

    return {key: form.getfirst(key) for key in valid}


class ViewCourse:
    """ Main program to create and handle form to view food items """
    def __init__(self, form, user):
        if not DB_FILE or ";" in DB_FILE:
            print_error("PROBLEM WITH DATABASE", DB_FILE)

        self.data = get_args(form)
        self.old_data = dict()

        self.cursor = None
        self.Process(DB_FILE, user, self.data['id'])

    def Process(self, database, user, record_id):
        """ draw form """

        with sqlite3.connect(database) as conn:
            conn.row_factory = sqlite3.Row
            self.cursor = conn.cursor()

            tmp = self.load_record(record_id)
            self.old_data = {key: "" if tmp[key] is None
                else str(tmp[key]) for key in tmp}
            self.process_data()

    def process_data(self):

        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)

        if 'action' not in self.data:
            status = "------------"
        else:
            status = "Invalid button %s" % self.data['action']

        # If a picture, display
        thumb_id = self.old_data['thumb_id']
        image = os.path.join(THUMB_URL, thumb_id + ".jpg") if thumb_id else ''

        template = env.get_template('mealdetail.html')

        input_ = dict(
            SCRIPT_NAME=SCRIPT_NAME,
            STATUS=status,
            IMAGE=image,
            title="View Course Detail",
            h1="View Food Entry",
            EDIT_CSS=False,
            disabled="disabled",
            **self.old_data)
        output = template.render(input_)

        print(output)

    def load_record(self, record_id):
        self.cursor.execute('SELECT * from course where id = ?', (record_id,))

        answer = self.cursor.fetchone()
        if not answer:
            raise RuntimeError('Record not found')

        return dict(answer)

