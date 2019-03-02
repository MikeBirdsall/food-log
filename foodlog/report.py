#!/usr/bin/env python3
""" Create dynamic report for foodlog

    Runs as cgi-bin from a browser

    Intended at start to work with URLs of the form

    http://...?start=mm/dd/yyyy;end=mm/dd/yyyy
    http://...?range=today
    http://...?range=yesterday
    ...

"""
import cgitb; cgitb.enable() # pylint: disable=C0321
import sys
from collections import namedtuple, OrderedDict
from datetime import date, datetime, timedelta
import sqlite3
from jinja2 import Environment, FileSystemLoader
from foodlog.my_info import config_path
from foodlog.templates import INVALID_TEMPLATE

ITEM = namedtuple('item', 'id comment carbs description servings calories fat '
    'day time protein meal size ini_id thumb_id')

config = config_path() # pylint: disable=invalid-name
DB_FILE = config.dir('DB_FILE')
MENU_URL = config.dir('MENU_URL')
VIEW_MENU_URL = config.dir('VIEW_MENU_URL')


IGNORE = set('template cmd'.split())
VALID = set('start end range title reverse edit dieter'.split())
VALID_RANGES = set('today yesterday lastweek thisweek'.split())

def dateformat(value, format="%A %Y-%m-%d"):
        return value.strftime(format)

def print_error(header, text):
    print(INVALID_TEMPLATE.format(header, text))
    sys.exit(0)

def datespan(first, last):
    """ Return sequence of dates from first to last inclusive """
    return (first + timedelta(n)
        for n in range(0, (last-first).days+1, 1 if first < last else -1))

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

def get_args(form):

    args = {}
    params = set(form.keys())
    params = params - IGNORE
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

    def __init__(self):
        self.missing_values = False
        self.bad_values = False
        self.total = 0.0

    def addin(self, value, servings):
        """ Add in numeric, otherwise set missing or illegal attribute """
        if value in (None, ''):
            self.missing_values = True
        else:
            try:
                self.total += value * servings
            except ValueError:
                self.bad_values = True

    def notated_value(self):
        value = "{:.1f}".format(self.total).rstrip('0').rstrip('.')
        missing_flag = "+?" if self.missing_values else ""
        bad_flag = "??!!" if self.bad_values else ""
        return "{}{}{}".format(value, missing_flag, bad_flag)

NUTRIENTS = 'calories carbs fat protein'.split()

class TotalNutrition:

    def __init__(self):
        self.which = {}
        for nutrient in NUTRIENTS:
            self.which[nutrient] = Nutrient()

    def add_nutrition(self, dish):
        for nutrient in NUTRIENTS:
            self.which[nutrient].addin(getattr(dish, nutrient), dish.servings)

    def totals(self):
        return {n:self.which[n].notated_value() for n in NUTRIENTS}

class ConstructWebPage:

    def __init__(self, database):
        self.database = database
        self.readonly = True # default
        self.start_date = None
        self.end_date = None
        self.page_content = []
        self.reverse = False
        self.title = ""
        self.user = None
        self.dieter = None

    def output(self, user, start_date, end_date, reverse, title, dieter):
        self.user = user
        self.start_date = start_date
        self.end_date = end_date
        self.reverse = bool(int(reverse))
        self.title = title
        self.dieter = dieter
        if self.user:
            foodmenu = MENU_URL
            self.readonly = False
        else:
            foodmenu = VIEW_MENU_URL
            self.readonly = True

        days = []

        days = self.fill_rows()

        input_ = dict(
            start=start_date,
            end=end_date,
            now=datetime.now().date(),
            edit_view="edit" if self.readonly else "view",
            foodmenu=foodmenu,
            title=title,
            days=days,
        )

        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        env.filters['dateformat'] = dateformat
        template = env.get_template('report.html')
        output = template.render(input_)
        print(output)

    def fill_rows(self):
        mealsinorder = OrderedDict() # date, meal in first course order
        answer = list(dict(date=x, total={}, meals=[])
            for x in datespan(self.start_date, self.end_date))
        answer_index = {x['date']:x for x in answer}
        running_totals = {x['date']:TotalNutrition() for x in answer}

        target_user = self.user or self.dieter
        line = '''select id, description, comment, servings,
            calories, fat, protein, carbs, day, time, meal, size, ini_id,
            thumb_id
            from course
            where
              dieter = ? and
              day between ? and ?
            order by day, time'''
        fields = (target_user, self.start_date, self.end_date)

        with sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(line, fields)

            # Organize ordered day/meal list of items
            for course in cursor.fetchall():
                fitem = ITEM(**course)
                index = (fitem.day, fitem.meal)
                if index not in mealsinorder:
                    mealsinorder[index] = []
                mealsinorder[index].append(fitem)

        # Fill in answer
        for meal, courses in mealsinorder.items():
            courselist = []
            m0 = meal[0]                  # daystring from database
            m1 = meal[1]                  # mealstring from database
            temp1 = answer_index[m0]      # dict with date, total, and meals for day m0
            temp2 = temp1['meals']        # meals for day m0
            temp2.append((m1, courselist)) # add tuple with mealname and empty list of courses
            # answer_index[meal[0]]['meals'].append((meal[1], courselist))
            for course in courses:       # named tuple ITEM for each course
                running_totals[meal[0]].add_nutrition(course)
                courselist.append(dict(
                    dish=course.description,
                    servings=course.servings,
                    calories=course.calories,
                    carbs=course.carbs,
                    fat=course.fat,
                    protein=course.protein)
                )

        # fill in totals
        for day, entry in answer_index.items():
            rtd = running_totals[day]
            z = dict(
                calories=rtd.which['calories'].notated_value(),
                carbs=rtd.which['carbs'].notated_value(),
                fat=rtd.which['fat'].notated_value(),
                protein=rtd.which['protein'].notated_value(),
            )
            entry['total'] = z
        return answer

class Report:

    def __init__(self, form, user):
        if not DB_FILE or ";" in DB_FILE:
            print_error("PROBLEM WITH DATABASE", DB_FILE)

        args = get_args(form)
        start_date, stop_date = get_dates(args)

        ConstructWebPage(
            DB_FILE,
        ).output(
            user,
            start_date,
            stop_date,
            args.get('reverse', 0),
            args.get('title') or "Food Log",
            args.get('dieter') or "")


