#!/usr/bin/python3

from jinja2 import Environment, FileSystemLoader

EDIT_CSS = """\
      input.calc {
        width:130px;
      }
"""


input_ = dict(
    SCRIPT_NAME="/foodlog/edit/run.py",
    STATUS="Ready to Edit",
    title="Edit Course Detail",
    h1="Edit Food Entry",
    EDIT_CSS=EDIT_CSS,
    disabled="",

    id=2125,
    description="Grilled Chicken Salad",
    comment="Gus's",
    calories=None,
    carbs=14,
    protein=47,
    fat=9,
    servings=1,
    day="2019-02-12",
    time="13:27",
    meal="Lunch",
    image="/tmp/thumbs/testimage1.jpg"
    )

file_loader = FileSystemLoader('..')
env = Environment(loader=file_loader)

template = env.get_template('editdetail.html')


output = template.render(input_)

print(output)

