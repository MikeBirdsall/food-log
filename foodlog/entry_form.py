""" Module for handling Food Log entry form

"""

from my_info import config_path

TEMPLATE = """\
Content-Type: text/html

<!DOCTYPE html>
<html>
  <head>
    <title>Enter Course</title>
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
      input.inst {{
        text-align:left;
      }}
      input {{
        display:inline-block;
        text-align:right;
      }}
      fieldset {{
        background:#fff7db;
      }}
      button {{
          background: #db8c47;
      }}
      input[type=submit] {{
          background: #db8c47;
      }}
    </style>
  </head>
  <body>
    <h1>Food Entry</h1>
    <form method="get">
      <button formaction="./report.py">List all meals</button>
      <input type="hidden" name="edit" value="1">
      <input type="hidden" name="reverse" value="1">
      <button formaction="{MENU_URL}" style="float: right">Food Menu</button>
    </form>
    <form method="post" enctype="multipart/form-data" action="{script}">
      <br>
      <input type="submit">
      <br>
      <fieldset style="max-width:360px">
        <legend>Image Entry:</legend>
        <input type="file" name="pic" accept="image/*"/><br>
      </fieldset>

      <fieldset style="max-width:360px">
        <legend>Identifying Information:</legend>
        Description: (used as title for dish)<br>
      <input type="text" name="description" {description} placeholder="Title/Description/Identifier"/><br>
        Comment:<br><input type="text" name="comment" {comment} placeholder="Comment/Context/Excuse"><br>
        Amount:<br> <input type="text" name="size" {size} placeholder="Like 2 cups or 12 oz or large bowl">
      </fieldset>

      <fieldset style="max-width:360px">
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

      <fieldset style="max-width:360px">
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
      <br>
      <input type="submit">
      <br>
    </form>

    <form method="get">
      <br>
      <button formaction="./report.py">List all Meals</button>
      <input type="hidden" name="edit" value="1">
      <input type="hidden" name="reverse" value="1">
      <button formaction="{MENU_URL}" style="float: right;>Food Menu</button>
    </form>
    <p>{status}</p>
  </body>\n</html>
"""

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



