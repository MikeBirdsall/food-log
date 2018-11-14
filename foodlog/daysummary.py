#!/usr/bin/env python3
""" Create dynamic report for foodlog with daily summary only.

    The general appearance of the report will be (whether text or http)

    | DayDate | Cals | Carbs | Fat | Protein |
    |---------|------|-------|-----|---------|
    | Date1   | nn   | nn    | nn  | nn      |
    | Date2   | nn+? | nn?!  | nn  | nn      |
    | Date3   | nn   | nn    |     | nn      |
    | Total   | NN+? | NN?!  | NN+?| NN      |
    | Average | NN-  | NN-   | NN- | NN      |

    Where
        nn and NN are numeric values,
        +? indicates that there is a missing value
        ?! indicates a bad value (not a good number)
        -  indicates that the Average is missing some data

    The Total is created from all numeric values available,
    and thus is at least a minimal Total.
    The Average is taken from days which had a valid value,
    which is to say no missing or bad value



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
from datetime import date, datetime, timedelta
import sqlite3
from my_info import config_path


ITEM = namedtuple('item', 'carbs servings calories fat day protein')

INVALID_TEMPLATE = """Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
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

def namedtuple_factory(cursor, row):
    """ sqlite3 rows as named tuples

        Usage connection.row_factory = namedtuple_factory
    """
    fields = [col[0] for col in cursor.description]
    Row = namedtuple('Row', fields)
    return Row(*row)

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

class Nutrient:

    def __init__(self, name):
        self.missing_values = False
        self.bad_values = False
        self.total = 0.0
        self.name = name

    def add_nutrient(self, other):
        """ add other Nutrient to self """
        self.missing_values = self.missing_values or other.missing_values
        self.bad_values = self.bad_values or other.bad_values
        self.total += other.total

    def addin(self, value, servings):
        """ Add in numeric, otherwise set missing or illegal attribute """
        if value in (None, ''):
            self.missing_values = True
        else:
            try:
                self.total += value * servings
            except ValueError:
                self.bad_values = True

    def __str__(self):
        return self.notated_value()

    def notated_value(self):
        value = "{:.1f}".format(self.total).rstrip('0').rstrip('.')
        missing_flag = "+?" if self.missing_values else ""
        bad_flag = "??!!" if self.bad_values else ""
        return "{}{}{}".format(value, missing_flag, bad_flag)

NUTRIENTS = 'calories carbs fat protein'.split()

class TotalNutrition:
    """ Holds aggregated total or average nutrition for a time period

        If average,
            title is Average, has count of days averaged for each nutrient
        If total for day,
            title is the day string YYYY-MM-DD
        If total for date range
            title is "Total"

    """

    def __init__(self):
        self.which = {}
        self.title = ""
        self.points_in_average = {}
        for nutrient in NUTRIENTS:
            self.which[nutrient] = Nutrient(nutrient)
            self.points_in_average[nutrient] = 0

    def add_total_nutrition(self, other):
        """ Add nutrient values in from another TotalNutrition object """
        for nutrient in other.which:
            self.which[nutrient].add_nutrient(other.which[nutrient])

    def add_nutrition(self, dish):
        """ Add nutrient values in from mapping """
        self.title = dish.day
        for nutrient in NUTRIENTS:
            self.which[nutrient].addin(getattr(dish, nutrient), dish.servings)

    def scale(self):
        for nutrient in NUTRIENTS:
            if self.points_in_average[nutrient] != 0:
                self.which[nutrient].total /= self.points_in_average[nutrient]

    def set_title(self, title):
        self.title = title

    def accumulate_average(self, day):
        """ Add valid nutrient values from a daily TotalNutrition object

        """
        for nutrient in day.which.values():
            if not (nutrient.missing_values or nutrient.bad_values):
                self.which[nutrient.name].addin(nutrient.total, servings=1)
                self.points_in_average[nutrient.name] += 1

    def as_dict(self):
        return {x: y.notated_value() for x, y in self.which.items()}

    def totals(self):
        return [self.which[n].notated_value() for n in NUTRIENTS]

class Summary:
    """ Summary of nutrition intake over time range

        Track daily totals, overall total, and average
        Deals with incomplete or faulty data.

        methods:
            calc - recalculates from the database
        """

    def __init__(self, database, start_date, end_date):
        self.database = database
        self.start_date = start_date
        self.end_date = end_date
        self.total = None
        self.average = None
        self.days = None
        self.days_total_nutrition = None
        self.calc()

    def calc(self):
        self.total = None
        self.average = None
        self.calc_days()
        self.calc_total()
        self.calc_average()

    def calc_days(self):
        """ Calculate daily sums of nutrients """
        days = self.days_total_nutrition = defaultdict(TotalNutrition)

        with sqlite3.connect(self.database) as conn:
            conn.row_factory = namedtuple_factory
            cursor = conn.cursor()

            cursor.execute("""select
                servings, calories, fat, protein, carbs, day
                from course
                where day between ? and ? order by day, time""",
                (self.start_date, self.end_date))

            for course in cursor:
                days[course.day].add_nutrition(course)

        # List of dicts of nutrients and date
        self.days = []
        for _ignore, day in sorted(days.items()):
            row = dict()
            row['date'] = day.title
            row.update(day.which)
            self.days.append(row)


    def calc_total(self):
        total = self.total = TotalNutrition()
        total.title = "Total"
        for day_n in self.days_total_nutrition.values():
            total.add_total_nutrition(day_n)

    def calc_average(self):
        average = self.average = TotalNutrition()
        average.title = "Average"
        for day_n in self.days_total_nutrition.values():
            average.accumulate_average(day_n)
        average.scale()


    def __str__(self):
        answer = []
        answer.append(
            "{:>11} {:>7} {:>6} {:>6} {:>6}".format(
            "Date", "Cals", "Carbs", "Fat", "Protein"))
        for x, row in (
            (x, self.days_total_nutrition[x])
            for x in sorted(self.days_total_nutrition)
        ):
            nutes = row.as_dict()
            nutes['date'] = x
            answer.append(
                "{date:11}: {calories:7} {carbs:6} {fat:6} {protein:6}".format(
                    **nutes))
        nutes = self.total.as_dict()
        nutes['date'] = "Total"
        answer.append(
            "{date:11}: {calories:7} {carbs:6} {fat:6} {protein:6}".format(
                **nutes))

        nutes = self.average.as_dict()
        nutes['date'] = "Average"
        answer.append(
            "{date:11}: {calories:7} {carbs:6} {fat:6} {protein:6}".format(
                **nutes))

        return "\n".join(answer)

def decorated_nutrient(nutrient, places=0):
    """ Writes nutrients coded for missing or bad values

        nutrient has float value, bool missing_values and bad_values
        return rounded string with flags for missing or bad
    """

    valstring = "{{:.{}f}}".format(places)
    value = valstring.format(nutrient.total)
    missing_flag = "+?" if nutrient.missing_values else ""
    bad_flag = "??!!" if nutrient.bad_values else ""
    return "{}{}{}".format(value, missing_flag, bad_flag)

def print_row(title_, nutrients):
    rowformat = "{title:11} {calories:7} {carbs:6} {fat:6} {protein:6}"
    row = dict(title=title_)
    for nutrient in NUTRIENTS:
        row[nutrient] = decorated_nutrient(nutrients[nutrient])
    print(rowformat.format(**row))

def main():

    if not DB_FILE or ";" in DB_FILE:
        print_error("PROBLEM WITH DATABASE", DB_FILE)

    args = get_args()
    start_date, stop_date = get_dates(args)


    bareformat = "{:11} {:7} {:6} {:6} {:6}"
    summary = Summary(DB_FILE, start_date, stop_date)
    headers = "Date Cals Carbs Fat Protein".split()
    print(bareformat.format(*headers))

    for day in summary.days:
        print_row(day['date'], day)

    print_row("Total", summary.total.which)
    print_row("Average", summary.average.which)
    print(bareformat.format(
        "Points",
        summary.average.points_in_average['calories'],
        summary.average.points_in_average['carbs'],
        summary.average.points_in_average['fat'],
        summary.average.points_in_average['protein'])
    )

if __name__ == '__main__':
    main()
