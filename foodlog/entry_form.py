""" Module for handling Food Log entry form created by copy or copy_template

"""

from jinja2 import Environment, FileSystemLoader
from foodlog.my_info import config_path
from foodlog.templates import TEMPLATE, WITH_EDIT_CSS


FIELDS = 'description comment size calories carbs fat protein'.split()

class EntryForm:
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
        values['STATUS'] = status
        # values['script'] = script
        values['title'] = "Enter Course"
        values['h1'] = "Food Entry"
        # values['MENU_URL'] = config_path().dir('MENU_URL')
        values['EDIT_CSS'] = WITH_EDIT_CSS
        # self.page = TEMPLATE.format(**values)

        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        template = env.get_template('foodentry.html')
        self.page=template.render(values)



