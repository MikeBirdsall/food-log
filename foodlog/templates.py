
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
            <input type="text" id="calccal" />
        <br>

        <label class="nutrit" for="carbs">Carbs(g):</label>
            <input class="nutrit" type="number" name="carbs" id="carbs" size="2" max="300" step="1">
            <button type="button" onclick="document.getElementById('carbs').value = 
                  eval(document.getElementById('calccarbs').value || 0)">=</button>
            <input type="text" id="calccarbs" />
        <br>

        <label class="nutrit" for="prot">Protein(g):</label>
            <input class="nutrit" type="number" name="protein" id="prot" size="2" max="300" step="1">
            <button type="button" onclick="document.getElementById('prot').value = 
                  eval(document.getElementById('calcprot').value || 0)">=</button>
            <input type="text" id="calcprot" />
        <br>

        <label class="nutrit" for="fat" >Fat(g):</label>
            <input class="nutrit" type="number" name="fat" id="fat" size="2" max="300" step="0.5">
            <button type="button" onclick="document.getElementById('fat').value = 
                  eval(document.getElementById('calcfat').value) || 0">=</button>
            <input type="text" id="calcfat"/>
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

