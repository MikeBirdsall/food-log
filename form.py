#!/usr/bin/python
"""
Program to load information about what I eat from an Android phone

This cgi-bin program is one of a group of programs to help me create and
maintain a record of everything I eat. This one writes an html form page
out and checks to see if it has been submitted with values. If it has (and
possible is validated) it will write out the data to files on the server.

Other programs will run to process the input data and prepare output web pages
detailing what I ate. There will be other cgi-bin programs to edit and manage
the data in various forms.

"""
import cgi
import cgitb; cgitb.enable()
import os, sys
from ConfigParser import SafeConfigParser
from datetime import datetime

UPLOAD_DIR = "/big/dom/xkirkbird/www/and/images"

class main():
    def __init__(self):
        self.fileitem = None
        self.status = ""
        self.picfile_name = None

        self.head()
        self.body()
        self.tail()

    def tail(self):
        print """    <p>%s</p>\n    </body>\n</html>
        """ % (self.status,)

    def text_out(self, message):
        self.status = message

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

    def body(self):
        print """<body>"""

        self.print_form()
        self.parse_form_fields()

    def print_form(self):
        print """    <h1>Food Entry</h1>\n    <form method="post" enctype="multipart/form-data" action="http://kirkbird.com/cgi-bin/food/form.py">
        <input type="submit"><br>

        <fieldset style="width:270px">
        <legend>Image Entry:</legend>
        <input type="file" name="pic" accept="image/*"/><br>
        </fieldset>

        <fieldset style="width:270px">
            <legend>Identifying Information:</legend>

        Description: (used as title for dish)<br> 
            <input type="text" name="description" placeholder="Title/Description/Identifier"/>
            <br>
        Comment:<br><input type="text" name="comment" placeholder="Comment/Context/Excuse">
            <br>
            Amount:<br> <input type="text" name="size" placeholder="Like 2 cups or 12 oz or large bowl">
        </fieldset>

        <fieldset style="width:270px">
        <legend>Nutrition:</legend>
        <label class="nutrit" for="calories">Calories:</label>
        <input class="nutrit" type="number" name="calories" id="calories" max="3000">
        <label class="nutrit" for="carbs">Carbs(g):</label>
        <input class="nutrit" type="number" name="carbs" id="carbs" size="2" max="300"><br>
        <label class="nutrit" for="prot">Protein(g):</label>
        <input class="nutrit" type="number" name="protein" id="prot" size="2" max="300"><br>
        <label class="nutrit" for="fat">Fat(g):</label>
        <input class="nutrit" type="number" name="fat" id="fat" size="2" max="300">
        </fieldset>

        <fieldset style="width:270px">
        <legend>Instance Information:</legend>
        <label class="inst" for="servings">Servings:</label>
        <input class="inst" type="number" name="servings" id="servings" min="1" max="9" value="1"><br>

        <label class="inst" for="day">Day:</label>
        <input class="inst" type="date" name="day" id="day"><br>

        <label class="inst" for="time">Time:</label>
        <input type="time" name="time"><br>

        <label class="inst" for="meal">Meal:</label>
        <input class="inst" list="meals" id="meal" name="meal">
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
        """

    # Meal Selections should be changed to be based on table
    # Meal selections could be radio buttons (perhaps too hard on phone

    def parse_form_fields(self):
        self.get_form_fields()
        if self.form.keys():
            self.set_outfile_name()
            self.handle_image()
            self.handle_text()
            self.text_out("Uploaded %s" % self.bname)
        else:
            self.text_out("Not yet submitted")

    def set_outfile_name(self):
        """ Using timestamp as basis for filenames """
        self.bname = datetime.now().strftime("%Y%m%dT%X")

    FORM_FIELD = "pic"
    def get_form_fields(self):
        self.form = cgi.FieldStorage()

    def handle_image(self):
        if 'pic' not in self.form:
            self.text_out("Not yet submitted")
            return
        self.fileitem = self.form[self.FORM_FIELD]

        if not self.fileitem.file: 
            self.text_out("Bad form field name pic not file")
            return

        if not self.fileitem.filename:
            self.text_out("No filename given - did you choose a file?")
            return

        self.picfile_name = self.fileitem.filename

        fout = file(os.path.join(UPLOAD_DIR, self.bname+".jpg"), 'wb')

        while True:
            chunk = self.fileitem.file.read(100000)
            if not chunk: break
            fout.write(chunk)
        fout.close()

    def handle_text(self):
        UPLOAD_SECTION = "upload"
        output = SafeConfigParser()
        output.add_section(UPLOAD_SECTION)

        data = dict((x,self.form.getfirst(x)) for x in self.form if x != self.FORM_FIELD)

        for key in data.keys():
            output.set(UPLOAD_SECTION, key, data[key])
        output.set(UPLOAD_SECTION, "image_file", self.picfile_name or "")

        output.add_section("edit")
        for key in data.keys():
            output.set("edit", key, data[key])

        with open(os.path.join(UPLOAD_DIR, self.bname + ".ini"), 'wb') as outfile:
            output.write(outfile)
    

if __name__ == '__main__':
    main()
