#!/usr/bin/python
"""
Program to edit a food item

This cgi-bin program is one of a group of programs to help me create and
maintain a record of everything I eat. This one writes and populates an html
form page which allows the food item fields be edited

Other programs will input new data, prepare output web pages, and to managed
the date in valious ways.

"""
import cgi
import cgitb; cgitb.enable() # pylint: disable=C0321
import os
import sqlite3
from datetime import datetime
from my_info import config_path

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')

TEMPLATE_REQUIRED = frozenset('description calories fat protein carbs'.split())
UPDATE_FIELDS = frozenset('description comment size calories number carbs '
    'protein fat servings day time meal'.split())
VALID_FIELDS = UPDATE_FIELDS.union('id ini_id action'.split())

FORM_TOP_TEMPLATE = """\
Content-Type: text/html

<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      form {{
          width:360px;
      }}
      label {{
          display: inline-block;
          text-align:left;
      }}
      label.nutrit {{
          width:130px;
          text-align:right;
      }}
      input.nutrit {{
          display:inline-block;
          width:70px;
      }}
      label.inst {{
          width:70px;
          text-align:right;
      }}
      input:inst {{
          text-align:left;
      }}
      input {{
          display:inline-block;
          text-align:right;
      }}
      fieldset {{
          background:#fff7db;
      }}
    </style>
  </head>
  <body>
    <h1>Edit Food Entry</h1>
    <form method="get">
        <button formaction="{MENU_URL}">Food Menu</button>
    </form>
    <form method="post" action="{SCRIPT_NAME}">
      <input type="submit" value="Update" name="action">
      <input type="submit" value="Make Template" name="action" style="float: right;"><br>
      <input type="hidden" name="id" value={id}>
      <fieldset style="max-width:360px">
        <legend>Identifying Information:</legend>
        Description:<br>
        <input type="text" name="description" placeholder="Title" value="{description}">
        <br>Comment:<br>
        <input type="text" name="comment" placeholder="Comment" value="{comment}"><br>
        Amount:<br>
        <input type="text" name="size" placeholder="Like 2 cups or large bowl" value="{size}">
      </fieldset>

      <fieldset style="max-width:360px"><legend>Nutrition:</legend>
        <label class="nutrit" for="calories">Calories:</label>
        <input class="nutrit" type="number" name="calories" id="calories"
          max="3000" step ="5" value="{calories}">
        <label class="nutrit" for="carbs">Carbs(g):</label>
        <input class="nutrit" type="number" name="carbs" id="carbs" size="2" max="300" value="{carbs}" step="1"><br>
        <label class="nutrit" for="protein">Protein(g):</label>
        <input class="nutrit" type="number" name="protein" id="protein" size="2" max="300" step="1"
           value="{protein}"><br>
        <label class="nutrit" for="fat">Fat(g):</label>
        <input class="nutrit" type="number" name="fat" id="fat" size="2" max="300" value="{fat}" step="0.5">
        </fieldset>

        <fieldset style="max-width:360px">
        <legend>Instance Information:</legend>
        <label class="inst" for="servings">Servings:</label>
        <input class="inst" type="number" name="servings" id="servings" min="0.1" max="9" step="0.1" value="{servings}"><br>

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
      </fieldset>
      <input type="submit" value="Update" name="action">
      <input type="submit" value="Make Template" name="action" style="float: right;"><br>
      <br> <br> <br> <br>
      <input type="submit" value="Delete" name="action">
    </form>
    {STATUS}<br/>
    {IMAGE}
  </body>
</html>
"""

DELETED_TEMPLATE = """\
Content-Type: text/html

<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      form {{
          width:360px;
      }}
      label {{
          display: inline-block;
          text-align:left;
      }}
      label.nutrit {{
          width:130px;
          text-align:right;
      }}
      input.nutrit {{
          display:inline-block;
          width:70px;
      }}
      label.inst {{
          width:70px;
          text-align:right;
      }}
      input:inst {{
          text-align:left;
      }}
      input {{
          display:inline-block;
          text-align:right;
      }}
      fieldset {{
          background:#fff7db;
      }}
    </style>
  </head>
  <body>
    <h1>Deleted Food Entry</h1>
    <form method="get">
        <button formaction="{MENU_URL}">Food Menu</button>
    </form>
    <form method="post" action="{SCRIPT_NAME}">
      <input type="hidden" name="id" value={id}>
      <fieldset style="max-width:360px">
        <legend>Identifying Information:</legend>
        Description:<br>
        <input type="text" name="description" placeholder="Title" value="{description}" readonly>
        <br>Comment:<br>
        <input type="text" name="comment" placeholder="Comment" value="{comment}" readonly><br>
        Amount:<br>
        <input type="text" name="size" placeholder="Like 2 cups or large bowl" value="{size}" readonly>
      </fieldset>

      <fieldset style="max-width:360px"><legend>Nutrition:</legend>
        <label class="nutrit" for="calories">Calories:</label>
        <input class="nutrit" type="number" name="calories" id="calories"
          max="3000" step ="5" value="{calories}" readonly>
        <label class="nutrit" for="carbs">Carbs(g):</label>
        <input class="nutrit" type="number" name="carbs" id="carbs" size="2" max="300" value="{carbs}" step="1" readonly><br>
        <label class="nutrit" for="protein">Protein(g):</label>
        <input class="nutrit" type="number" name="protein" id="protein" size="2" max="300" step="1"
           value="{protein}" readonly><br>
        <label class="nutrit" for="fat">Fat(g):</label>
        <input class="nutrit" type="number" name="fat" id="fat" size="2" max="300" value="{fat}" step="0.5" readonly>
        </fieldset>

        <fieldset style="max-width:360px">
        <legend>Instance Information:</legend>
        <label class="inst" for="servings">Servings:</label>
        <input class="inst" type="number" name="servings" id="servings" min="0.1" max="9" step="0.1" value="{servings}" readonly><br>

        <label class="inst" for="day">Day:</label>
        <input class="inst" type="date" name="day" id="day" value="{day}" readonly><br>

        <label class="inst" for="time">Time:</label>
        <input type="time" name="time" value="{time}" readonly><br>

        <label class="inst" for="meal">Meal:</label>
        <input class="inst" list="meals" id="meal" name="meal" value="{meal}" readonly>
            <datalist id="meals">
            <option value="Breakfast">
            <option value="Lunch">
            <option value="Supper">
            <option value="Snack">
            </datalist>
      </fieldset>
      <br>
    </form>
    {STATUS}<br/>
  </body>
</html>
"""

IMAGE_TEMPLATE = """\
    <img src="%s" alt="Food">\
"""

class EditCourse(object):
    """ Main program do create and handle form to edit food items """
    def __init__(self):
        self.old_data = dict()
        self.data = dict()

        config = config_path()
        self.menu_url = config.dir('MENU_URL')
        self.thumb_url = config.dir('THUMB_URL')
        self.db_file = config.dir('DB_FILE')
        self.log_filename = config.dir('DB_LOG')
        self.log_file = None
        self.cursor = None

    def process(self):
        """ If form filled, update database. In either case (re)draw form """

        self.data = self.get_form_data()
        with open(self.log_filename, "a") as self.log_file:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                self.cursor = conn.cursor()

                tmp = self.load_record()
                self.old_data = {key: "" if tmp[key] is None
                    else str(tmp[key]) for key in tmp}
                self.process_data()

    def process_data(self):

        if 'action' not in self.data:
            status = "Ready to Edit"
        elif self.data['action'] == 'Update':
            status = self.update()
        elif self.data['action'] == 'Make Template':
            status = self.make_template()
        elif self.data['action'] == 'Delete':
            status = self.delete()
            print DELETED_TEMPLATE.format(
                MENU_URL=self.menu_url,
                SCRIPT_NAME=SCRIPT_NAME,
                STATUS=status,
                **self.old_data
            )
            return
            
        else:
            status = "Invalid button %s" % self.data['action']

        # If a picture, display
        thumb_id = self.old_data['thumb_id']
        if thumb_id:
            image = IMAGE_TEMPLATE % os.path.join(self.thumb_url,
                                                  thumb_id + ".jpg")
        else:
            image = ''

        print FORM_TOP_TEMPLATE.format(
                MENU_URL=self.menu_url,
                SCRIPT_NAME=SCRIPT_NAME,
                STATUS=status,
                IMAGE=image,
                **self.old_data
        )

    def make_template(self):
        """ Create a template database entry """

        missing = TEMPLATE_REQUIRED.difference(self.data)
        if missing:
            return ("<h3>Template must have %s filled in.</h3>" %
                ', '.join(missing))

        # Write a database entry
        xline = """insert into template
            (description, comment, calories, fat, protein, carbs, size)
            values (?, ?, ?, ?, ?, ?, ?)"""
        xparms = tuple(self.data.get(x, '') for x in """description comment
            calories fat protein carbs size""".split())

        self.cursor.execute(xline, xparms)
        print >> self.log_file, dict(command=xline, args=xparms)

        return "<h3>Template created at %s</h3>" % (datetime.now().time())


    def delete(self):
        """ Delete record from database, write deleted entry in log """
        print >> self.log_file, "Delete", self.old_data
        print >> self.log_file, "Replace with:"
        print >> self.log_file, "#insert into course ", str(tuple(self.old_data.keys())).translate(None, "'"), "VALUES ", str(tuple(self.old_data.values()))
        line = "Delete from course where id = %s" % (self.data['id'])
        self.cursor.execute(line)
        return "<p>Entry deleted at %s</p>" % datetime.now().time()

    def update(self):
        """ Update fields in database and write mysql in log """
        status = "<p>Not yet updated</p>"
        needed = UPDATE_FIELDS.intersection(self.data)
        needed = [key for key in needed if self.old_data[key] != self.data[key]]
        if needed:
            args = tuple(str(self.data[x]) for x in needed)
            updates = ', '.join("%s = ?" % x for x in needed)

            line = "UPDATE course set %s where id = %s" % (updates,
                self.data['id'])

            # Want to self.cursor.execute(xline, *needed stuff)
            # Want to print lline % * needed stuff
            self.cursor.execute(line, args)
            print >> self.log_file, dict(command=line, args=args)

            # Update the data to reflect changes
            self.old_data.update({k: self.data.get(k) for k in needed})

            status = "<p>Dish  updated at %s</p>" % datetime.now().time()

        return status

    def load_record(self):
        if 'id' in self.data:
            self.cursor.execute('SELECT * from course where id = ?',
                (self.data['id'],))
        elif 'ini_id' in self.data:
            self.cursor.execute('SELECT * from course where ini_id = ?',
                (self.data['ini_id'],))
        else:
            raise RuntimeError('No record selected')

        answer = self.cursor.fetchone()
        if not answer:
            raise RuntimeError('Record not found')

        return dict(answer)

    def get_form_data(self):

        fs = cgi.FieldStorage()

        # We need identity of record we are editing; either "id" or "ini_id"
        if not (fs.keys() and ("id" in fs or "ini_id" in fs)):
            raise RuntimeError("No Input")

        # Don't allow extra fields - protection against misspelling
        invalid_fields = set(fs.keys()).difference(VALID_FIELDS)
        if invalid_fields:
            raise RuntimeError("Bad field names %s" % invalid_fields)

        return dict((x, fs.getfirst(x)) for x in fs)

if __name__ == '__main__':
    EditCourse().process()

