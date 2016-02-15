#!/usr/bin/env python
""" Create html file with food in date range

    Combining two earlier programs to create a list of food consumed in a date
    range either in a "read-only" mode for a dietician or someone else to
    review, or in an "edit" mode where the authorized user can do appropriate
    editing tasks on items in the list.

    Both of those will now be created from a database file which holds all the
    data for meals in that date range.

    This version of the program is not intended to be run as cgi-bin from a web
    page, but just from a cron job or command line, but the output is intended
    as a web page, and will have links to other web pages, cgi-bin programs, and
    the thumbnail pictures of a course/dish. It's possible that those can be
    distributed across web sites (kirkbird/mbirdsall) which are nonetheless all
    available on the same filesystem, or the HTML output may be copied to a
    different server.

    The URL links to those resources will therefore be rooted based on command
    line arguments which can be either absolute or relatives URLs. Relative URLS
    can either path-relative (leading ../ or no leading slash), root-relative (
    one leading slash), or protocol relative (two leading slashes.) The options
    are:

        --url => URL path for other static pages, like the menu (index.html, and
             other lists created by this program.)
        --cgi => URL path for cgi-bin and thus other dynamically created pages,
                 which will typically have a querystring with parameters in the
                 URL.
        --thumbs => URL path for the thumbnail pictures.

    The date range is created from command line arguments:
        --fdow, --first-day-of-week, -f => First day of week 0=Monday, 6=Sunday
        --now => Create report from previous first day of week till today
        --last-week does seven days starting with the first day of the
                week (make it configurable, for me it is Thursday)
                more than seven days ago.
        --start_date limits to entries after it (Default date.min)
        --end_date limits to entries before it (default date.max)

    writes to stdout

"""

from collections import defaultdict, namedtuple
from operator import attrgetter
#from my_info import config_path
from datetime import date, datetime, timedelta
import argparse
import sqlite3


ITEM = namedtuple('item', 'comment carbs description servings calories fat day '
    'time protein meal size ini_id thumb_id')

HEAD_TEMPLATE = """\
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Food Record {start} - {end}</title>
    <style>
      table {{
        background:#fff7db;
      }}
      table, th, td {{
        border: 1px solid black;
        border-collapse: collapse;
      }}
      th, td {{
        padding: 5px;
        white-space: nowrap;
      }}
    </style>
  </head>
  <body>
    <h1>MGB Food</h1>
    <h2>{start} - {end}</h2>
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

NUTRITION_TEMPLATE = """\
        <td>{dish}</td>
        <td>{servings}</td>
        <td>{calories}</td>
        <td>{carbs}</td>
        <td>{fat}</td>
        <td>{protein}</td>
"""
FIRST_IN_MEAL_TEMPLATE = """\
        <tr><th rowspan="{courses}">{meal}</th>
""" + NUTRITION_TEMPLATE + """\
      </tr>"""

OTHERS_IN_MEAL_TEMPLATE = """\
      <tr>
""" + NUTRITION_TEMPLATE + """\
      </tr>"""

DAY_HEADER_TEMPLATE = """\
      <tr>
        <th colspan="7">{date}</th>
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

#config = config_path()
#THUMB_URL = config.dir("THUMB_URL")

class ConstructWebPage(object):

    def __init__(self, database, readonly, cgi):
        self.database = database
        self.readonly = readonly
        self.cgi = cgi
        self.start_date = None
        self.end_date = None

    def output(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

        print HEAD_TEMPLATE.format(start=start_date, end=end_date)
        self.print_rows()
        print AFTERWARD_TEMPLATE % (datetime.now())

    def print_rows(self):
        # Open the database,
        items = dict()
        days = defaultdict(list)
        with sqlite3.connect(self.database) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''select description, comment, servings, calories,
                fat, protein, carbs, day, time, meal, size, ini_id, thumb_id
                from course
                where day between ? and ? order by day, time''',
                (self.start_date, self.end_date))

            for course in cursor.fetchall():
                fitem = ITEM(**course) # pylint:disable=W0142
                items[fitem.day, fitem.time] = fitem
                days[fitem.day].append((fitem.day, fitem.time))

            for day, item_list in sorted(days.iteritems()):
                meal_date = datetime.strptime(day, "%Y-%m-%d").strftime(
                    "%A %Y-%m-%d")
                print DAY_HEADER_TEMPLATE.format(date=meal_date)
                self.print_item_rows([value for key, value in items.items()
                    if key in item_list])

    def detail_or_edit_url(self, dish):
        """ Return Link to detail or edit page for item """

        label = ellipse_truncate(dish.description)
        script = "detail.py" if self.readonly else "edit.py"
        return "<a href={loc}{script}?id={id}>{label}</a>".format(
            loc=self.cgi, script=script, label=label, id=dish.ini_id)

    def course_dict(self, dish, **kwargs):
        answer = dict()
        for key, value in kwargs.iteritems():
            answer[key] = value
        answer['dish'] = self.detail_or_edit_url(dish)
        for field in "servings calories carbs fat protein".split():
            answer[field] = safe_by_servings(getattr(dish, field, None),
                dish.servings)

        return answer

    def sorted_items_by_meal(self, item_rows):
        """ Returns all items in the same meal, sorted by time """
        meals = defaultdict(list)
        for item in item_rows:
            meals[item.meal].append(item)

        for meal in meals.values():
            meal.sort(key=attrgetter('time'))

        return sorted(meals.values(), key=lambda x:x[0].time)

    def print_item_rows(self, item_rows):

        meals = self.sorted_items_by_meal(item_rows)
        for meal in meals:
            self.print_meal(meal)
        print_total(meals)


    def print_meal(self, meal):
        dish = meal[0]
        print FIRST_IN_MEAL_TEMPLATE.format(
            **self.course_dict(dish, meal=dish.meal, courses=len(meal)))
        for dish in meal[1:]:
            print OTHERS_IN_MEAL_TEMPLATE.format(**self.course_dict(dish))

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


def safe_by_servings(val, servings=1):
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
    editgroup = parser.add_mutually_exclusive_group()
    editgroup.add_argument("--edit", action="store_false", dest="readonly")
    editgroup.add_argument("--readonly", action="store_true")
    dategroup = parser.add_mutually_exclusive_group()
    dategroup.add_argument("--now", "--current", "-n", action="store_true")
    dategroup.add_argument("--previous", "-p", type=int, choices=xrange(20))
    dategroup.add_argument("--last_week", "-w", action='store_true')
    parser.add_argument("--cgi", required=True)
    parser.add_argument("--start_date",
        type=lambda s:datetime.strptime(s, "%Y-%m-%d").date(), default=date.min)
    parser.add_argument("--end_date", default=date.max,
        type=lambda s:datetime.strptime(s, "%Y-%m-%d").date())
    args = parser.parse_args()
    if not args.readonly and not args.cgi:
        parser.print_help()

    start_date, stop_date = get_dates(args)


    ConstructWebPage(args.sqlite_file, args.readonly, args.cgi).output(
        start_date, stop_date)

if __name__ == '__main__':
    main()