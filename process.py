#!/usr/bin/python
"""
 Program to process information from an files uploaded from phone.

 This program is one of a group of programs to help me create and maintain a
 record of everything I eat. This one normally runs as a crong job and copies
 information from the images into the ini file that holds the text values, and
 created a thumbnail (or at least smaller) image which is used for most of the
 web pages.  The resulting pages are moved out of the staging directory into
 archive or working directories.

 """

from glob import glob
import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from ConfigParser import SafeConfigParser
from datetime import datetime, time
from my_info import UPLOAD_DIR, THUMB_DIR, ARCHIVE_DIR, DATA_DIR

Thumb_size = 400, 300

class main(object):
    def __init__(self):
        self.picdaytime = ""
        self.ini_parser = None
        self.gps_data = dict()

    def run(self):
        os.chdir(UPLOAD_DIR)

        if not os.path.exists(THUMB_DIR):
            os.makedirs(THUMB_DIR)

        if not os.path.exists(ARCHIVE_DIR):
            os.makedirs(ARCHIVE_DIR)

        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        for basename in self.get_basenames():

            try:
                ini = open(basename + ".ini", 'r+')
            except IOError:
                ini = None

            try:
                jpg = Image.open(basename + ".jpg")
            except IOError:
                jpg = None

            try:
                png = Image.open(basename + ".png")
            except IOError:
                png = None

            self.process(basename, ini, jpg, png)


    def get_basenames(self):
        # There are files grouped by their basename without extension.
        # Currently the basename is a timestamp when uploaded.
        # There should be an .ini file and possibly either a jpg or png file
        # But I may want to handle an image without an ini for recovery purposes
        files = glob("*.ini") + glob("*.jpg") + glob("*.png")
        return set(
            os.path.splitext(
                os.path.split(x)[1]
                )[0] for x in files)

    def read_ini_data(self, ini):
        """ Get data out of the ini file """
        self.ini_parser = SafeConfigParser()
        self.ini_parser.readfp(ini)
        if ('edit') not in self.ini_parser.sections():
            self.ini_parser.add_section('edit')
            for field in self.ini_parser.options('upload'):
                if field == 'image_file':
                    continue
                self.ini_parser.set('edit', field,
                    value=self.ini_parser.get('upload', field))

    def read_exif_data(self, img):
        self.picdaytime = None
        if not img:
            return
        exif = img._getexif()
        if not exif:
            return
        for tag, value in exif.items():
            decoded = TAGS.get(tag, hex(tag))
            # Put appropriate data into self
            if decoded.startswith('DateTime') and not self.picdaytime:
                # Transform 'YYYY:MM:DD HH:MM:SS' to datetime
                self.picdaytime = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
            elif decoded == 'GPSInfo':
                gps_data = dict()
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                self.gps_data = gps_data

    def update_datetime(self, basename):
        """ Use multiple possibilities to default date/time """

        # Use date or time from ini file preferentially, but if either is not
        # set, fill in from exif
        # datetime is set (in this priority) from the edit section of the ini,
        # from the exif date and time in the image, or from the filename
        # chosen at upload

        saved = self.ini_parser

        if self.picdaytime:
            picday = self.picdaytime.date().strftime("%Y-%m-%d")
            pictime = self.picdaytime.time().strftime("%H:%M")


            if not saved.has_option('edit', 'day') or not saved.get('edit', 'day'):
                saved.set('edit', 'day', value=picday)

            if not saved.has_option('edit', 'time') or not saved.get('edit', 'time'):
                saved.set('edit', 'time', value=pictime)
            return

        if not basename:
            return

        basename_datetime = datetime.strptime(basename, "%Y%m%dT%H:%M:%S")
        basename_day = basename_datetime.date().strftime("%Y-%m-%d")
        basename_time = basename_datetime.time().strftime("%H:%M")
        saved.set('edit', 'day', value=basename_day)
        saved.set('edit', 'time', value=basename_time)

    def update_thumb_id(self, basename, img):
        saved = self.ini_parser
        if img:
            thumb_id = basename
        else:
            thumb_id = ""

        saved.set('edit', 'id', basename)
        saved.set('edit', 'thumb_id', thumb_id)

    def update_meal(self):
        saved = self.ini_parser
        if saved.has_option('edit', 'meal') and saved.get('edit', 'meal'):
            return
        if not saved.has_option('edit', 'time'):
            return
        if not saved.get('edit', 'time'):
            return

        mealtime = saved.get('edit', 'time')
        mealtime = datetime.strptime(mealtime, "%H:%M").time()
        if mealtime < time(4):
            meal = "Snack"
        elif mealtime < time(11):
            meal = "Breakfast"
        elif mealtime < time(15):
            meal = "Lunch"
        elif mealtime < time(17):
            meal = "Snack"
        elif mealtime < time(21, 30):
            meal = "Supper"
        else:
            meal = "Snack"

        saved.set('edit', 'meal', meal)


    def create_empty_ini(self, basename):
        """ Create an empty ini file and open as ini """
        self.ini_parser = SafeConfigParser()
        self.ini_parser.add_section('upload')
        self.ini_parser.add_section('edit')
        for field in ('description', 'comment', 'size', 'servings', 'calories',
                'carbs', 'protein', 'fat', 'day', 'time', 'meal'):
            self.ini_parser.set('upload', field, "")
            self.ini_parser.set('edit', field, "")
        return open(basename+".ini", mode='w+')

    def process(self, basename, ini, jpg, png):
        """ Fill in, thumbnail, and move out the way """


        print "Processing %s" % basename

        # Shouldn't have both jpg and png, but give precedence to jpg
        img = jpg or png

        if jpg and png:
            shutil.move(png.filename,
                os.path.join(ARCHIVE_DIR, basename+'.png'))

        if not ini:
            ini = self.create_empty_ini(basename)
        else:
            self.read_ini_data(ini)

        # If not already set, day and time can come from the image file
        # But if they were uploaded or edited already, don't use it
        # GPS and location will be the same way when they get done
        self.read_exif_data(img)
        self.update_datetime(basename)
        self.update_meal()
        self.update_thumb_id(basename, img)
        ini.seek(0, 0)
        self.ini_parser.write(ini)

        # Create the thumbnail
        if img:
            thumbfile_name = os.path.join(THUMB_DIR, basename+".jpg")
            thumbfile = open(thumbfile_name, mode="w+")
            thumb = img.copy()
            thumb.thumbnail(Thumb_size, Image.ANTIALIAS)
            thumb.save(thumbfile_name, "JPEG")
            thumbfile.close()
            os.chmod(thumbfile_name, 0644)
            shutil.move(img.filename, os.path.join(ARCHIVE_DIR, img.filename))

        ini_dest = os.path.join(DATA_DIR, ini.name)
        shutil.move(ini.name, ini_dest)
        # Now put a link to the same file in a directory for the day
        day_dir = os.path.join(DATA_DIR, self.ini_parser.get('edit', 'day'))
        if not os.path.exists(day_dir):
            os.makedirs(day_dir)
        os.link(ini_dest, os.path.join(day_dir, ini.name))

        ini.close()

if __name__ == '__main__':
    main().run()

