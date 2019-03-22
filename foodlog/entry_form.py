""" Module for handling Food Log entry form created by copy or copy_template

"""

import os
from jinja2 import Environment, FileSystemLoader
from foodlog import COPY_FIELDS

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')

class EntryForm:
    """ Create an entry form HTML page with possible defaults values """

    def __init__(self):
        self.status = ""  # String containing error message if needed
        self.page = ""    # String with the HTML page

    def create_form(self, defaults, status=""):
        values = dict()
        for field in COPY_FIELDS:
            if field in defaults.keys() and defaults[field] is not None:
                values[field] = "%s" % defaults[field]
        if "IMAGE" in defaults:
            values['IMAGE'] = defaults['IMAGE']

        values['STATUS'] = status
        values['title'] = "Enter Course"
        values['h1'] = "Food Entry"
        values['EDIT_CSS'] = True
        values['SCRIPT_NAME'] = SCRIPT_NAME

        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        template = env.get_template('foodentry.html')
        self.page = template.render(values)



