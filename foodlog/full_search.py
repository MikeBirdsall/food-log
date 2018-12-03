#!/usr/bin/python3
"""
Program to lookup courses (items) based on a full text search of all existing
items.

This cgi-bin program is one of a group of programs to help me create and
maintain a record of everything I eat. This one writes an html which is a list
of results from a full text search as a clickable row of its values,
which will allow editing it.

"""
import cgi
import cgitb
cgitb.enable()
import os
from my_info import config_path
from templates import (SEARCH_TEMPLATE, SEARCH_COURSE_TEMPLATE, WITH_EDIT_CSS,
    SEARCH_HEAD_TEMPLATE, TABLE_TAIL_TEMPLATE)
from search_engine import TextSearchEngine

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')
SCRIPT_NAME = os.path.join(os.path.dirname(SCRIPT_NAME), "form.py")

config = config_path()
DB_FILE = config.dir('DB_FILE')
MENU_URL = config.dir('MENU_URL')

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

def edit_url(dish):
    """ Return link to edit for dish """

    label = ellipse_truncate(dish.description, default="No Description Yet")
    return '<a href="./edit.py?id={id}">{label}</a>'.format(
        label=label, id=dish.id
    )

class FullTextSearch(object):
    def __init__(self):
        self.form = cgi.FieldStorage()

    def run(self):
        if self.form.keys():
            status = self.form_entry()
            if not status:
                return
            print("""<p3>%s</p3>""" % status)
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

    def form_entry(self):
        """ Print a form with courses from search results """
        searchstring = self.form['searchstring'].value

        print(SEARCH_HEAD_TEMPLATE.format(
            TITLE="Search for Courses",
            MENU_URL=MENU_URL,
            EDIT_CSS=WITH_EDIT_CSS,
            h1="Full Text Search")
        )

        course = None

        for course, score in TextSearchEngine(DB_FILE, searchstring).results()[:19]:
            substitutions = self.course_dict(course, score)
            print(SEARCH_COURSE_TEMPLATE.format(**substitutions))

        if not course:
            return "No Results for search %s" % searchstring
        else:
            print(TABLE_TAIL_TEMPLATE.format(MENU_URL=MENU_URL))
            return

    def create_search_form(self):
        print(SEARCH_TEMPLATE.format(
            MENU_URL=MENU_URL,
            TITLE="Search for Courses",
            h1="Full Text Search",
            EDIT_CSS=WITH_EDIT_CSS
            ))

if __name__ == '__main__':
    FullTextSearch().run()
