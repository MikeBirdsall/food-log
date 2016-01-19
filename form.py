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
</head>
<body>

<p><strong>Food Entry</strong></p>
<form method="post" enctype="multipart/form-data"
action="http://kirkbird.com/cgi-bin/form2.py">
  <label>Enter Dish</label><br>
  <input type="file" name="pic" accept="image/*"><br>

  Description: (used as title for dish)<br> <textarea name="description"
  rows="3" cols="35">
  </textarea><br>

  Amount:<br> <input type="text" name="size size="35><br>

  Cal:<input type="number" name="calories" max="3000"><br>
  Carb:<input type="number" name="carbs" size="2" max="300">
  Prot:<input type="number" name="protein" size="2" max="300">
  Fat:<input type="number" name="fat" size="2" max="300"><br>

  Comment: (context/excuse/...)<br><input type="text" name="comment"
  placeholder="Comment/Context/Excuse"><br>

  servings: <input type="number" name="servings" min="1" max="9" value="1">

  day: <input type="date" name="day"><br>

  time: <input type="time" name="time"><br>

  meal: <input list="meals" name="meal">
    <datalist id="meals">
      <option value="Breakfast">
      <option value="Lunch">
      <option value="Supper">
      <option value="Snack">
    </datalist>
  <br>
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
