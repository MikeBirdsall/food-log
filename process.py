#!/usr/bin/python
"""
 This is going to be a program to process images uploaded, generally from an
 Android phone, which I am using to keep track of my diet.

 There will be files in the base directory (for now it is www/and/images)
 that have been newly updated. There will be two files with matching names
 apart from extensions; a .txt and a .jpg (or possible png).
 I want to

 """
import sys
import os
import tempfile
import shutil
from PIL import Image


UPLOAD_DIR = "/big/dom/xkirkbird/www/and/images/"
THUMB_DIR = UPLOAD_DIR + "thumbs/"
ARCHIVE_DIR = UPLOAD_DIR + "archive/"

Thumb_size = 400, 300

files = os.listdir(UPLOAD_DIR)

files = [os.path.join(UPLOAD_DIR, file) for file in files 
    if file.endswith(".jpg") or file.endswith(".png")]

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


    path, basename = os.path.split(fname)
    basename, ext = os.path.splitext(basename)
    textname = os.extsep.join([basename, "txt"])

    # Copy image and txt file to archive
    shutil.move(fname, os.path.join(ARCHIVE_DIR, basename+ext))

    textfull = os.path.join(UPLOAD_DIR, textname)
    """
    if os.path.isfile(textname):
        shutil.move(textfull, os.path.join(ARCHIVE_DIR, textname))
    """

    try:
        shutil.move(textfull, os.path.join(ARCHIVE_DIR, textname))
    except IOError as e:
        if e.errno != 2:
            raise
        else:
            print "Skipping missing text file %s " % (textfull,)


    # TODO: Deal with duplicate and missing filenames

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


