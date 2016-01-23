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
import os, sys
from ConfigParser import SafeConfigParser
from datetime import datetime

ROOT_DIR = "/home/mbirdsall/food/"
#ROOT_DIR = "/big/dom/xkirkbird/"
DATA_DIR = ROOT_DIR + "www/and/images/byday/"
THUMB_DIR = ROOT_DIR + "www/and/images/thumbs"
THUMB_URL = "/and/images/thumbs/"
SELF_URL = "http://localhost:8000/cgi-bin/edit.py"
#SELF_URL = "http://kirkbird.com/cgi-bin/food/edit.py"

update_fields = frozenset('description comment size calories number carbs '
    'protein fat servings day time meal'.split())
valid_fields = frozenset('cmd id description comment size calories number carbs '
    'protein fat servings day time meal'.split())

class main():
    def __init__(self):
        self.old_data = dict()
        pass

    def process(self):
        """ Update file from form or update form from file depending on state """

        self.head()

        self.data = self.get_form_data()

        self.parser = self.open_ini_file(self.data['id'])


        """
        # Getting debug information to find out how to deal with no form or form
        print "<p>%s</p>" % datetime.now().time()
        print "<p>%s</p>" % self.data

        # Show that it comes from CGI
        if 'GATEWAY_INTERFACE' in os.environ:
            print '<p>CGI - %s</p>' % os.environ['GATEWAY_INTERFACE']
        else:
            print "Not CGI. CLI?"

        fs = cgi.FieldStorage()
        for key in fs.keys():
            print "%s - %s<br/>" % (key, fs[key].value)

        for field in sorted(os.environ):
            print "%s = %s<br/>" % (field, os.environ[field])
        """

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
        status = "<p>Not yet updated</p>"
        needed = update_fields.intersection(self.data)
        if needed:
            EDIT_SECTION = 'edit'
            for field in needed:
                self.parser.set(EDIT_SECTION, field, self.data[field])

            self.ini.seek(0, 0)
            self.parser.write(self.ini)
            status = "<p>File updated at %s</p>" % datetime.now().time()

        self.ini.close()
        return status

    def show_image(self, image):
        print """<img src="%s" alt="Food">""" % image

    def tail(self):
        print """</body></html>"""

    def load_data(self):
        for option in self.parser.options('edit'):
            self.old_data[option] = self.parser.get('edit', option) or ""

    def body(self):
        print """<body>"""

        data = self.load_data()

        self.print_form()

    def print_form(self):
        print """    <h1>Food Entry</h1>
           <form method="post" enctype="multipart/form-data" action="%s">
        <input type="submit"><br> """ % SELF_URL

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
            raise RuntimeError, "No Input"

        # Don't allow extra fields - protection against misspelling
        invalid_fields = set(fs.keys()).difference(valid_fields)
        if invalid_fields:
            raise RuntimeError, "Bad field names %s" % invalid_fields

        return dict((x, fs.getfirst(x)) for x in fs)

    def open_ini_file(self, id):
        # Check id is valid format and file exists and readable
        upload_second = datetime.strptime(id, "%Y%m%dT%H:%M:%S")
        ini_loc = os.path.join(DATA_DIR, id + '.ini')
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

