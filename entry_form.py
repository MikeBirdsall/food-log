""" Module for handling Food Log entry form

"""

import sys, os
import cgi
import cgitb; cgitb.enable()

TEMPLATE = """\
Content-Type: text/html

<html>
  <head>
    <meta name="viewport" content="width=device=width, initial-scale=1" />
    <style>
      form {{
        width:300px;
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
    <h1>Food Entry</h1>
    <form method="get">
      <button formaction="/and/images/pages/list.html">List all meals</button>
    </form>
    <form method="post" enctype="multipart/form-data" action={script}">
      <input type="submit"><br>
      <fieldset style="width:270px">
        <legend>Image Entry:</legend>
        <input type="file" name="pic" accept="image/*"/><br>
      </fieldset>

      <fieldset style="width:270px">
        <legend>Identifying Information:</legend>
        Description: (used as title for dish)<br>
      <input type="text" name="description" {description} placeholder="Title/Description/Identifier"/><br>
        Comment:<br><input type="text" name="comment" {comment} placeholder="Comment/Context/Excuse"><br>
        Amount:<br> <input type="text" name="size" {size} placeholder="Like 2 cups or 12 oz or large bowl">
      </fieldset>

      <fieldset style="width:270px">
        <legend>Nutrition:</legend>
        <label class="nutrit" for="calories">Calories:</label>
        <input class="nutrit" type="number" name="calories" {calories} id="calories" max="3000" step="5">
        <label class="nutrit" for="carbs">Carbs(g):</label>
        <input class="nutrit" type="number" name="carbs" {carbs} id="carbs" size="2" max="300" step="1"><br>
        <label class="nutrit" for="prot">Protein(g):</label>
        <input class="nutrit" type="number" name="protein" id="prot" {protein} size="2" max="300" step="1"><br>
        <label class="nutrit" for="fat">Fat(g):</label>
        <input class="nutrit" type="number" name="fat" id="fat" {fat} size="2" max="300" step="0.5">
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
        </datalist><br>
      </fieldset>
      <input type="submit"><br>
    </form>

    <form method="get">
      <button formaction="/and/images/pages/list.html">List all meals</button>
      <button formaction="/and/images/pages/menu.html">Food Menu</button>
    </form>
    <p>{status}</p>
  </body>\n</html>
"""

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')

fields = 'description comment size calories carbs fat protein'.split()

class entryform(object):

    def __init__(self):
        self.status = ""
        self.page = ""

    def create_form(self, defaults, script, status=""):
        values = dict()
        for x in fields:
            if x in defaults.keys() and defaults[x] is not None:
                values[x] = "value=%s" % defaults[x]
            else:
                values[x] = ""
        values['status'] = status
        values['script'] = script
        self.page = TEMPLATE.format(**values)


