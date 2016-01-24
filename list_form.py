#!/usr/bin/python
""" Create html page with full listing of items in my food record

"""

import os, sys
from glob import glob
from ConfigParser import SafeConfigParser
from collections import defaultdict, namedtuple
from operator import attrgetter
from my_info import DATA_DIR, THUMB_URL
from datetime import datetime

ITEM = namedtuple('item',
    'comment carbs description servings calories fat day time '
    'protein meal size id thumb_id')

SECTION = 'edit'

# The edit link depends on the cgi-bin organization
if 'GATEWAY_INTERFACE' in os.environ:
    EDIT_URL = os.environ.get('SCRIPT_NAME', '')
    EDIT_URL = os.path.join(os.path.dirname(EDIT_URL), "edit.py")
else:
    # this is a bit of a hack to get the relative URL
    # based on it being in the same directory as this script
    # and the url staring with "/cgi-bin"
    # Doesn't work in wing

    EDIT_URL = os.path.abspath(sys.argv[0])  # Get the full pathname
    EDIT_URL = EDIT_URL.partition('/cgi-bin')[1:] # Get parts staring with /cgi-bin
    EDIT_URL = "".join(EDIT_URL) # put it back together
    EDIT_URL = os.path.dirname(EDIT_URL) # pull off current script name
    EDIT_URL = os.path.join(EDIT_URL, 'edit.py') # add on new script name

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

    print_header()
    print_body_start()
    for day, item_list in sorted(days.iteritems(), reverse=True):
        print_dayrow(day)
        print_item_rows([value for key, value in items.items()
            if key in item_list])
    print_afterward()

    sys.exit()

def sorted_items_by_meal(item_rows):
    """ Returns all items in the same meal, sorted by time """
    meals = defaultdict(list)
    for item in item_rows:
        meals[item.meal].append(item)

    for meal in meals.values():
        meal.sort(key=attrgetter('time'))

    return sorted(meals.values(), key=lambda x: x[0].time)


def ellipse_truncate(text, length=40):
    """ Return canonical form of description to fit in length """
    result = text or "No Description Yet"
    return (result[:length-1] + "&hellip;") if len(result) > length else result

def thumb_url(dish, placeholder="No image"):
    """ Return Link to thumbnail image or placeholder if it doesn't exist """
    if not dish.thumb_id:
        return placeholder
    return '<a href="%s">%s</a>' % (THUMB_URL + dish.thumb_id + ".jpg", "Image")

def print_meal(meal):
    """ Print html for all the table rows for a meal

        The rows are printed such that the meal name spans all rows
    """
    dish = meal[0]
    desc = ellipse_truncate(dish.description)
    link = thumb_url(dish)
    edit = "<a href=%s?id=%s>Edit</a>" % (EDIT_URL, dish.thumb_id)

    print """<tr>
    <th rowspan="%s">%s</th>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    </tr>""" % (len(meal), meal[0].meal, desc, link, edit)
    for dish in meal[1:]:
        desc = ellipse_truncate(dish.description)
        link = thumb_url(dish)
        print """<tr><td>%s</td><td>%s</td><td>%s</td></tr>""" % (
            desc, link, edit)

def print_item_rows(item_rows):
    """ Divide by meal """
    # Get the meals and order them by earliest item

    meals = sorted_items_by_meal(item_rows)
    for meal in meals:
        print_meal(meal)

def print_afterward():
    """ Constant part at end of html """
    print """</table>
    </body>
    </html>"""

def print_header():
    """ Print the html for the <head/> """
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
    """ Print html for constant part at start of body

        Could be improved by templating to allow the full string, with variable
        part filled in and the whole thing printed

    """
    print """<body>
    <h1>MGB Food Log</h1>
    <table>
    """

def print_dayrow(day):
    """ Print html row with date, spanning the table """
    print """<tr>
      <th colspan="4">%s</th>
      </tr>
      <tr>
        <th>Meal</th>
        <th>Item</th>
        <th> </th>
        <th>Edit?</th>
""" % datetime.strptime(day, "%Y-%m-%d").strftime("%A %Y-%m-%d")

if __name__ == '__main__':
    main()
