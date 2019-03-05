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
from jinja2 import Environment, FileSystemLoader

from foodlog.my_info import config_path
from foodlog.search_engine import TextSearchEngine

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')
SCRIPT_NAME = os.path.join(os.path.dirname(SCRIPT_NAME), "form.py")

config = config_path() # pylint: disable=invalid-name
DB_FILE = config.dir('DB_FILE')

IGNORE = frozenset('template cmd jinjatemplate'.split())
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

def spacenone(value):
    return "" if value is None else str(value)

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

def print_error(header, text):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('invalid.html')
    print(template.render(dict(h1=header, text=text)))
    sys.exit(0)

def get_args(form):
    params = set(form.keys())

    params = params - IGNORE
    invalid = params - VALID
    valid = params - invalid
    if invalid:
        print_error("Invalid parameters:", invalid)

    return {key: form.getfirst(key) for key in valid}

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
        answer['description'] = dish.description
        for field in "calories carbs fat protein".split():
            answer[field] = safe_int(getattr(dish, field, None))
        for field in "comment size".split():
            answer[field] = getattr(dish, field, "")
        answer['score'] = score
        answer['id'] = dish.id

        return answer

    def search(self, searchstring):
        try:
            return TextSearchEngine(DB_FILE, searchstring).results()
        except OperationalError as e:
            self.status = e
            return list()

    def form_entry(self, searchstring, user):
        """ Print a form with courses from search results """

        results = []
        course = None
        for course, score in self.search(searchstring)[:19]:
            substitutions = self.course_dict(course, score)
            results.append(substitutions)
        if self.status:
            return
        if not course:
            self.status = "No Results for search %s" % searchstring
            return

        input_ = dict(
            title="Search for Courses",
            h1="Full Text Search: {}".format(searchstring),
            results=results
        )

        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        env.filters['spacenone'] = spacenone
        template = env.get_template('searchresult.html')
        output = template.render(input_)
        print(output)
        return

    def create_search_form(self):
        input_ = dict(
            TITLE="Search for Courses",
            h1="Full Text Search",
            status=(self.status or "Ready For Search"),
            cheatsheet=CHEATSHEET,
            EDIT_CSS=True
        )
        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        env.filters['spacenone'] = spacenone
        template = env.get_template('search.html')
        output = template.render(input_)
        print(output)
        return

