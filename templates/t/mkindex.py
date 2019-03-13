#!/usr/bin/python3

import sys
import argparse
from datetime import datetime, date, timedelta
from jinja2 import Environment, FileSystemLoader

class week:

    def __init__(self, firstweekday=0):
        self.firstweekday = firstweekday
        self.start = None
        self.end = None

    def week_containing(self, include):
        new_week_day = (include.weekday() - self.firstweekday) % 7
        self.start = include - timedelta(days=new_week_day)
        self.end = self.start + timedelta(days=6)
        return self

    def next_week(self):
        self.start += timedelta(weeks=1)
        self.end += timedelta(weeks=1)
        return self

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def main():

    parser = argparse.ArgumentParser(
        description="Create dietitian index.html file")
    parser.add_argument("--dieter", '-d', type=str, required=True,
        help="id of dieter")
    parser.add_argument("--name", '-n', type=str,
        help="Long name for dieter")
    # Don't have dateutil on my hosting service, so we'll stick with datetime
    parser.add_argument("--last", '-l', type=valid_date, required=True,
        help="Last day included in weeks")
    parser.add_argument("--first", '-f', type=valid_date, required=True,
        help="First day included in weeks")

    args = parser.parse_args()

    reports = []

    input_ = dict(
        title="Food Log Menu",
        h1="{} Food Records".format(args.name),
        dieter=args.dieter,
        reports=reports
        )

    reports.extend(
        [
            dict(prompt="This Week", range="thisweek"),
            dict(prompt="Last Week", range="lastweek")
        ])

    # Put in buttons for weeks from some start date to some end date
    # Will eventually get them from as input, but for now hard code
    #start_date = date.today() - timedelta(weeks=3)
    #end_date = start_date + timedelta(days=54)
    start_date = args.first
    end_date = args.last

    # Get every week range (starting on Thursday - 3) that included some date
    # in the range, particularly the first and last date:

    weeknum = 1
    this_week = week(firstweekday=3)
    this_week.week_containing(start_date)
    while this_week.start <= end_date:
        prompt = "Week {}".format(weeknum)
        reports.append(
            dict(start=this_week.start, end=this_week.end, prompt=prompt)
        )
        weeknum += 1
        this_week.next_week()

    reports.append(dict(prompt="Full List", reverse=True))

    file_loader = FileSystemLoader('..')
    env = Environment(loader=file_loader)

    template = env.get_template('mkindex.html')
    output = template.render(input_)
    print(output)

if __name__ == "__main__":
    main()

