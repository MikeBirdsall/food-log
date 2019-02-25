#!/usr/bin/python3
"""
Program to edit a food item

This cgi-bin program is one of a group of programs to help me create and
maintain a record of everything I eat. This one writes and populates an html
form page which allows the food item fields be edited

Other programs will input new data, prepare output web pages, and to managed
the date in valious ways.

"""
import cgitb; cgitb.enable() # pylint: disable=C0321
import sys
import os
import sqlite3
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from foodlog.my_info import config_path
from foodlog.entry_form import EntryForm
from foodlog.templates import (IMAGE_TEMPLATE, WITHOUT_EDIT_CSS, WITH_EDIT_CSS,
    INVALID_TEMPLATE)

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')

TEMPLATE_REQUIRED = frozenset('description calories fat protein carbs'.split())
UPDATE_FIELDS = frozenset('description comment size calories number carbs '
    'protein fat servings day time meal'.split())
VALID = UPDATE_FIELDS.union('id ini_id action'.split())
config = config_path() # pylint: disable=invalid-name
DB_FILE = config.dir('DB_FILE')
THUMB_URL = config.dir('THUMB_URL')
LOG_FILENAME = config.dir('DB_LOG')

IGNORE = frozenset('template cmd'.split())

def print_error(header, text):
    print(INVALID_TEMPLATE.format(header, text))
    sys.exit(0)

def get_args(form):
    params = set(form.keys())
    if not ("id" in params or "ini_id" in params):
        raise RuntimeError("No Input")

    params = params - IGNORE
    invalid = params - VALID
    valid = params - invalid
    if invalid:
        print_error("Invalid parameters:", invalid)

    return {key: form.getfirst(key) for key in valid}


class Edit:
    """ Main program do create and handle form to edit food items """

    def __init__(self, form, user):
        if not DB_FILE or ";" in DB_FILE:
            print_error("PROBLEM WITH DATABASE", DB_FILE)

        args = get_args(form)

        self.old_data = dict()
        self.data = args

        self.log_file = None
        self.cursor = None
        self.Process(DB_FILE, user)

    def Process(self, database, user):
        """ If form filled, update database. In either case (re)draw form """
        self.page_content = {}

        with open(LOG_FILENAME, "a") as self.log_file:
            with sqlite3.connect(database) as conn:
                conn.row_factory = sqlite3.Row
                self.cursor = conn.cursor()

                tmp = self.load_record()
                self.old_data = {key: "" if tmp[key] is None
                    else str(tmp[key]) for key in tmp}
                self.process_data()

    def process_data(self):

        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)

        if 'action' not in self.data:
            status = "Ready to Edit"
        elif self.data['action'] == 'Update':
            status = self.update()
        elif self.data['action'] == 'Copy':
            status = self.copy()
            return
        elif self.data['action'] == 'Make Template':
            status = self.make_template()
        elif self.data['action'] == 'Delete':
            status = self.delete()
            template = env.get_template('mealdetail.html')
            input_ = dict(
                SCRIPT_NAME=SCRIPT_NAME,
                STATUS=status,
                title="Deleted Course Display",
                h1="Deleted Food Entry",
                EDIT_CSS=WITHOUT_EDIT_CSS,
                disabled="disabled",
                **self.old_data)
            output = template.render(input_)
            print(output)
            return

        else:
            status = "Invalid button %s" % self.data['action']

        # If a picture, display
        thumb_id = self.old_data['thumb_id']
        if thumb_id:
            image = IMAGE_TEMPLATE % os.path.join(THUMB_URL,
                                                  thumb_id + ".jpg")
        else:
            image = ''

        template = env.get_template('editdetail.html')

        input_ = dict(
            SCRIPT_NAME=SCRIPT_NAME,
            STATUS=status,
            IMAGE=image,
            title="Edit Course Detail",
            h1="Edit Food Entry",
            EDIT_CSS=WITH_EDIT_CSS,
            disabled="",
            **self.old_data)
        output = template.render(input_)

        print(output)

    def make_template(self):
        """ Create a template database entry """

        missing = TEMPLATE_REQUIRED.difference(self.data)
        if missing:
            return ("<h3>Template must have %s filled in.</h3>" %
                ', '.join(missing))

        # Write a database entry
        xline = """insert into template
            (description, comment, calories, fat, protein, carbs, size)
            values (?, ?, ?, ?, ?, ?, ?)"""
        xparms = tuple(self.data.get(x, '') for x in """description comment
            calories fat protein carbs size""".split())

        self.cursor.execute(xline, xparms)
        print(dict(command=xline, args=xparms), file=self.log_file)

        return "<h3>Template created at %s</h3>" % (
            datetime.now().time().strftime("%I:%M:%S %p"))


    def delete(self):
        """ Delete record from database, write deleted entry in log """
        # Write deleted entry into log
        print("Delete", self.old_data, file=self.log_file)

        # Write comment about how to restore it
        print("#Replace with:", file=self.log_file)
        print("#Insert into course ",
            str(tuple(self.old_data.keys())).translate({ord("'"): None}),
            "VALUES ",
            str(tuple(self.old_data.values())),
            file=self.log_file)
        line = "Delete from course where id = %s" % (self.data['id'])
        self.cursor.execute(line)
        return ("<p>Entry deleted at %s</p>" %
            datetime.now().time().strftime("%I:%M:%S %p"))

    def copy(self):
        # pull defaults from self
        copied = {key:self.data.get(key, '') for key in
            'description comment size calories carbs fat protein'.split()}
        form = EntryForm()
        form.create_form(copied, script=SCRIPT_NAME, status="Unsubmitted Form")
        if form.status:
            return form.status
        print(form.page)


    def update(self):
        """ Update fields in database and write mysql in log """
        status = "<p>Not yet updated</p>"
        needed = UPDATE_FIELDS.intersection(self.data)
        needed = [key for key in needed if self.old_data[key] != self.data[key]]
        if needed:
            args = tuple(str(self.data[x]) for x in needed)
            updates = ', '.join("%s = ?" % x for x in needed)

            line = "UPDATE course set %s where id = %s" % (updates,
                self.data['id'])

            # Want to self.cursor.execute(xline, *needed stuff)
            # Want to print lline % * needed stuff
            self.cursor.execute(line, args)
            print(dict(command=line, args=args), file=self.log_file)

            # Update the data to reflect changes
            self.old_data.update({k: self.data.get(k) for k in needed})

            status = ("<p>Dish  updated at %s</p>" %
                datetime.now().time().strftime("%-I:%M:%S %p"))

        return status

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

