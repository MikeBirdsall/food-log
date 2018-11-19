
# Used in form.py
PAGE_TEMPLATE = """Content-Type: text/html\n\n<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Input Course Information</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta charset="UTF-8">
    <style>
      form {{
        width:360px;
      }}

      label {{
        display: inline-block;
        text-align:left;
      }}

      label.nutrit {{
         width:70px;
         text-align:right;
      }}

      input.nutrit {{
        display:inline-block;
        width:45px;
      }}

      label.inst {{
        width:70px;
        text-align:right;
      }}

      input.inst {{
        text-align:left;
      }}

      input.calc {{
        width:150px;
      }}

      input {{
        display:inline-block;
        text-align:right;
      }}

      fieldset {{
        background:#fff7db;
      }}

      input[type=submit] {{
        background: #db8c47;
      }}
      button {{
          background: #db8c47;
      }}
    </style>
    <script>
      <!--
        function sayHello() {{
          alert("Hello World")
        }}
      //-->
    </script>
        
  </head>
  <body>
    <h1>Food Entry</h1>
    <form method="get">
      <button formaction="report.py">List all meals</button>
      <button formaction="{MENU_URL}" style="float: right;">Food Menu</button>
      <input type="hidden" name="edit" value="1">
      <input type="hidden" name="reverse" value="1">
    </form>
    <form method="post" enctype="multipart/form-data" action="{SCRIPT_NAME}">
      <br>
      <input type="submit">
      <br>
      <fieldset style="max-width:360px">
        <legend>Image Entry:</legend>
        <input type="file" name="pic" accept="image/*"/>
      </fieldset>

      <fieldset style="max-width:360px">
        <legend>Identifying Information:</legend>
        Description: (used as title for dish)<br>
        <input type="text" name="description" placeholder="Title/Description/Identifier"/>
        <br>Comment:<br>
            <input type="text" name="comment" placeholder="Comment/Context/Excuse"/>
        <br>Amount:<br>
            <input type="text" name="size" placeholder="Like 2 cups or 12 oz or large bowl"/>
      </fieldset>

      <fieldset style="max-width:360px"><legend>Nutrition:</legend>
        <label class="nutrit" for="calories">Calories:</label>
        <input class="nutrit" type="number" name="calories" id="calories" max="3000" step="5"/>
            <button type="button" onclick="document.getElementById('calories').value = 
                  eval(document.getElementById('calccal').value || 0)">=</button>
            <input class="calc" type="text" id="calccal" />
        <br>

        <label class="nutrit" for="carbs">Carbs(g):</label>
            <input class="nutrit" type="number" name="carbs" id="carbs" size="2" max="300" step="1">
            <button type="button" onclick="document.getElementById('carbs').value = 
                  eval(document.getElementById('calccarbs').value || 0)">=</button>
            <input class="calc" type="text" id="calccarbs" />
        <br>

        <label class="nutrit" for="prot">Protein(g):</label>
            <input class="nutrit" type="number" name="protein" id="prot" size="2" max="300" step="1">
            <button type="button" onclick="document.getElementById('prot').value = 
                  eval(document.getElementById('calcprot').value || 0)">=</button>
            <input class="calc" type="text" id="calcprot" />
        <br>

        <label class="nutrit" for="fat" >Fat(g):</label>
            <input class="nutrit" type="number" name="fat" id="fat" size="2" max="300" step="0.5">
            <button type="button" onclick="document.getElementById('fat').value = 
                  eval(document.getElementById('calcfat').value) || 0">=</button>
            <input class="calc" type="text" id="calcfat"/>
        <br>

      </fieldset>

      <fieldset style="max-width:360px">
        <legend>Instance Information:</legend>

        <label class="inst" for="servings">Servings:</label>
        <input class="inst" type="number" name="servings" id="servings" min="0.1" max="9" value="1" step="0.1"><br>

        <label class="inst" for="day">Day:</label>
        <input class="inst" type="date" name="day" id="day"><br>

        <label class="inst" for="time">Time: </label>
        <input type="time" name="time" id="time"><br>

        <label class="inst" for="meal">Meal: </label>
        <input class="inst" list="meals" name="meal" id="meal"><br>

        <datalist id="meals">
          <option value="Breakfast">
          <option value="Lunch">
          <option value="Supper">
          <option value="Snack">
          <option value="Exercise">
        </datalist>
      </fieldset>
      <br>
      <input type="submit">
      <br>
    </form>

    <form method="get">
      <button formaction="report.py">List all meals</button>
      <button formaction="{MENU_URL}" style="float: right;">Food Menu</button>
      <input type="hidden" name="edit" value="1">
      <input type="hidden" name="reverse" value="1">
    </form>
    <p>{STATUS}</p>
  </body>
</html>
"""

# Used in copy_template
HEAD_TEMPLATE = """\
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Create course from template</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      button {{
        max-width: 540px;
        width: 100%;
        background: #db8c47;
      }}
    </style>
  </head>
  <body> \
    <h1>Choose Template</h1>
    <form method="get">
      <button formaction="{MENU_URL}/">Back to Food Menu</button><br/><br/>\
"""

ROW_TEMPLATE = """\
      <button name="choice" type="submit" value=%s>%s</button><br/><br/>\
"""

FORM_TAIL_TEMPLATE = """\
    </form>\
  </body>
</html>\
"""

# Used in detail.py
FORM_TOP_TEMPLATE = """\
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
  <head>
    <title>View Course Info</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta charset="UTF-8">
    <style>
      form {{
          width:360px;
      }}

      label {{
          display: inline-block;
          text-align:left;
      }}
      
      label.nutrit {{
          width:70px;
          text-align:right;
      }}

      input.nutrit {{
          display:inline-block;
          width:45px;
      }}

      label.inst {{
          width:70px;
          text-align:right;
      }}

      input.inst {{
          text-align:left;
      }}

      input.calc {{
        width:150px;
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
    </style>
  </head>
  <body>
    <h1>Food Entry</h1>
    <form method="get">
        <button formaction="{MENU_URL}/">Food Menu</button>
    </form>
    <form method="post" action="{SCRIPT_NAME}">
      <input type="hidden" name="id" value={id}>
      <fieldset style="max-width:360px" disabled>
        <legend>Identifying Information:</legend>
        Description:<br>
        <input type="text" name="description" placeholder="Title" value="{description}">
        <br>Comment:<br>
        <input type="text" name="comment" placeholder="Comment" value="{comment}"><br>
        Amount:<br>
        <input type="text" name="size" placeholder="Like 2 cups or large bowl" value="{size}">
      </fieldset>

      <fieldset style="max-width:360px" disabled><legend>Nutrition:</legend>
        <label class="nutrit" for="calories">Calories:</label>
        <input class="nutrit" type="number" name="calories" id="calories"
          max="3000" step ="5" value="{calories}">
        <br>

        <label class="nutrit" for="carbs">Carbs(g):</label>
        <input class="nutrit" type="number" name="carbs" id="carbs" size="2" max="300" value="{carbs}" step="1">
        <br>

        <label class="nutrit" for="protein">Protein(g):</label>
        <input class="nutrit" type="number" name="protein" id="protein" size="2" max="300" step="1"
           value="{protein}">
        <br>

        <label class="nutrit" for="fat">Fat(g):</label>
        <input class="nutrit" type="number" name="fat" id="fat" size="2" max="300" value="{fat}" step="0.5">
        <br>

        </fieldset>

        <fieldset style="max-width:360px" disabled>
        <legend>Instance Information:</legend>
        <label class="inst" for="servings">Servings:</label>
        <input class="inst" type="number" name="servings" id="servings" min="0.1" max="9" value="{servings}"><br>

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
    </form>
    {STATUS}<br/>
    {IMAGE}
  </body>
</html>
"""

IMAGE_TEMPLATE = """\
    <img src="%s" alt="Food">\
"""

# Used in edit.py

DELETED_TEMPLATE = """\
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Deleted Course Display</title>
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
          width:70px;
          text-align:right;
      }}

      input.nutrit {{
          display:inline-block;
          width:45px;
      }}

      label.inst {{
          width:70px;
          text-align:right;
      }}

      input.inst {{
          text-align:left;
      }}

      input.calc {{
        width:150px;
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
    </style>
  </head>
  <body>
    <h1>Deleted Food Entry</h1>
    <form method="get">
        <button formaction="{MENU_URL}/">Food Menu</button>
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
            <button type="button" onclick="document.getElementById('calories').value = 
                  eval(document.getElementById('calccal').value || 0)">=</button>
            <input class="calc" type="text" id="calccal" />
        <br>

        <label class="nutrit" for="carbs">Carbs(g):</label>
        <input class="nutrit" type="number" name="carbs" id="carbs" size="2" max="300" value="{carbs}" step="1" readonly>
            <button type="button" onclick="document.getElementById('carbs').value = 
                  eval(document.getElementById('calccarbs').value || 0)">=</button>
            <input class="calc" type="text" id="calccarbs" />
        <br>

        <label class="nutrit" for="protein">Protein(g):</label>
        <input class="nutrit" type="number" name="protein" id="protein" size="2" max="300" step="1">
            <button type="button" onclick="document.getElementById('prot').value = 
                  eval(document.getElementById('calcprot').value || 0)">=</button>
            <input class="calc" type="text" id="calcprot" />
        <br>

           value="{protein}" readonly><br>
        <label class="nutrit" for="fat">Fat(g):</label>
        <input class="nutrit" type="number" name="fat" id="fat" size="2" max="300" value="{fat}" step="0.5" readonly>
            <button type="button" onclick="document.getElementById('fat').value = 
                  eval(document.getElementById('calcfat').value) || 0">=</button>
            <input class="calc" type="text" id="calcfat"/>
        <br>

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

EDIT_TOP_TEMPLATE = """\
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Edit Course Detail</title>
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
          width:70px;
          text-align:right;
      }}
      
      input.nutrit {{
          display:inline-block;
          width:45px;
      }}

      label.inst {{
          width:70px;
          text-align:right;
      }}

      input.inst {{
          text-align:left;
      }}

      input.calc {{
        width:150px;
      }}

      input {{
          display:inline-block;
          text-align:right;
      }}

      fieldset {{
          background:#fff7db;
      }}

      input[type=submit] {{
          background: #db8c47;
      }}

      button {{
          background: #db8c47;
      }}
    </style>
  </head>
  <body>
    <h1>Edit Food Entry</h1>
    <form method="get">
        <button formaction="{MENU_URL}/">Food Menu</button>
        <br>
    </form>
    <form method="post" action="{SCRIPT_NAME}">
      <br>
      <input type="submit" value="Update" name="action">
      <input type="submit" value="Copy" name="action" style="float: center;">
      <input type="submit" value="Make Template" name="action" style="float: right;"><br>
      <input type="hidden" name="id" value={id}>
      <br>
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
            <button type="button" onclick="document.getElementById('calories').value = 
                  eval(document.getElementById('calccal').value || 0)">=</button>
            <input class="calc" type="text" id="calccal" />
        <br>

        <label class="nutrit" for="carbs">Carbs(g):</label>
        <input class="nutrit" type="number" name="carbs" id="carbs" size="2" max="300" value="{carbs}" step="1">
            <button type="button" onclick="document.getElementById('carbs').value = 
                  eval(document.getElementById('calccarbs').value || 0)">=</button>
            <input class="calc" type="text" id="calccarbs" />
        <br>

        <label class="nutrit" for="protein">Protein(g):</label>
        <input class="nutrit" type="number" name="protein" id="protein" size="2" max="300" step="1"
           value="{protein}">
            <button type="button" onclick="document.getElementById('prot').value = 
                  eval(document.getElementById('calcprot').value || 0)">=</button>
            <input class="calc" type="text" id="calcprot" />
        <br>

        <label class="nutrit" for="fat">Fat(g):</label>
        <input class="nutrit" type="number" name="fat" id="fat" size="2" max="300" value="{fat}" step="0.5">
            <button type="button" onclick="document.getElementById('fat').value = 
                  eval(document.getElementById('calcfat').value) || 0">=</button>
            <input class="calc" type="text" id="calcfat"/>
        <br>

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
# Used in entry_form.py
TEMPLATE = """\
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
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
         width:70px;
         text-align:right;
      }}

      input.nutrit {{
        display:inline-block;
        width:45px;
      }}

      label.inst {{
        width:70px;
        text-align:right;
      }}

      input.inst {{
        text-align:left;
      }}

      input.calc {{
        width:150px;
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
            <button type="button" onclick="document.getElementById('calories').value = 
                  eval(document.getElementById('calccal').value || 0)">=</button>
            <input class="calc" type="text" id="calccal" />
        <br>

        <label class="nutrit" for="carbs">Carbs(g):</label>
        <input class="nutrit" type="number" name="carbs" {carbs} id="carbs" size="2" max="300" step="1">
            <button type="button" onclick="document.getElementById('carbs').value = 
                  eval(document.getElementById('calccarbs').value || 0)">=</button>
            <input class="calc" type="text" id="calccarbs" />
        <br>

        <label class="nutrit" for="prot">Protein(g):</label>
        <input class="nutrit" type="number" name="protein" id="prot" {protein} size="2" max="300" step="1">
            <button type="button" onclick="document.getElementById('prot').value = 
                  eval(document.getElementById('calcprot').value || 0)">=</button>
            <input class="calc" type="text" id="calcprot" />
        <br>

        <label class="nutrit" for="fat">Fat(g):</label>
        <input class="nutrit" type="number" name="fat" id="fat" {fat} size="2" max="300" step="0.5">
            <button type="button" onclick="document.getElementById('fat').value = 
                  eval(document.getElementById('calcfat').value) || 0">=</button>
            <input class="calc" type="text" id="calcfat"/>
        <br>
        
      </fieldset>

      <fieldset style="max-width:360px">
        <legend>Instance Information:</legend>

        <label class="inst" for="servings">Servings:</label>
        <input class="inst" type="number" name="servings" id="servings" min="1" max="9" value="1"><br>

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
      <button formaction="./report.py">List all Meals</button>
      <input type="hidden" name="edit" value="1">
      <input type="hidden" name="reverse" value="1">
      <button formaction="{MENU_URL}" style="float: right">Food Menu</button>
    </form>
    <p>{status}</p>
  </body>\n</html>
"""

# Used in report.py

INVALID_TEMPLATE = """Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
  <head>
  <title>Invalid Parameters</title>
  <meta name="viewport" content="width-device-width, initial-scale=1" />
  </head>
  <body>
    <h1>{}</h1>
    {}
  </body>
</html>
"""

REPORT_HEAD_TEMPLATE = """Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Food Record {start} - {end}</title>
    <style>
      table {{
        background:#fff7db;
      }}
      table, th, td {{
        border: 1px solid black;
        border-collapse: collapse;
      }}
      th, td {{
        padding: 5px;
        white-space: nowrap;
      }}
      button {{
          background: #db8c47;
      }}
    </style>
  </head>
  <body>
    <h1>{title}</h1>
    <h2>{start} - {end}</h2>
    <form method="get">
        <button formaction="{foodmenu}">Food Menu</button>
    </form>
    <table>"""

AFTERWARD_TEMPLATE = """</table>
    <form method="get">
        <button formaction="{foodmenu}">Food Menu</button>
    </form>
    recomputed on {now}
  </body>
</html>"""

DAY_HEADER_TEMPLATE = """<tr>
        <th colspan="7">{date}</th>
      </tr>
      <tr>
        <th>Meal</th>
        <th>Item</th>
        <th>Servings</th>
        <th>Cals</th>
        <th>Carbs</th>
        <th>Fat</th>
        <th>Protein</th>
      </tr>"""

NUTRITION_TEMPLATE = """<td>{dish}</td>
        <td>{servings}</td>
        <td>{calories}</td>
        <td>{carbs}</td>
        <td>{fat}</td>
        <td>{protein}</td>
"""

OTHERS_IN_MEAL_TEMPLATE = """<tr>
""" + NUTRITION_TEMPLATE + """</tr>"""

FIRST_IN_MEAL_TEMPLATE = """<tr><th rowspan="{courses}">{meal}</th>
""" + NUTRITION_TEMPLATE + """</tr>"""

TOTAL_TEMPLATE = """<tr>
        <th colspan="3">Total</th>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>
"""
