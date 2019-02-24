#!/usr/bin/python3

from jinja2 import Environment, FileSystemLoader

EDIT_CSS = """\
      input.calc {
        width:130px;
        visibility:hidden;
      }

      button.ifedit {
          visibility:hidden;
      }
"""


input_ = dict(
    SCRIPT_NAME="/foodlog/view/run.py",
    STATUS="------------",
    title="View Course Info",
    h1="Food Entry",
    EDIT_CSS=EDIT_CSS,
    disabled="disabled",

    id=2125,
    description="Grilled Chicken Salad",
    comment="Gus's",
    calories=310,
    carbs=14,
    protein=47,
    fat=9,
    servings=1,
    day="2019-02-12",
    time="13:27",
    meal="Lunch",
    )

file_loader = FileSystemLoader('..')
env = Environment(loader=file_loader)

template = env.get_template('mealdetail.html')


output = template.render(input_)

print(output)

