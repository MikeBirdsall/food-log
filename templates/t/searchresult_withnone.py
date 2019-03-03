#!/usr/bin/python3

from jinja2 import Environment, FileSystemLoader

results = [
    dict(
        description="Noodles and Company steak Stromboli",
        comment="",
        size="small",
        cals=530,
        carbs=50,
        fat=25,
        protein=27,
        score=30),

    dict(
        description="Steak sandwich",
        comment="",
        size="4 oz and bun",
        cals=480,
        carbs=44,
        fat=20,
        protein=27,
        score=30),
    dict(
        description="chipotle tacos",
        comment="Steak, no beans, gu...",
        size="",
        cals=285,
        carbs=None,
        fat=16,
        protein=None,
        score=30),
    dict(
        description="Steak Sandwich",
        comment="",
        size="",
        cals=380,
        carbs=45,
        fat=3.5,
        protein=34,
        score=30),
    ]
input_ = dict(
    title="Search for Courses",
    h1="Full Text Search: steak NOT shake",
    results=results,
    )

env = Environment(loader=FileSystemLoader(".."))
template = env.get_template("searchresult.html")


output = template.render(input_)

print(output)

