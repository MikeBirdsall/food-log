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

THUMB_SIZE = 400, 300

class main(object):
    def __init__(self):
        self.picdaytime = None
        self.ini_parser = None
        self.gps_data = dict()
        self.ini_name = ""

    def run(self):
        os.chdir(UPLOAD_DIR)

        if not os.path.exists(THUMB_DIR):
            os.makedirs(THUMB_DIR)

        if not os.path.exists(ARCHIVE_DIR):
            os.makedirs(ARCHIVE_DIR)

        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        for basename in sorted(self.get_basenames()):
            self.ini_name = basename+".ini"
            self.process(basename)


    def load_ini_data(self):
        try:
            with open(self.ini_name, 'r') as inifile:
                self.ini_parser.readfp(inifile)
        except IOError:
            self.ini_parser.add_section('upload')
            for field in ('description', 'comment', 'size', 'servings',
                    'calories', 'carbs', 'protein', 'fat', 'day', 'time',
                    'meal', 'image_file'):
                self.ini_parser.set('upload', field, "")

        if ('edit') not in self.ini_parser.sections():
            self.ini_parser.add_section('edit')
            for field in self.ini_parser.options('upload'):
                if field == 'image_file':
                    continue
                self.ini_parser.set('edit', field,
                    value=self.ini_parser.get('upload', field))


    def get_basenames(self):
        # There are files grouped by their basename without extension.
        # Currently the basename is a timestamp when uploaded.
        # There should be an .ini file and a .image file
        # But I may want to handle an image without an ini for recovery purposes
        # Perhaps deal with image files loaded some other way with other
        # extensions?
        files = glob("*.ini") + glob("*.image")
        return set(
            os.path.splitext(
                os.path.split(x)[1]
                )[0] for x in files)

    def read_exif_data(self, img):
        self.picdaytime = None
        try:
            exif = img._getexif()  # pylint: disable=W0212
        except AttributeError:
            return
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
        """ Use multiple possibilities to default date/time

            If date or time are already set in the form, use that value
            If one or both are not and we have data from image exif, use
            that for the appropriate one.
            If one or both still not set, use value from basename.
            If we don't have a basename???? we can' set it.

        """

        if self.picdaytime:
            default_datetime = self.picdaytime
        else:
            try:
                default_datetime = datetime.strptime(basename,
                    "%Y%m%dT%H:%M:%S")
            except ValueError:
                # No datetime we can set
                return

        date_eaten = default_datetime.date().strftime("%Y-%m-%d")
        time_eaten = default_datetime.time().strftime("%H:%M")

        saved = self.ini_parser
        if not saved.has_option('edit', 'day') or not saved.get('edit', 'day'):
            saved.set('edit', 'day', value=date_eaten)

        if not saved.has_option('edit', 'time') or not saved.get('edit', 'time'):
            saved.set('edit', 'time', value=time_eaten)

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
        mealtime = saved.get('edit', 'time')
        if not mealtime:
            return

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

    def process(self, basename):
        """ Fill in, thumbnail, and move out the way """
        print "Processing %s" % basename

        self.ini_parser = SafeConfigParser()
        self.load_ini_data()

        try:
            img = Image.open(basename + ".image")
        except IOError:
            self.picdaytime = None
            img = None
        else:
            self.read_exif_data(img)
            thumbfile_name = os.path.join(THUMB_DIR, basename+".jpg")
            thumb = img.copy()
            thumb.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
            thumb.save(thumbfile_name, "JPEG") # Thumbnails may be overwritten
            os.chmod(thumbfile_name, 0644) # Make it servable to browser
            shutil.move(img.filename, ARCHIVE_DIR) # Move into archive directory without overwriting

        self.update_datetime(basename)
        self.update_meal()
        self.update_thumb_id(basename, img)
        with open(self.ini_name, 'w') as inifile:
            self.ini_parser.write(inifile)

        shutil.move(self.ini_name, DATA_DIR)
        # Now put a link to the same file in a directory for the day
        day_dir = os.path.join(DATA_DIR, self.ini_parser.get('edit', 'day') or "date-unknown")
        if not os.path.exists(day_dir):
            os.makedirs(day_dir)
        os.link(os.path.join(DATA_DIR, self.ini_name),
            os.path.join(day_dir, self.ini_name))

if __name__ == '__main__':
    main().run()

