#!/usr/bin/python
""" Program to edit a food item

This cgi-bin program is one of a group of programs to help me create and
maintain a record of everything I eat. This one writes and populates an html
form page which allows the food item fields be edited

Other programs will input new data, prepare output web pages, and to managed
the date in valious ways.

"""
import cgi
import cgitb; cgitb.enable()
import os
from ConfigParser import SafeConfigParser
from datetime import datetime
from my_info import DATA_DIR, THUMB_DIR, THUMB_URL

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')

UPDATE_FIELDS = frozenset('description comment size calories number carbs '
    'protein fat servings day time meal'.split())
VALID_FIELDS = UPDATE_FIELDS.union('id'.split())
EDIT_SECTION = 'edit'

class main(object):
    """ Main program do create and handle form to edit food items """
    def __init__(self):
        self.old_data = dict()
        self.parser = None
        self.data = dict()
        self.ini = None     # file object

    def process(self):
        """ Update file from form or vice versa depending on state """

        self.head()

        self.data = self.get_form_data()

        self.parser = self.open_ini_file(self.data['id'])

        status = self.update()

        self.body()
        print status

        # If a picture, display
        thumb_id = self.old_data['thumb_id']
        if thumb_id:
            if os.path.join(THUMB_DIR, thumb_id + ".ini"):
                self.show_image(os.path.join(THUMB_URL, thumb_id + ".jpg"))

        self.tail()

    def update(self):
        """ Update fields in ini file if any fields from form and close file """
        status = "<p>Not yet updated</p>"
        needed = UPDATE_FIELDS.intersection(self.data)
        if needed:
            for field in needed:
                self.parser.set(EDIT_SECTION, field, self.data[field])

            self.ini.seek(0, 0)
            self.parser.write(self.ini)
            status = "<p>File updated at %s</p>" % datetime.now().time()

        self.ini.close()
        return status

    def show_image(self, image):
        """ Emit html for an image link """
        print """<img src="%s" alt="Food">""" % image

    def tail(self):
        """ Emit html for constant trailing parts """
        print """</body></html>"""

    def load_data(self):
        for option in self.parser.options('edit'):
            self.old_data[option] = self.parser.get('edit', option) or ""

    def body(self):
        print """<body>"""

        self.load_data()

        self.print_form()

    def print_form(self):
        print """    <h1>Food Entry</h1>
            <form method==get">
                <button formaction="/and/images/pages/index.html">Food Menu</button>
                <button formaction="/and/images/pages/list.html">List All Meals</button>
            </form>
            <form method="post" action="%s">
        <input type="submit"><br> """ % SCRIPT_NAME

        print """
        <input type="hidden" name="id" value={id}>
        <fieldset style="width:270px"><legend>Identifying Information:</legend>
          Description:<br>
          <input type="text" name="description" placeholder="Title" value="{description}">
          <br>Comment:<br>
          <input type="text" name="comment" placeholder="Comment" value="{comment}"><br>
          Amount:<br>
          <input type="text" name="size" placeholder="Like 2 cups or large bowl" value="{size}">
        </fieldset>

        <fieldset style="width:270px">
        <legend>Nutrition:</legend>
        <label class="nutrit" for="calories">Calories:</label>
        <input class="nutrit" type="number" name="calories" id="calories" max="3000" value="{calories}">
        <label class="nutrit" for="carbs">Carbs(g):</label>
        <input class="nutrit" type="number" name="carbs" id="carbs" size="2" max="300" value="{carbs}"><br>
        <label class="nutrit" for="protein">Protein(g):</label>
        <input class="nutrit" type="number" name="protein" id="protein" size="2" max="300"
           value="{protein}"><br>
        <label class="nutrit" for="fat">Fat(g):</label>
        <input class="nutrit" type="number" name="fat" id="fat" size="2" max="300" value="{fat}">
        </fieldset>

        <fieldset style="width:270px">
        <legend>Instance Information:</legend>
        <label class="inst" for="servings">Servings:</label>
        <input class="inst" type="number" name="servings" id="servings" min="1" max="9" value="{servings}"><br>

        <label class="inst" for="day">Day:</label>
        <input class="inst" type="date" name="day" id="day" value="{day}"><br>

        <label class="inst" for="time">Time:</label>
        <input type="time" name="time" value="{time}"><br>

        <label class="inst" for="meal">Meal:</label>
        <input class="inst" list="meals" id="meal" name="meal" value="{meal}">
            <datalist id="meals">
            <option value="Breakfast">
            <option value="Lunch">
            <option value="Supper">
            <option value="Snack">
            </datalist>
        <br>
        </fieldset>
        <input type="submit"><br>
        </form>
        """.format(**self.old_data)

    def get_form_data(self):

        fs = cgi.FieldStorage()

        # Need at least "id" form field
        if not fs.keys():
            raise RuntimeError("No Input")

        # Don't allow extra fields - protection against misspelling
        invalid_fields = set(fs.keys()).difference(VALID_FIELDS)
        if invalid_fields:
            raise RuntimeError("Bad field names %s" % invalid_fields)

        return dict((x, fs.getfirst(x)) for x in fs)

    def open_ini_file(self, id_):
        # Check id is valid format and file exists and readable
        ini_loc = os.path.join(DATA_DIR, id_ + '.ini')
        try:
            self.ini = open(ini_loc, 'r+')
        except IOError:
            print "Problem opening ini file"
            raise

        parser = SafeConfigParser()
        parser.readfp(self.ini)
        return parser

    def head(self):
        print """Content-Type: text/html\n\n<html>\n    <head>
        <meta name="viewport" content="width=320" />\n"""
        self.css()
        print """ </head>
            """

    def css(self):
        print """        <style>
            form {
                width:300px;
            }

            label {
                display: inline-block;
                text-align:left;
            }

            label.nutrit {
                width:130px;
                text-align:right;
            }

            input.nutrit {
                display:inline-block;
                width:70px;
            }

            label.inst {
                width:70px;
                text-align:right;
            }

            input:inst {
                text-align:left;
            }

            input {
                display:inline-block;
                text-align:right;
            }
            fieldset {
                background:#fff7db;
            }
        </style>"""


if __name__ == '__main__':
    main().process()

