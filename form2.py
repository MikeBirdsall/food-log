#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()
import os, sys

UPLOAD_DIR = "/big/dom/xkirkbird/www/and/images"

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

<p><strong>Upload Image Of Meal</strong></p>
<form method="post" enctype="multipart/form-data"
action="http://kirkbird.com/cgi-bin/form2.py">
  <label>Pick Image</label><br>
  <input type="file" name="pic" accept="image/*"><br>
  Description:<br>
  <input type="text" name="Description">
  <input type="submit"><br>
</form>

"""
form_field = "pic"
form = cgi.FieldStorage()
if 'pic' not in form:
    text_out("No picture yet")
else:
    fileitem = form[form_field]

if not fileitem.file: 
    text_out("Bad form field name pic not file")

if not fileitem.filename:
    text_out("No filename given - did you choose a file?")

fout = file(os.path.join(UPLOAD_DIR, fileitem.filename), 'wb')

while 1:
    chunk = fileitem.file.read(100000)
    if not chunk: break
    fout.write(chunk)
fout.close()

bname, dummy = os.path.splitext(fileitem.filename)
fout = file(os.path.join(UPLOAD_DIR, bname + ".txt"), 'wb')
fout.write(form.getfirst("Description", ""))
fout.close()

text_out("File uploaded")

