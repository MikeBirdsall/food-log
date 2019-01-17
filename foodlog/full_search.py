#!/usr/bin/python3
"""
Program to lookup courses (items) based on a full text search of all existing
items.

This cgi-bin program is one of a group of programs to help me create and
maintain a record of everything I eat. This one writes an html which is a list
of results from a full text search as a clickable row of its values,
which will allow editing it.

"""
import cgitb
cgitb.enable()
import os
import sys
from sqlite3 import OperationalError

from foodlog.my_info import config_path
from foodlog.templates import (SEARCH_TEMPLATE, SEARCH_COURSE_TEMPLATE,
    WITH_EDIT_CSS, SEARCH_HEAD_TEMPLATE, TABLE_TAIL_TEMPLATE, INVALID_TEMPLATE)
from foodlog.search_engine import TextSearchEngine

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')
SCRIPT_NAME = os.path.join(os.path.dirname(SCRIPT_NAME), "form.py")

config = config_path() # pylint: disable=invalid-name
DB_FILE = config.dir('DB_FILE')

IGNORE = set('template cmd'.split())
VALID = frozenset('searchstring'.split())

CHEATSHEET = """
<p>Examples:</p>
<ul>
  <li>salad</li>
  <li>egg*</li>
  <li>egg* sand*</li>
  <li>ste* NEAR/3 ric*</li>
  <li>steak OR roast</li>
  <li>steak NOT shake</li>
  <li>ste* NOT shake</li>
</ul>
"""
def safe_int(val):
    if val is None or val == '':
        return ''
    if isinstance(val, str):
        try:
            val = float(val)
        except ValueError:
            return val
    if isinstance(val, int):
        return "{:n}".format(val)
    if isinstance(val, float):
        return "{:.1f}".format(val).rstrip('0').rstrip('.')
    return val

def ellipse_truncate(text, length=30, default=""):
    "Return canonical form of description to fit in length """
    result = text or default
    return (result[:length-1] + "&hellip;") if len(result) > length else result

def print_error(header, text):
    print(INVALID_TEMPLATE.format(header, text))
    sys.exit(0)

def get_args(form):
    params = set(form.keys())

    params = params - IGNORE
    invalid = params - VALID
    valid = params - invalid
    if invalid:
        print_error("Invalid parameters:", invalid)

    return {key: form.getfirst(key) for key in valid}

def edit_url(dish):
    """ Return link to edit for dish """

    label = ellipse_truncate(dish.description, default="No Description Yet")
    return '<a href="run.py?cmd=edit&id={id}">{label}</a>'.format(
        label=label, id=dish.id
    )

class FullTextSearch:
    def __init__(self, form, user):

        if not DB_FILE or ";" in DB_FILE:
            print_error("PROBLEM WITH DATABASE", DB_FILE)

        self.status = None
        args = get_args(form)

        self.run(args.get('searchstring'), user)

    def run(self, searchstring, user):
        self.status = None
        if searchstring:
            self.form_entry(searchstring, user)
            if not self.status:
                return
        self.create_search_form()


    def course_dict(self, dish, score):
        answer = dict()
        answer['description'] = edit_url(dish)
        for field in "calories carbs fat protein".split():
            answer[field] = safe_int(getattr(dish, field, None))
        for field in "comment size".split():
            answer[field] = ellipse_truncate(
                getattr(dish, field, ""),
                length=20)
        answer['score'] = score

        return answer

    def search(self, searchstring):
        try:
            return TextSearchEngine(DB_FILE, searchstring).results()
        except OperationalError as e:
            self.status = e
            return list()

    def form_entry(self, searchstring, user):
        """ Print a form with courses from search results """

        page_content = []

        page_content.append(SEARCH_HEAD_TEMPLATE.format(
            TITLE="Search for Courses",
            EDIT_CSS=WITH_EDIT_CSS,
            h1="Full Text Search: {}".format(searchstring))
        )

        course = None

        for course, score in self.search(searchstring)[:19]:
            substitutions = self.course_dict(course, score)
            page_content.append(
                SEARCH_COURSE_TEMPLATE.format(**substitutions)
            )

        if self.status:
            return
        if not course:
            self.status = "No Results for search %s" % searchstring
            return
        else:
            page_content.append(TABLE_TAIL_TEMPLATE)
            for chunk in page_content:
                print(chunk)
            return

    def create_search_form(self):
        print(SEARCH_TEMPLATE.format(
            TITLE="Search for Courses",
            h1="Full Text Search",
            status=(self.status or "Ready For Search"),
            cheatsheet=CHEATSHEET,
            EDIT_CSS=WITH_EDIT_CSS
            ))

