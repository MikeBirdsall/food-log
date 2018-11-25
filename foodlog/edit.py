#!/usr/bin/python
"""
Program to edit a food item

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
from datetime import datetime
from my_info import config_path
from entry_form import EntryForm
from templates import IMAGE_TEMPLATE, DELETED_TEMPLATE, EDIT_TOP_TEMPLATE

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')

TEMPLATE_REQUIRED = frozenset('description calories fat protein carbs'.split())
UPDATE_FIELDS = frozenset('description comment size calories number carbs '
    'protein fat servings day time meal'.split())
VALID_FIELDS = UPDATE_FIELDS.union('id ini_id action'.split())


class EditCourse(object):
    """ Main program do create and handle form to edit food items """
    def __init__(self):
        self.old_data = dict()
        self.data = dict()

        config = config_path()
        self.menu_url = config.dir('MENU_URL')
        self.thumb_url = config.dir('THUMB_URL')
        self.db_file = config.dir('DB_FILE')
        self.log_filename = config.dir('DB_LOG')
        self.log_file = None
        self.cursor = None

    def process(self):
        """ If form filled, update database. In either case (re)draw form """

        self.data = self.get_form_data()
        with open(self.log_filename, "a") as self.log_file:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                self.cursor = conn.cursor()

                tmp = self.load_record()
                self.old_data = {key: "" if tmp[key] is None
                    else str(tmp[key]) for key in tmp}
                self.process_data()

    def process_data(self):

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
            print EDIT_TOP_TEMPLATE.format(
                MENU_URL=self.menu_url,
                SCRIPT_NAME=SCRIPT_NAME,
                STATUS=status,
                IMAGE='',
                TITLE="Deleted Course Display",
                h1="Deleted Food Entry",
                **self.old_data
            )
            return

        else:
            status = "Invalid button %s" % self.data['action']

        # If a picture, display
        thumb_id = self.old_data['thumb_id']
        if thumb_id:
            image = IMAGE_TEMPLATE % os.path.join(self.thumb_url,
                                                  thumb_id + ".jpg")
        else:
            image = ''

        print EDIT_TOP_TEMPLATE.format(
                MENU_URL=self.menu_url,
                SCRIPT_NAME=SCRIPT_NAME,
                STATUS=status,
                IMAGE=image,
                TITLE="Edit Course Detail",
                h1="Edit Food Entry",
                **self.old_data
        )

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
        print >> self.log_file, dict(command=xline, args=xparms)

        return "<h3>Template created at %s</h3>" % (datetime.now().time().strftime("%I:%M:%S %p"))


    def delete(self):
        """ Delete record from database, write deleted entry in log """
        print >> self.log_file, "Delete", self.old_data
        print >> self.log_file, "Replace with:"
        print >> self.log_file, "#insert into course ", str(tuple(self.old_data.keys())).translate(None, "'"), "VALUES ", str(tuple(self.old_data.values()))
        line = "Delete from course where id = %s" % (self.data['id'])
        self.cursor.execute(line)
        return "<p>Entry deleted at %s</p>" % datetime.now().time().strftime("%I:%M:%S %p")

    def copy(self):
        global SCRIPT_NAME
        # pull defaults from self
        copied = {key:self.data.get(key, '') for key in
            'description comment size calories carbs fat protein'.split()}
        form = EntryForm()
        SCRIPT_NAME = os.path.join(os.path.dirname(SCRIPT_NAME), "form.py")
        form.create_form(copied, script=SCRIPT_NAME, status="Unsubmitted Form")
        if form.status:
            return form.status
        print form.page


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
            print >> self.log_file, dict(command=line, args=args)

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

