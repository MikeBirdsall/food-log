#!/usr/bin/env python3
""" Create dynamic report for foodlog

    Runs as cgi-bin from a browser

    Intended at start to work with URLs of the form

    http://...?start=mm/dd/yyyy;end=mm/dd/yyyy
    http://...?range=today
    http://...?range=yesterday
    ...

"""
import cgi
import cgitb; cgitb.enable() # pylint: disable=C0321
import sys
from collections import defaultdict, namedtuple
from operator import attrgetter
from datetime import date, datetime, timedelta
import sqlite3
from my_info import config_path

ITEM = namedtuple('item', 'id comment carbs description servings calories fat '
    'day time protein meal size ini_id thumb_id')

INVALID_TEMPLATE = """Content-Type: text/html

<!DOCTYPE html>
<html>
  <head>
  <title>Invalid Parameters</title>
  <meta name="viewport" content="width-device-width, initial-scale=1" />
  </head>
  <body>
    <h1>{}</h1>
    {}
  </body>
</html>
"""

HEAD_TEMPLATE = """Content-Type: text/html

<!DOCTYPE html>
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
      button {{
          background: #db8c47;
      }}
    </style>
  </head>
  <body>
    <h1>{title}</h1>
    <h2>{start} - {end}</h2>
    <form method="get">
        <button formaction="{foodmenu}">Food Menu</button>
    </form>
    <table>"""

AFTERWARD_TEMPLATE = """</table>
    <form method="get">
        <button formaction="{foodmenu}">Food Menu</button>
    </form>
    recomputed on {now}
  </body>
</html>"""

DAY_HEADER_TEMPLATE = """<tr>
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

NUTRITION_TEMPLATE = """<td>{dish}</td>
        <td>{servings}</td>
        <td>{calories}</td>
        <td>{carbs}</td>
        <td>{fat}</td>
        <td>{protein}</td>
"""

OTHERS_IN_MEAL_TEMPLATE = """<tr>
""" + NUTRITION_TEMPLATE + """</tr>"""

FIRST_IN_MEAL_TEMPLATE = """<tr><th rowspan="{courses}">{meal}</th>
""" + NUTRITION_TEMPLATE + """</tr>"""

TOTAL_TEMPLATE = """<tr>
        <th colspan="3">Total</th>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>
"""




config = config_path() # pylint: disable=invalid-name
DB_FILE = config.dir('DB_FILE')
MENU_URL = config.dir('MENU_URL')
VIEW_MENU_URL = config.dir('VIEW_MENU_URL')


VALID = set('start end range title reverse edit'.split())
VALID_RANGES = set('today yesterday lastweek thisweek'.split())

def print_error(header, text):
    print(INVALID_TEMPLATE.format(header, text))
    sys.exit(0)

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
    if 'range' in args:
        range_key = args['range']
        if range_key == 'today':
            which = date.today()
            return which, which
        elif range_key == 'yesterday':
            which = date.today() - timedelta(days=1)
            return which, which
        elif range_key == 'lastweek':
            return week_range(1)
        elif range_key == 'thisweek':
            return week_range(0)
        else:
            print_error("Program Error:",
                "Error handling range {}".format(args['range']))
    else:
        return (
            args.get('start') or (
                # First day of previous month
                date.today().replace(day=1) - timedelta(days=1)
                ).replace(day=1),
            args.get('end') or date.today())

def add_with_none(now, new, servings):
    if new in (None, ''):
        return (now[0], "+?")
    elif new == '':
        print_error("----", "Bad value: new:%s" % new)
        return (now[0], "+?")
    else:
        try:
            return (now[0] + (float(new) * float(servings)), now[1])
        except ValueError:
            print_error(
                "add_with_none",
                "Bad value: total:%s, new:%s, servings:%s" %
                (now[0], new, servings))
            return (now[0], "??%s" % (new))


def get_args():

    args = {}
    form = cgi.FieldStorage()
    params = set(form.keys())
    invalid = params - VALID
    valid = params - invalid
    if invalid:
        print_error("Invalid parameters:", invalid)


    for key in valid:
        args[key] = form.getfirst(key)

    # Check for incompatible params
    if 'range' in args and ('start' in args or 'end' in args):
        print_error("Incompatible parameters",
            "Cannot mix range and start or end")

    if 'range' in args and args['range'] not in VALID_RANGES:
        print_error("Invalid parameters:",
            "{} is not a valid value for range".format(args['range']))

    # Check that start and end are valid dates
    # Todo investigate importing dateutil.parser using venv
    for date_ in [x for x in ['start', 'end'] if x in args]:
        try:
            args[date_] = datetime.strptime(args[date_], "%Y-%m-%d").date()
        except ValueError:
            print_error("Bad date",
                "Date {} should be YYYY-MM-DD".format(args[date_]))

    return args

class ConstructWebPage():

    def __init__(self, database, readonly):
        self.database = database
        self.readonly = bool(int(readonly))
        self.start_date = None
        self.end_date = None
        self.page_content = []
        self.reverse = False
        self.title = ""

    def output(self, start_date, end_date, reverse, title):
        self.start_date = start_date
        self.end_date = end_date
        self.reverse = bool(int(reverse))
        self.title = title
        if self.readonly:
            foodmenu = VIEW_MENU_URL
        else:
            foodmenu = MENU_URL

        self.page_content.append(HEAD_TEMPLATE.format(
            start=start_date,
            end=end_date,
            foodmenu=foodmenu,
            title=title))

        self.print_rows()
        self.page_content.append(
            AFTERWARD_TEMPLATE.format(
            now=datetime.now().date(),
            foodmenu=foodmenu))

        for chunk in self.page_content:
            print(chunk)

    def print_rows(self):
        items = dict()
        days = defaultdict(list)
        with sqlite3.connect(self.database) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''select id, description, comment, servings,
                calories, fat, protein, carbs, day, time, meal, size, ini_id,
                thumb_id
                from course
                where day between ? and ? order by day, time''',
                (self.start_date, self.end_date))

            for course in cursor.fetchall():
                fitem = ITEM(**course)
                items[fitem.id] = fitem
                days[fitem.day].append(fitem.id)

            for day, item_id_list in sorted(
                    days.items(), reverse=self.reverse):
                meal_date = datetime.strptime(day, "%Y-%m-%d").strftime(
                    "%A %Y-%m-%d")
                self.page_content.append(DAY_HEADER_TEMPLATE.format(
                    date=meal_date))
                self.print_item_rows([value for key, value in items.items()
                    if key in item_id_list])

    def print_item_rows(self, item_rows):

        meals = self.sorted_items_by_meal(item_rows)
        for meal in meals:
            self.print_meal(meal)
        self.print_total(meals)

    def detail_or_edit_url(self, dish, bold=False):
        """ Return Link to detail or edit page for item """

        label = ellipse_truncate(dish.description)
        if bold:
            label = "<strong>{}</strong>".format(label)
        script = "detail.py" if self.readonly else "edit.py"
        return '<a href="./{script}?id={id}">{label}</a>'.format(
            script=script, label=label, id=dish.id)

    def course_dict(self, dish, **kwargs):
        answer = dict()
        for key, value in kwargs.items():
            answer[key] = value
        bold = dish.thumb_id is not None
        answer['dish'] = self.detail_or_edit_url(dish, bold=bold)
        for field in "calories carbs fat protein".split():
            answer[field] = safe_by_servings(getattr(dish, field, None),
                dish.servings)
        answer['servings'] = safe_by_servings(dish.servings)

        return answer

    def sorted_items_by_meal(self, item_rows):
        """ Returns all items in the same meal, sorted by time """
        meals = defaultdict(list)
        for item in item_rows:
            meals[item.meal].append(item)

        for meal in meals.values():
            meal.sort(key=attrgetter('time'))

        return sorted(meals.values(), key=lambda x: x[0].time)

    def print_meal(self, meal):
        dish = meal[0]
        self.page_content.append(FIRST_IN_MEAL_TEMPLATE.format(
            **self.course_dict(dish, meal=dish.meal, courses=len(meal))))
        for dish in meal[1:]:
            self.page_content.append(
                OTHERS_IN_MEAL_TEMPLATE.format(**self.course_dict(dish))
            )

    def print_total(self, meals):
        """ Print total row for entire day"""
        cals = carbs = fat = protein = (0, "")
        for meal in meals:
            for dish in meal:
                cals = add_with_none(cals, dish.calories, dish.servings)
                carbs = add_with_none(carbs, dish.carbs, dish.servings)
                fat = add_with_none(fat, dish.fat, dish.servings)
                protein = add_with_none(protein, dish.protein, dish.servings)

    # pylint:disable=W0141
        self.page_content.append(
            TOTAL_TEMPLATE % (
            ''.join(map(str, cals)),
            ''.join(map(str, carbs)),
            ''.join(map(str, fat)),
            ''.join(map(str, protein))))

def safe_by_servings(val, servings=1):
    if val is None:
        return ""
    return val * servings

def ellipse_truncate(text, length=40):
    """ Return canonical form of description to fit in length """
    result = text or "No Description Yet"
    return (result[:length-1] + "&hellip;") if len(result) > length else result


def main():

    if not DB_FILE or ";" in DB_FILE:
        print_error("PROBLEM WITH DATABASE", DB_FILE)

    args = get_args()
    start_date, stop_date = get_dates(args)

    ConstructWebPage(
        DB_FILE,
        not args.get('edit', 0),
    ).output(
        start_date,
        stop_date,
        args.get('reverse', 0),
        args.get('title') or "Food Log")


if __name__ == '__main__':
    main()
