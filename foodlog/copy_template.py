#!/usr/bin/python3
"""
Program to create course entry based on a template

This cgi-bin program is one of a group of programs to help me create and
maintain a record of everything I eat. This one writes an html which is a list
of every template as a button, which will create an entry form pre-populated
with the values from the template.

"""
import os
import sys
import cgitb; cgitb.enable() # pylint: disable=multiple-statements
import sqlite3
from jinja2 import Environment, FileSystemLoader
from foodlog.my_info import config_path
from foodlog.entry_form import EntryForm
from foodlog.templates import (INVALID_TEMPLATE)

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')

config = config_path() # pylint: disable=invalid-name
DB_FILE = config.dir('DB_FILE')

IGNORE = frozenset('template cmd'.split())
VALID = frozenset('id'.split())

def print_error(header, text):
    print(INVALID_TEMPLATE.format(header, text))
    sys.exit(0)

def get_args(form):
    """ Check and report invalid form input, return dict of valid parameters """
    params = set(form.keys())
    params = params - IGNORE
    invalid = params - VALID
    valid = params - invalid
    if invalid:
        print_error("Invalid parameters:", invalid)

    return {key: form.getfirst(key) for key in valid}


class CopyTemplate:
    """ Manage form for creating defaulted entry from template """

    def __init__(self, form, user):
        if not DB_FILE or ";" in DB_FILE:
            print_error("PROBLEM WITH DATABASE", DB_FILE)

        args = get_args(form)

        self.run(args.get('id'))

    def run(self, template_id):
        if template_id:
            status = self.form_entry(template_id)
            if not status:
                return
            print("""<p3>%s</p3>""" % status)
        self.create_selection()

    def form_entry(self, template_id):
        """ Print an entry form with default values from template """

        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                'select * from template where id = ?',
                (template_id, ))
            row = cursor.fetchone()

        if not row:
            return "No Template for id %s" % template_id
        form = EntryForm()
        form.create_form(row, script=SCRIPT_NAME)
        print(form.page)

        return None

    def create_selection(self):
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            rows = cursor.execute('select * from template').fetchall()
            rows = [
                dict(id=x['id'], description=x['description']) for x in rows
            ]

        input_ = dict(
            title="Create Course From Template",
            h1="Choose Template",
            templates=rows)

        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        template = env.get_template('picktemplate.html')

        output = template.render(input_)

        print(output)
