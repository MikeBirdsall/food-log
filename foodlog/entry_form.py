""" Module for handling Food Log entry form

"""

from my_info import config_path
from templates import TEMPLATE


FIELDS = 'description comment size calories carbs fat protein'.split()

class EntryForm(object):
    """ Create an entry form HTML page with possible defaults values """

    def __init__(self):
        self.status = ""  # String containing error message if needed
        self.page = ""    # String with the HTML page

    def create_form(self, defaults, script, status=""):
        values = dict()
        for field in FIELDS:
            if field in defaults.keys() and defaults[field] is not None:
                values[field] = """value="%s" """ % defaults[field]
            else:
                values[field] = ""
        values['status'] = status
        values['script'] = script
        values['MENU_URL'] = config_path().dir('MENU_URL')
        self.page = TEMPLATE.format(**values)



