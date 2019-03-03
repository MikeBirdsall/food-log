"""
    Templates and supporting strings for creating HTML for foodlog
"""

# Snippets to fill in variable parts of the templates
WITHOUT_EDIT_CSS = """\
      input.calc {
        width:130px;
        visibility:hidden;
      }

      button.ifedit {
          visibility:hidden;
      }
"""

WITH_EDIT_CSS = """\
      input.calc {
        width:130px;
      }
"""

# Needs for interpolation:
#   TITLE, EDIT_CSS

HEAD2_TEMPLATE = """\
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
  <head>
    <title>{TITLE}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="./css/foodlog.css" />
    <style>
      {EDIT_CSS}
    </style>
  </head>
"""


# Used in full_search.py
# Needs for interpolation:
#  MENU_URL, TITLE, EDIT_CSS

SEARCH_TEMPLATE = HEAD2_TEMPLATE + """\
  <body>
    <h1>{h1}</h1>
    <form method="post">
      <input type="submit">
      <br> <br>
      <fieldset style='max-width:360px'>
        Search String:<br>
        <input type="text" name="searchstring" size="50" autofocus required/>
      </fieldset>
      <br>
      <input type="submit">
    </form>
    <h2>{status}</h2>
    <form method="get">
      <br>
      <button formaction="index.html">Back to Food Menu</button>
    </form>
    {cheatsheet}
  </body>
</html>
"""

# Used in detail.py
# Needs for interpolation:

IMAGE_TEMPLATE = """\
    <img src="%s" alt="Food">\
"""

# Used in entry_form.py
# Needs for interpolation:

TEMPLATE = HEAD2_TEMPLATE + """\
  <body>
    <h1>{h1}</h1>
    <form method="get">
      <button formaction="run.py">List all meals</button>
      <input type="hidden" name="template" value="TEMPLATE">
      <input type="hidden" name="cmd" value="report">
      <input type="hidden" name="edit" value="1">
      <input type="hidden" name="reverse" value="1">
      <button formaction="index.html" style="float: right">Food Menu</button>
    </form>
    <form method="post" enctype="multipart/form-data" action="{script}">
      <input type="hidden" name="cmd" value="enter">
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
            <button type="button" class="ifedit" onclick="document.getElementById('calories').value =
                  eval(document.getElementById('calccal').value || 0)">=</button>
            <input class="calc" type="text" id="calccal" />
        <br>

        <label class="nutrit" for="carbs">Carbs(g):</label>
        <input class="nutrit" type="number" name="carbs" {carbs} id="carbs" size="2" max="300" step="1">
            <button type="button" class="ifedit" onclick="document.getElementById('carbs').value =
                  eval(document.getElementById('calccarbs').value || 0)">=</button>
            <input class="calc" type="text" id="calccarbs" />
        <br>

        <label class="nutrit" for="prot">Protein(g):</label>
        <input class="nutrit" type="number" name="protein" id="prot" {protein} size="2" max="300" step="1">
            <button type="button" class="ifedit" onclick="document.getElementById('prot').value =
                  eval(document.getElementById('calcprot').value || 0)">=</button>
            <input class="calc" type="text" id="calcprot" />
        <br>

        <label class="nutrit" for="fat">Fat(g):</label>
        <input class="nutrit" type="number" name="fat" id="fat" {fat} size="2" max="300" step="0.5">
            <button type="button" class="ifedit" onclick="document.getElementById('fat').value =
                  eval(document.getElementById('calcfat').value) || 0">=</button>
            <input class="calc" type="text" id="calcfat"/>
        <br>

      </fieldset>

      <fieldset style="max-width:360px">
        <legend>Instance Information:</legend>

        <label class="inst" for="servings">Servings:</label>
        <input class="inst" type="number" name="servings" id="servings" min="0.1" max="9" step="0.1" value="1"><br>

        <label class="inst" for="day">Day:</label>
        <input class="inst" type="date" name="day" id="day"><br>

        <label class="inst" for="time">Time:</label>
        <input class="inst" type="time" name="time" id="time"><br>

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
      <button formaction="run.py">List all meals</button>
      <input type="hidden" name="cmd" value="report">
      <input type="hidden" name="edit" value="1">
      <input type="hidden" name="reverse" value="1">
      <button formaction="index.html" style="float: right">Food Menu</button>
    </form>
    <p>{status}</p>
  </body>\n</html>
"""

# Used in report.py
# Needs for interpolation:


INVALID_TEMPLATE = """\
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
  <head>
  <title>Invalid Parameters</title>
  <meta name="viewport" content="width-device-width, initial-scale=1" />
  <meta charset="UTF-8">
  </head>
  <body>
    <h1>{}</h1>
    {}
  </body>
</html>
"""

# Used in report.py
# Needs for interpolation:

NUTRITION_TEMPLATE = """<td>{dish}</td>
        <td>{servings}</td>
        <td>{calories}</td>
        <td>{carbs}</td>
        <td>{fat}</td>
        <td>{protein}</td>
"""

# Used in report.py
# Needs for interpolation:

OTHERS_IN_MEAL_TEMPLATE = """<tr>
""" + NUTRITION_TEMPLATE + """</tr>"""

# Used in report.py
# Needs for interpolation:

FIRST_IN_MEAL_TEMPLATE = """<tr><th rowspan="{courses}">{meal}</th>
""" + NUTRITION_TEMPLATE + """</tr>"""

# Used in report.py
# Needs for interpolation:

TOTAL_TEMPLATE = """<tr>
        <th colspan="3">Total</th>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>
"""
