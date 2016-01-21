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


UPLOAD_DIR = "/home/mbirdsall/food/upload/"
THUMB_DIR = "/home/mbirdsall/food/thumbs/"
ARCHIVE_DIR = "/home/mbirdsall/food/archive/"
DATA_DIR = "/home/mbirdsall/food/byday"
#UPLOAD_DIR = "/big/dom/xkirkbird/www/and/images/"
#THUMB_DIR = UPLOAD_DIR + "thumbs/"
#ARCHIVE_DIR = UPLOAD_DIR + "archive/"

Thumb_size = 400, 300

class main():
    def __init__(self):
        self.picdaytime = ""

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
            decoded = TAGS.get(tag, tag) # or get(tag, hex(tag))
            # Put appropriate data into self
            if decoded.startswith('DateTime') and not self.picdaytime:
                # Transform 'YYYY:MM:DD HH:MM:SS' to datetime
                self.picdaytime = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                # self.picdaytime = datetime(*map(int, value.replace(':', ' ').split()))
            elif decoded == 'GPSInfo':
                gps_data = dict()
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                self.gps_data = gps_data

    def update_datetime(self, basename):
        """ Use multiple possibilities to default date/time """

        # datetime is set (in this priority) from the edit section of the ini,
        # from the exif date and time in the image, or from the filename
        # chosen at upload

        saved = self.ini_parser
        if saved.has_option('edit', 'day') and saved.get('edit', 'day'):
            return

        if saved.has_option('edit', 'time') and saved.get('edit', 'time'):
            return

        if self.picdaytime:
            picday = self.picdaytime.date().strftime("%Y-%m-%d")
            pictime = self.picdaytime.time().strftime("%H:%M")

            saved.set('edit', 'day', value=picday)
            saved.set('edit', 'time', value=pictime)
            return

        if not basename:
            return

        basename_datetime = datetime.strptime(basename, "%Y%m%dT%H:%M:%S")
        basename_day = basename_datetime.date().strftime("%Y-%m-%d")
        basename_time = basename_datetime.time().strftime("%H:%M")
        saved.set('edit', 'day', value=basename_day)
        saved.set('edit', 'time', value=basename_time)

    def update_meal(self):
        saved = self.ini_parser
        if saved.has_option('edit', 'meal') and saved.get('edit', 'meal'):
            return
        if not saved.has_option('edit', 'time') or not saved.get('edit', 'time'):
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
        ini.seek(0,0)
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





'''
for fname in files:

    # Intention is to make this rerunnable, so original files are
    # are placed into the archive directory. If you copy all the files
    # back from the archive directory, delete all the files in the thumbs
    # directory, and possibly empty the database (intelligently) you can
    # rerun on everything. That will require keeping the .txt file with
    # any edited changes. May want to keep original and edited data.
    image = Image.open(fname)

    newfile = tempfile.NamedTemporaryFile(suffix='.jpg', prefix='image_',
        dir=THUMB_DIR, delete=False)

'''

'''
    # Save thumbnail copy
    thumb = image.copy()
    thumb.thumbnail(Thumb_size, Image.ANTIALIAS)
    thumb.save(newfile.name, 'JPEG')
    newfile.close()
    os.chmod(newfile.name, 0644)

    # Collect and save database info
        # From text file
        #    Description
        #    amount
        #    cals
        #    protein
        #    fat
        #    carbs
        #    meal
        # from exif
        #   creation time
        #   gps coordinates
        # File name
        #   fname = full name from browser
        #   basename = os.path.splitext(fname)
        #   newfile.name


'''

'''
    path, basename = os.path.split(fname)
    basename, ext = os.path.splitext(basename)
    textname = os.extsep.join([basename, "txt"])

    # Copy image and txt file to archive
    shutil.move(fname, os.path.join(ARCHIVE_DIR, basename+ext))

    textfull = os.path.join(UPLOAD_DIR, textname)
    #if os.path.isfile(textname):
        #shutil.move(textfull, os.path.join(ARCHIVE_DIR, textname))

    try:
        shutil.move(textfull, os.path.join(ARCHIVE_DIR, textname))
    except IOError as e:
        if e.errno != 2:
            raise
        else:
            print "Skipping missing text file %s " % (textfull,)


    # TODO: Deal with duplicate and missing filenames

'''

if __name__ == '__main__':
    main().run()

    """
    Move the data from the .txt file into a databaes (perhaps ultimately, they
    should be put in the database when uploading), create a thumbnail from the
    .jpg and put it in a thumbnail directory, extract exif information from the
    .jpg into the database and move the .jpg to an archive, # which indicates
    that the processing is done.

    The exif processing and the thumbnail processing can all be done in python
    with the PIL (Python Imaging Library).

    To create the thumbnail, open the image with

        from PIL Import Image

        newsize = width, height
        im = Image(infile)
        tn = im.copy()
        tn.thumbnail(newsize, Image.ANTIALIAS)
        tn.save(outputpath, 'JPEG')

        can also use tn = im.resize(newsize, Image.ANTIALIAS) instead. Check
        the implications of this.  In either case, have to deal with aspect
        ratio.


    To deal with exif values
    (Also check on using the piexif library with PIL)

        from PIL.ExifTags import TAGS

        img = Image.open(imgdir + fname)
        exif = img._getexif()
        if exif:
            for tag, value in exif.items():
                decoded = TAGS.get(tag, tag) # or get(tag, hex(tag))
                if decoded == 'Orientation':
                    if value == 3: img = img.rotate(180)
                    ...

    Dealing with GPS Latitude and Longitude

        from PIL.ExifTags import TAGS, GPSTAGS

        im = Image(infile)
        info = im._getexif()
        if info:
            for tag, value in info.items():
                decoded = get(tag, tag)
                if decoded == 'GPSInfo':
                    gps_data = dict()
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]

                    exif_data[decoded] = gps_value
                else:
                    exif_data[decoded] = value

        # exif_data['GPSInfo']['GPSLatitude'] and
        # exif_data['GPSInfo']['GPSLongitude']
        # each have a three element array with each holding two

    Dealing with time picture taken (in Exif data)

    Thumbnail in IFD1 of EXIF data?

    ://pypi.python.org/pypi/ExifRead


    resources:
    http://andrius.miasnikovas.lt/2010/04/creating-thumbnails-from-photos-with-python-pil/
    https://opensource.com/life/15/2/resize-images-python
    http://effbot.org/imagingbook/image.htm
    http://eran.sandler.co.il/2011/05/20/extract-gps-latitude-and-longitude-data-from-exif-using-python-imaging-library-pil/comment-page-1/
    """


