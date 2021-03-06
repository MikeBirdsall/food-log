#!/usr/bin/python3

from datetime import date
from jinja2 import Environment, FileSystemLoader

def spacenone(value):
    return "" if value is None else str(value)

def dateformat(value, format='%A %Y-%m-%d'):
    return value.strftime(format)

days = [
    dict( # First Day
        date=date(2019, 1, 1),
        total=dict(
            calories=550,
            carbs=48,
            fat=30,
            protein=28,
            ),
        meals=[
            ("Breakfast", [
                dict(
                    dish="Half Corned Beef Hash, poached eggs, toast and coffee",
                    id=10,
                    servings=1,
                    calories=550,
                    carbs=48,
                    fat=30,
                    protein=28,
                    )
                ],
            )
        ],
    ),
    dict( # Second Day
        date=date(2019, 1, 2),
        total=dict(
            calories="675+?",
            carbs=104,
            fat=59,
            protein="84+?",
            ),
        meals=[
            ("Breakfast", [            # First Meal
                dict(
                    id=20,
                    dish="Donut SMP",
                    servings=1,
                    calories=225,
                    carbs=26,
                    fat=12,
                    protein=28,
                    )
                ]
            ),
            ("Lunch", [                # Second Meal
                dict(                  # First Course
                    dish="First course of second meal",
                    id=39,
                    servings=1,
                    calories=225,
                    carbs=26,
                    fat=12,
                    protein=28,
                    ),
                dict(                  # Second Course
                    dish="Second course of second meal, but a much longer "
                        "description than earlier ones, so it gets "
                        "truncated",
                    id=40,
                    servings=1,
                    calories=225,
                    carbs=26,
                    fat=12,
                    protein=28,
                    ),
                ],
            ),
            ("Supper", [                # Third Meal
                dict(
                    id=44,
                    dish="",
                    servings=1,
                    calories="",
                    carbs=26,
                    fat=23,
                    protein="",
                ),
                dict(
                    id=44,
                    dish="Includes None in values for carbs and fat",
                    servings=1,
                    calories="",
                    carbs=None,
                    fat=None,
                    protein="",
                ),
                ]
            )
        ]
    ),
    dict( # Third Day
        date=date(2019, 1, 3),
        )
    ]

input_ = dict(
    start="2018-02-24",
    end="2018-02-25",
    now="2018-02-27",
    reverse=True,
    title="Food Record 2018-02-24 - 2018-02-27",
    h1="Food Log",
    cmd="detail",
    days=days,
)

file_loader = FileSystemLoader('..')
env = Environment(loader=file_loader)
env.filters['dateformat'] = dateformat
env.filters['spacenone'] = spacenone
template = env.get_template("report.html")

output = template.render(input_)

print(output)

