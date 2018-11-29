#!/usr/bin/python3
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
import cgitb; cgitb.enable() # pylint: disable=C0321
import os
import sqlite3
import subprocess
from datetime import datetime, time
from my_info import config_path
from PIL import Image
from PIL.ExifTags import TAGS
from templates import PAGE_TEMPLATE, WITH_EDIT_CSS

THUMB_SIZE = 400, 300
ORIG_KEYS = """description comment size calories carbs protein fat servings
    time day meal""".split()

SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')

UPLOAD_SECTION = "upload"
IMAGE_FILE_FIELD = "pic"

class EntryForm(object):
    """ Class to handle input and output of basic entry form """
    def __init__(self):
        self.upload_time = datetime.now()
        self.bname = self.outfile_name()
        config = config_path()
        # Since this is an "edit" form, this menu_url is for the editing menus
        self.menu_url = config.dir('MENU_URL')
        self.db_file = config.dir('DB_FILE')
        self.log_filename = config.dir("DB_LOG")
        self.thumb_dir = config.dir("THUMB_DIR")
        self.archive_dir = config.dir("ARCHIVE_DIR")
        self.fileitem = None
        self.log_file = None
        self.form = cgi.FieldStorage()

    def process(self):
        with open(self.log_filename, "a") as self.log_file:
            if self.form.keys():
                status = self.handle_filled_form()
            else:
                status = "Unsubmitted Form"

        print(PAGE_TEMPLATE.format(
            SCRIPT_NAME=SCRIPT_NAME,
            MENU_URL=self.menu_url,
            STATUS=status,
            EDIT_CSS=WITH_EDIT_CSS,
            TITLE="Input Course Information",
            h1="Food Entry")
        )

    def handle_filled_form(self):
        """ Create image, thumbnail, database, and database log entries

        using a unique base filename <basename>
        <ARCHIVE_DIR>/<basename>.image:  uploaded imagefile, if there is one
        <THUMB_DIR>/<basename>.jpg:  thumbnail of imagefile, if there is one
        <DB_FILE>: sqlite3 database with appended:
            id: autoincremented id
            orig_description, description: form description field
            orig_comment, comment: comment form comment field
            orig_size, size: form size field
            orig_calories, calories: form calories field
            orig_carbs, carbs: form carbs field
            orig_protein, protein: form protein field
            orig_fat, fat: form fat field
            orig_servings, servings: form servings field
            orig_time: form time field
            time: form time field or exif_data time field or upload time field
            orig_day: form day field
            day: form day field or exif_data day field or upload day field
            orig_meal: form meal field
            meal: form meal field or meal based on time
            image_file: client file name
            ini_id: <basename>
            thumb_id: <basename>, if there is one

        """

        image_fields = self.handle_image()
        if 'error' in image_fields:
            return image_fields['error']
        text_fields = self.set_fields_from_form()
        if 'error' in text_fields:
            return text_fields['error']

        merged = self.merge_fields(image_fields, text_fields)
        # Create multiple records if semicolons in orig_description/description
        # and no cals/carbs/prot/fat
        if 'description' in merged and ';' in merged['description']:
            if bool(
                    set(merged.keys()) &
                    set(['calories', 'fat', 'protein', 'carbs'])):
                return "Can't split course with %s set" % (
                    list(
                        set(merged.keys()) &
                        set(['calories', 'fat', 'protein', 'carbs'])))
            else:
                newdesc = merged['description'].split(';')
                for description in newdesc:
                    part = merged.copy()
                    part['description'] = description
                    self.insert_in_db(part)
                return "Uploaded %s dishes at %s" % (len(newdesc), self.bname)
        else:
            self.insert_in_db(merged)
            return "Uploaded %s" % self.bname

    def outfile_name(self):
        """ Using timestamp as basis for filenames

            This will have to change to allow more than one entry per second

        """
        return self.upload_time.strftime("%Y%m%dT%X")

    def handle_image(self):
        """ Upload image, create thumbnail, get exif data

            Return dict of:
                time: time value of exif Datetime
                day: day value of exif Datetime
                image_file: form pic file filename attribute
                thumb_id: thumbnail file basename, if there is one

        """
        if IMAGE_FILE_FIELD not in self.form:
            # Form didn't have file upload field, but let's allow it
            return dict()

        self.fileitem = self.form[IMAGE_FILE_FIELD]

        if not self.fileitem.filename:
            # No image file uploaded
            return dict()

        answer = dict()

        answer['image_file'] = self.fileitem.filename

        image_filename = self.bname + ".image"
        image_path = os.path.join(self.archive_dir, image_filename)
        # We don't know what kind of image file it is but we don't need to
        with open(image_path, 'wb') as fout:
            while True:
                chunk = self.fileitem.file.read(100000)
                if not chunk:
                    break
                fout.write(chunk)

        try:
            img = Image.open(image_path)
        except IOError:
            return dict(error="Error opening image file %s" % image_filename)

        exif_daytime = read_exif_data(img)
        if exif_daytime:
            answer['day'] = exif_daytime[0]
            answer['time'] = exif_daytime[1]

        thumbid = self.bname + ".jpg"
        thumbfile_name = os.path.join(self.thumb_dir, thumbid)



        # Check that file names don't have some sort of space in them
        if len(image_path.split()) > 1 or len(thumbfile_name.split()) > 1:
            return dict(
                error="Bad filesnames {} or {}".format(
                    image_path, thumbfile_name))

        command = "convert -thumbnail {} {} {}".format(
            THUMB_SIZE[1], image_path, thumbfile_name).split()
        returncode = subprocess.call(command)
        if returncode:
            # Try it the old way here in python
            thumb = img.copy()
            thumb.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
            if thumb.mode != 'RGB':
                thumb = thumb.convert('RGB')
            thumb.save(thumbfile_name, "JPEG")
            os.chmod(thumbfile_name, 0o644)
            return dict(
                error="Error creating thumbnail {}".format(
                    thumbfile_name))

        answer['thumb_id'] = self.bname
        return answer

    def set_fields_from_form(self):
        """ Gather data from form """
        answer = dict()
        for key in ORIG_KEYS:
            if key in self.form and not self.form.filename:
                value = self.form.getfirst(key)
                # Empty strings in POST are reported
                if value != '':
                    answer["orig_%s" % key] = answer[key] = value

        return answer

    def merge_fields(self, image_fields, text_fields):
        """ Combine image data and text field data """
        answer = dict(
            day=self.upload_time.strftime("%Y-%m-%d"),
            time=self.upload_time.strftime("%H:%M"),
            ini_id=self.bname
        )

        answer.update(image_fields)
        answer.update(text_fields)

        if 'meal' not in answer:
            if 'time' in answer:
                answer['meal'] = meal_at_this_time(answer['time'])

        return answer

    def insert_in_db(self, dict_):
        """ Insert record(s) defined by dict_


        """

        # Insert a course record with columns and values defined by dict_
        fields = [x for x in dict_ if dict_[x] != ""]
        vals = [dict_[x] for x in fields]

        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if not fields:
                line = "insert into course default values"
                cursor.execute(line)
                print(dict(command=line), file=self.log_file)
            else:
                line = "INSERT INTO course (%s) VALUES (%s)" % (
                    ", ".join(fields), ", ".join("?" for x in vals))
                cursor.execute(line, vals)
                print(dict(command=line, args=vals), file=self.log_file)

def read_exif_data(img):
    """ Read out pertinent image exif data - in this case datetime

        Exif time is in YYYY:MM:DD HH:MM:SS format.
        The formats from the form are YYYY-MM-DD and HH:MM
        The easiest way to convert is to go through datetime

    """
    try:
        exif = img._getexif() # pylint: disable=W0212
    except AttributeError:
        return
    if not exif:
        return
    for tag, value in exif.items():
        decoded = TAGS.get(tag, hex(tag))
        if decoded.startswith('DateTime'):
            dt = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
            return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")

def meal_at_this_time(when):
    """ Return string for default meal eaten at this time

        Should eventually configure the meal times

    """
    when = datetime.strptime(when, "%H:%M").time()
    if when < time(4):
        return "Snack"
    elif when < time(11):
        return "Breakfast"
    elif when < time(15):
        return "Lunch"
    elif when < time(17):
        return "Snack"
    elif when < time(21, 30):
        return "Supper"
    else:
        return "Snack"

if __name__ == '__main__':
    EntryForm().process()
