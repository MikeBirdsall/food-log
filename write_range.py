#!/usr/bin/env python
""" First draft to create "weekly" from database

    Use the named database to create a web page
    all the meals for all the days specified
    There are some different switches to pick different days.
    --last-week does seven days starting with the first day of the
                week (make it configurable, for me it is Thursday)
                more than seven days ago.
    --start_date limits to entries after it (Default date.min)
    --end_date limits to entries before it (default date.max)

    writes to stdout

"""

from datetime import date, datetime, timedelta
from collections import defaultdict, namedtuple
from operator import attrgetter
import argparse
import sqlite3
from my_info import THUMB_URL
import cgitb; cgitb.enable()

ITEM = namedtuple('item',
    'comment carbs description servings calories fat day time '
    'protein meal size thumb_id')

HEADER_TEMPLATE = """<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Food Record %s - %s</title>
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
  </head>"""

BODY_START_TEMPLATE = """  <body>
    <h1>MGB Food</h1>
    <h2>%s - %s</h2>
    <form method="get">
        <button formaction="/and/images/pages/menu.html">Food Menu</button>
    </form>
    <table>"""

AFTERWARD_TEMPLATE = """    </table>
    recomputed on %s 
  </body>
</html>"""

FIRST_IN_MEAL_TEMPLATE = """      <tr><th rowspan="%s">%s</th>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>"""

OTHERS_IN_MEAL_TEMPLATE = """      <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>"""

DAY_HEADER_TEMPLATE = """      <tr>
        <th colspan="6">%s</th>
      </tr>
      <tr>
        <th>Meal</th>
        <th>Item</th>
        <th>Cals</th>
        <th>Carbs</th>
        <th>Fat</th>
        <th>Protein</th>
      </tr>"""

TOTAL_TEMPLATE = """      <tr>
        <th colspan="2">Total</th>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>
"""
class ConstructWebPage(object):

    def __init__(self, database):
        self.database = database
        self.start_date = None
        self.end_date = None

    def output(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

        print HEADER_TEMPLATE % (self.start_date, self.end_date)
        print BODY_START_TEMPLATE % (self.start_date, self.end_date)
        self.print_rows()
        print AFTERWARD_TEMPLATE % datetime.now()

    def sorted_items_by_meal(self, item_rows):
        """ Returns all items in the same meal, sorted by time """
        meals = defaultdict(list)
        for item in item_rows:
            meals[item.meal].append(item)

        for meal in meals.values():
            meal.sort(key=attrgetter('time'))

        return sorted(meals.values(), key=lambda x:x[0].time)

    def print_meal(self, meal):
        dish = meal[0]
        desc = ellipse_truncate(dish.description)
        print FIRST_IN_MEAL_TEMPLATE % (
            len(meal),
            dish.meal,
            thumb_url(dish, desc),
            blank_null(dish.calories),
            blank_null(dish.carbs),
            blank_null(dish.fat),
            blank_null(dish.protein))

        for dish in meal[1:]:
            desc = ellipse_truncate(dish.description)
            print OTHERS_IN_MEAL_TEMPLATE % (
                thumb_url(dish, desc),
                blank_null(dish.calories),
                blank_null(dish.carbs),
                blank_null(dish.fat),
                blank_null(dish.protein))

    def print_total(self, meals):
        """ Print total row for entire day"""
        cals = carbs = fat = protein = (0, "")
        for meal in meals:
            for dish in meal:
                cals = add_with_none(cals, dish.calories, dish.servings)
                carbs = add_with_none(carbs, dish.carbs, dish.servings)
                fat = add_with_none(fat, dish.fat, dish.servings)
                protein = add_with_none(protein, dish.protein, dish.servings)

        print TOTAL_TEMPLATE % (
            ''.join(map(str, cals)),
            ''.join(map(str, carbs)),
            ''.join(map(str, fat)),
            ''.join(map(str, protein)))

    def print_item_rows(self, item_rows):

        meals = self.sorted_items_by_meal(item_rows)
        for meal in meals:
            self.print_meal(meal)
        self.print_total(meals)

    def print_rows(self):
        # Open the database,
        items = dict()
        days = defaultdict(list)
        with sqlite3.connect(self.database) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''select description, comment,
                servings, calories, fat, protein, carbs, day, time,
                meal, size, thumb_id from course
                where day between ? and ? order by day, time''',
                (self.start_date, self.end_date))

            for course in cursor.fetchall():
                fitem = ITEM(**course)
                items[fitem.day, fitem.time] = fitem
                days[fitem.day].append((fitem.day, fitem.time))

            for day, item_list in sorted(days.iteritems()):
                print DAY_HEADER_TEMPLATE % datetime.strptime(
                    day, "%Y-%m-%d").strftime("%A %Y-%m-%d")
                self.print_item_rows([value for key, value in items.items()
                    if key in item_list])

def thumb_url(dish, label):
    """ Return Link to thumbnail image or placeholder if it doesn't exist """
    if not dish.thumb_id:
        return label
    return '<a href="%s">%s</a>' % (THUMB_URL + dish.thumb_id + ".jpg", label)

def blank_null(val):
    if val is None:
        return ""
    return val

def ellipse_truncate(text, length=40):
    """ Return canonical form of description to fit in length """
    result = text or "No Description Yet"
    return (result[:length-1] + "&hellip;") if len(result) > length else result

def get_dates(args):
    if args.last_week:
        # Get previous Wednesday (config this later)
        today = date.today()
        start_date = today - timedelta(days=(8 + (today.weekday() + 3) % 7))
        end_date = start_date + timedelta(days=6)
        return start_date, end_date
    else:
        return args.start_date, args.end_date



def add_with_none(now, new, servings):
    if new is None:
        return (now[0], "+?")
    else:
        return (now[0] + (new * servings), now[1])

def main():
    """ Commandline program to create food diary dataabase from ini files """
    parser = argparse.ArgumentParser()
    parser.add_argument("sqlite_file", type=str, help="database file")
    parser.add_argument("--last_week", "-w", action='store_true')
    parser.add_argument("--start_date",
        type=lambda s:datetime.strptime(s, "%Y-%m-%d").date(), default=date.min)
    parser.add_argument("--end_date", type=date, default=date.max)
    args = parser.parse_args()
    date_range = get_dates(args)
    ConstructWebPage(args.sqlite_file).output(*date_range)

if __name__ == '__main__':
    main()
