#!/usr/bin/python
""" Program to test things about the cgi-bin environment

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


class main():
    def __init__(self):
        pass

    def process(self):
        """ Update file from form or update form from file depending on state """

        self.head()  # Need before any output

        print "<p>Python path"
        for path in sys.path:
            print path, "<br/>"
        print "</p>"

        print "<p>%s</p>" % datetime.now().time()

        fs = cgi.FieldStorage()

        print "<p>%s</p>" % dict((x, fs.getfirst(x)) for x in fs)


        # Show if it comes from CGI
        if 'GATEWAY_INTERFACE' in os.environ:
            print '<p>CGI - %s</p>' % os.environ['GATEWAY_INTERFACE']
        else:
            print "Not CGI. CLI?"

        for field in sorted(os.environ):
            print "%s = %s<br/>" % (field, os.environ[field])

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

    def head(self):
        print """Content-Type: text/html\n\n<html>\n    <head>
        <meta name="viewport" content="width=320" />\n"""
        print """ </head>
            """

if __name__ == '__main__':
    main().process()

