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
from my_info import config_path
import cgitb; cgitb.enable()

config = config_path()
THUMB_URL = config.dir("THUMB_URL")

ITEM = namedtuple('item', 'comment carbs description servings calories fat day '
    'time protein meal size thumb_id')

HEADER_TEMPLATE = """\
<html>
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

BODY_START_TEMPLATE = """\
  <body>
    <h1>MGB Food</h1>
    <h2>%s - %s</h2>
    <form method="get">
        <button formaction="index.html">Food Menu</button>
    </form>
    <table>"""

AFTERWARD_TEMPLATE = """\
    </table>
    <form method="get">
        <button formaction="index.html">Food Menu</button>
    </form>
    recomputed on %s
  </body>
</html>"""

FIRST_IN_MEAL_TEMPLATE = """\
        <tr><th rowspan="%s">%s</th>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>"""

OTHERS_IN_MEAL_TEMPLATE = """\
      <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>"""

DAY_HEADER_TEMPLATE = """\
      <tr>
        <th colspan="7">%s</th>
      </tr>
      <tr>
        <th>Meal</th>
        <th>Item</th>
        <th>Servings</th>
        <th>Cals</th>
        <th>Carbs</th>
        <th>Fat</th>
        <th>Protein</th>
      </tr>"""

TOTAL_TEMPLATE = """\
      <tr>
        <th colspan="3">Total</th>
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
        print AFTERWARD_TEMPLATE % (datetime.now())

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
                fitem = ITEM(**course) # pylint:disable=W0142
                items[fitem.day, fitem.time] = fitem
                days[fitem.day].append((fitem.day, fitem.time))

            for day, item_list in sorted(days.iteritems()):
                print DAY_HEADER_TEMPLATE % datetime.strptime(
                    day, "%Y-%m-%d").strftime("%A %Y-%m-%d")
                print_item_rows([value for key, value in items.items()
                    if key in item_list])

def sorted_items_by_meal(item_rows):
    """ Returns all items in the same meal, sorted by time """
    meals = defaultdict(list)
    for item in item_rows:
        meals[item.meal].append(item)

    for meal in meals.values():
        meal.sort(key=attrgetter('time'))

    return sorted(meals.values(), key=lambda x:x[0].time)

def print_item_rows(item_rows):

    meals = sorted_items_by_meal(item_rows)
    for meal in meals:
        print_meal(meal)
    print_total(meals)

def print_meal(meal):
    dish = meal[0]
    desc = ellipse_truncate(dish.description)
    print FIRST_IN_MEAL_TEMPLATE % (
        len(meal),
        dish.meal,
        thumb_url(dish, desc),
        blank_null(dish.servings),
        blank_null(dish.calories, dish.servings),
        blank_null(dish.carbs, dish.servings),
        blank_null(dish.fat, dish.servings),
        blank_null(dish.protein, dish.servings))

    for dish in meal[1:]:
        desc = ellipse_truncate(dish.description)
        print OTHERS_IN_MEAL_TEMPLATE % (
            thumb_url(dish, desc),
            blank_null(dish.servings),
            blank_null(dish.calories, dish.servings),
            blank_null(dish.carbs, dish.servings),
            blank_null(dish.fat, dish.servings),
            blank_null(dish.protein, dish.servings))

def print_total(meals):
    """ Print total row for entire day"""
    cals = carbs = fat = protein = (0, "")
    for meal in meals:
        for dish in meal:
            cals = add_with_none(cals, dish.calories, dish.servings)
            carbs = add_with_none(carbs, dish.carbs, dish.servings)
            fat = add_with_none(fat, dish.fat, dish.servings)
            protein = add_with_none(protein, dish.protein, dish.servings)

# pylint:disable=W0141
    print TOTAL_TEMPLATE % (
        ''.join(map(str, cals)),
        ''.join(map(str, carbs)),
        ''.join(map(str, fat)),
        ''.join(map(str, protein)))

def thumb_url(dish, label):
    """ Return Link to thumbnail image or placeholder if it doesn't exist """
    if not dish.thumb_id:
        return label
    return '<a href="%s">%s</a>' % (THUMB_URL + dish.thumb_id + ".jpg", label)

def blank_null(val, servings=1):
    if val is None:
        return ""
    return val * servings

def ellipse_truncate(text, length=40):
    """ Return canonical form of description to fit in length """
    result = text or "No Description Yet"
    return (result[:length-1] + "&hellip;") if len(result) > length else result

def week_range(num_weeks, firstweekday=3):
    """ Return the range num_weeks ago

        Figure out the week where num_weeks == 0 is this week (contains today)
        and week == 1 is last week, and so on. Weeks are defined by start_day
        using the datetime.weekday(), so if start_day == 0, the week starts on
        Monday or if start_day == 3, the week starts on Thursday.

    """

    today = date.today()
    new_week_day = (today.weekday() - firstweekday) % 7
    weekstart = today - timedelta(days=new_week_day)
    first_day_of_week = weekstart - timedelta(days=num_weeks*7)
    last_day_of_week = min(today, first_day_of_week + timedelta(days=6))
    return first_day_of_week, last_day_of_week

def get_dates(args):
    if args.now:
        return week_range(0)
    elif args.last_week:
        return week_range(1)
    elif args.previous is not None:
        print args.previous
        return week_range(args.previous)
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
    dategroup = parser.add_mutually_exclusive_group()
    dategroup.add_argument("--now", "--current", "-n", action="store_true")
    dategroup.add_argument("--previous", "-p", type=int, choices=xrange(20))
    dategroup.add_argument("--last_week", "-w", action='store_true')
    parser.add_argument("--start_date",
        type=lambda s:datetime.strptime(s, "%Y-%m-%d").date(), default=date.min)
    parser.add_argument("--end_date", default=date.max,
        type=lambda s:datetime.strptime(s, "%Y-%m-%d").date())
    args = parser.parse_args()
    date_range = get_dates(args)
    ConstructWebPage(args.sqlite_file).output(*date_range) # pylint:disable=W0142

if __name__ == '__main__':
    main()
