#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()
import os, sys

UPLOAD_DIR = "/big/dom/xkirkbird/www/and/test"

def text_out(message):
    print """ <p>%s</p>
    </body></html>
    """ % (message,)
    sys.exit()

print """Content-Type: text/html\n
<head>
    <meta name="viewport" content="width=320" />
<style>
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

</style>
</head>

<body>

<h1>Food Entry</h1>
<form method="post" enctype="multipart/form-data" action="http://kirkbird.com/cgi-bin/food/form.py">

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

form_field = "pic"
form = cgi.FieldStorage()
if 'pic' not in form:
    text_out("Not yet submitted")
else:
    fileitem = form[form_field]

if not fileitem.file: 
    text_out("Bad form field name pic not file")

if not fileitem.filename:
    text_out("No filename given - did you choose a file?")

fout = file(os.path.join(UPLOAD_DIR, fileitem.filename), 'wb')

while True:
    chunk = fileitem.file.read(100000)
    if not chunk: break
    fout.write(chunk)
fout.close()

bname, dummy = os.path.splitext(fileitem.filename)
fout = file(os.path.join(UPLOAD_DIR, bname + ".txt"), 'wb')
fout.write(form.getfirst("Description", ""))
fout.close()

text_out("File uploaded")

#   Cal:<input type="number" name="calories" size="2" maxsize="4" max="3000">
#   Carb:<input type="number" name="carbs" size="2" maxsize="3" max="300">
#   Prot:<input type="number" name="protein" size="2" maxsize="3" max="300">
#   Fat:<input type="number" name="fat" size="2" maxsize="3" max="300"><br>
#  servings: <input type="range" name="servings" id="servingID" min="1" max="9" value="1" oninput="servingOutID.value=servingID.value">
#  <output name="servingOutputName" id="servingOutID">1</output><br>
#  Description: (used as title for dish)<br> <textarea name="description" rows="3" cols="35"> </textarea>
