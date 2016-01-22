#!/usr/bin/python
""" Create html page with full listing of items in my food record

"""

import os, sys
from glob import glob
from ConfigParser import SafeConfigParser
from collections import defaultdict, namedtuple
from operator import attrgetter

ITEM = namedtuple('item',
    'comment carbs description servings calories fat day time '
    'protein meal size')

UPLOAD_DIR = "/big/dom/xkirkbird/www/and/images/"
THUMB_DIR = UPLOAD_DIR + "thumbs/"
ARCHIVE_DIR = UPLOAD_DIR + "archive/"
DATA_DIR = UPLOAD_DIR + "byday/"
#UPLOAD_DIR = "/home/mbirdsall/food/upload/"
#THUMB_DIR = "/home/mbirdsall/food/thumbs/"
#ARCHIVE_DIR = "/home/mbirdsall/food/archive/"
#DATA_DIR = "/home/mbirdsall/food/byday"

SECTION = 'edit'


def main():
    """ Generate full food listing html """

    # Gather all the info
    os.chdir(DATA_DIR)

    files = glob("*.ini")

    items = dict() # all fields for each item identified by upload second
    days = defaultdict(list) # list of all items in a day

    for _file in files:
        upload_second = os.path.splitext(_file)[0]
        parser = SafeConfigParser()
        parser.read(_file)
        info = dict(parser.items(SECTION))
        fitem = ITEM(**info)
        items[upload_second] = fitem
        days[fitem.day].append(upload_second)

    """
    for day, item_list in sorted(days.iteritems()):
        for item in sorted(item_list):
            print day, items[item].time, items[item].meal, items[item].description
    """

    print_header()
    print_body_start()
    for day, item_list in sorted(days.iteritems()):
        print_dayrow(day)
        print_item_rows([value for key, value in items.items() if key in item_list])
    print_afterward()

    sys.exit()

def sorted_items_by_meal(item_rows):
    meals = defaultdict(list)
    for item in item_rows:
        meals[item.meal].append(item)

    for meal in meals.values():
        meal.sort(key=attrgetter('time'))

    z = sorted(meals.values(), key=lambda x: x[0].time)
    return z


def ellipse_truncate(s, length):
    if s:
        return (s[:length] + "&hellip;") if len(s) > length+2 else s
    else:
        return "No Description Yet"

def print_meal(meal):
    width = 40
    desc = ellipse_truncate(meal[0].description, width)
    print """<tr>
    <th rowspan="%s">%s</th>
    <td>%s</td>
    </tr>""" % (len(meal), meal[0].meal, desc)
    for dish in meal[1:]:
        desc = ellipse_truncate(dish.description, width)
        print """<tr><td>%s</td></tr>""" % desc

def print_item_rows(item_rows):
    """ Divide by meal """
    # Get the meals and order them by earliest item

    meals = sorted_items_by_meal(item_rows)
    for meal in meals:
        print_meal(meal)

def print_afterward():
    print """</table>
    </body>
    </html>"""

def print_header():
    print """<html>
    <head>
      <title>Food Items</title>
        <style>
          table {
            background:#fff7db;
          }
          table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
          }
          th, td {
            padding: 5px;
            white-space: nowrap;
          }
        </style>
      </head>
    """

def print_body_start():
    print """<body>
    <h1>MGB Food Log</h1>
    <table>
    """

def print_dayrow(day):
    print """<tr>
      <th colspan="2">%s</th>
      </tr>
      <tr>
        <th>Meal</th>
        <th>Item</th>
""" % day

def print_first_item_row(item_rows):
    print """<tr>
    <th rowspan="%s">%s</th>
      <td>%s</td>
    </th>""" % (len(item_rows), item_rows, item_rows)

if __name__ == '__main__':
    main()
