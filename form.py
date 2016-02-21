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
import sqlite3
from ConfigParser import SafeConfigParser
from datetime import datetime
from my_info import config_path

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')

UPLOAD_SECTION = "upload"
HEAD_TEMPLATE = """Content-Type: text/html\n\n<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      form {
        max-width:360px;
      }

      label {
        display: block;
        text-align:left;
      }

      input {
        display:block;
      }

      label.nutrit {
         display: block;
         text-align:left;
      }

      input.nutrit {
        display:block;
      }

      label.inst {
        text-align:left;
      }

      input:inst {
        display:block;
        text-align:left;
      }

      fieldset {
        background:#fff7db;
      }
    </style>
  </head>
"""

TAIL_TEMPLATE = """    <p>%s</p>
  </body>\n</html>
"""

FORM_TEMPLATE = """    <h1>Food Entry</h1>
    <form method="get">
      <button formaction="{MENU_URL}/list.html">List all meals</button>
      &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;
      <button formaction="{MENU_URL}">Food Menu</button>
    </form>
    <form method="post" enctype="multipart/form-data" action="{SCRIPT_NAME}">
      <input type="submit"><br>
      <fieldset style="max-width:360px">
        <legend>Image Entry:</legend>
        <input type="file" name="pic" accept="image/*"/>
      </fieldset>

      <fieldset style="max-width:360px">
        <legend>Identifying Information:</legend>
        <label>Description: (used as title for dish)<br>
            <input type="text" name="description" placeholder="Title/Description/Identifier"/>
        </label>
        <label>Comment:
            <input type="text" name="comment" placeholder="Comment/Context/Excuse"/>
        </label>
        <label>Amount:
            <input type="text" name="size" placeholder="Like 2 cups or 12 oz or large bowl"/>
        </label>
      </fieldset>

      <fieldset style="max-width:360px">
        <legend>Nutrition:</legend>
        <label class="nutrit">Calories:
            <input class="nutrit" type="number" name="calories" max="3000" step="5">
        </label>
        <label class="nutrit">Carbs(g):
            <input class="nutrit" type="number" name="carbs" size="2" max="300" step="1">
        </label>
        <label class="nutrit">Protein(g):
            <input class="nutrit" type="number" name="prot" size="2" max="300" step="1">
        </label>
        <label class="nutrit">Fat(g):
            <input class="nutrit" type="number" name="fat" size="2" max="300" step="0.5">
        </label>
      </fieldset>

      <fieldset style="max-width:360px">
        <legend>Instance Information:</legend>

        <label class="inst">Servings:
            <input class="inst" type="number" name="servings" min="1" max="9" value="1" step="0.1">
        </label>

        <label class="inst">Day:
            <input class="inst" type="date" name="day">
        </label>

        <label class="inst">Time:
            <input type="time" name="time">
        </label>

        <label class="inst">Meal:
            <input class="inst" list="meals" name="meal">
        </label>

        <datalist id="meals">
          <option value="Breakfast">
          <option value="Lunch">
          <option value="Supper">
          <option value="Snack">
        </datalist>
      </fieldset>
      <input type="submit">
    </form>

    <form method="get">
      <button formaction="{MENU_URL}/list.html">List all meals</button>
      &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;
      <button formaction="{MENU_URL}">Food Menu</button>
    </form>
"""

class main(object):
    def __init__(self):
        config = config_path()
        self.MENU_URL = config.dir('MENU_URL')
        self.UPLOAD_DIR = config.dir('UPLOAD_DIR')
        self.DB_FILE = config.dir('DB_FILE')
        self.fileitem = None
        self.status = ""
        self.picfile_name = None

        print HEAD_TEMPLATE
        self.body()
        print TAIL_TEMPLATE % (self.status,)

    def text_out(self, message):
        self.status = message

    def body(self):
        print """  <body>"""

        print FORM_TEMPLATE.format(SCRIPT_NAME=SCRIPT_NAME, MENU_URL=self.MENU_URL)
        self.parse_form_fields()

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
        if self.FORM_FIELD not in self.form:
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

        # We don't know what kine of image file it is but we don't need to
        fout = file(os.path.join(self.UPLOAD_DIR, self.bname+".image"), 'wb')

        while True:
            chunk = self.fileitem.file.read(100000)
            if not chunk:
                break
            fout.write(chunk)
        fout.close()

    def handle_text(self):
        output = SafeConfigParser()
        output.add_section(UPLOAD_SECTION)

        data = dict((x, self.form.getfirst(x))
            for x in self.form if x != self.FORM_FIELD)

        for key in data.keys():
            output.set(UPLOAD_SECTION, key, data[key])
        output.set(UPLOAD_SECTION, "image_file", self.picfile_name or "")

        output.add_section("edit")
        for key in data.keys():
            output.set("edit", key, data[key])

        with open(
                os.path.join(self.UPLOAD_DIR, self.bname + ".ini"),
                    'wb') as outfile:
            output.write(outfile)

        self.insert_in_db(self.extract_from_ini(output))

    def insert_in_db(self, dict_):
        fields = [x for x in dict_ if dict_[x] != ""]
        with sqlite3.connect(self.DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if not fields:
                cursor.execute("insert into course default values")
            else:
                cursor.execute(
                    "INSERT INTO course (%s)" % ", ".join(fields) +
                    "VALUES (%s)" % ", ".join("?" * len(fields)),
                    tuple([dict_[x] for x in fields]))

    def extract_from_ini(self, parser):
        combined = dict(("orig_"+x[0], x[1])
            for x in parser.items("upload"))
        combined['image_file'] = combined.pop('orig_image_file')
        combined.update(dict(parser.items("edit")))
        combined['ini_id'] = self.bname
        return combined

if __name__ == '__main__':
    main()
