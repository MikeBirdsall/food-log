#!/usr/bin/python3

from jinja2 import Environment, FileSystemLoader

EDIT_CSS = """\
      input.calc {
        width:130px;
      }
"""


input_ = dict(
    TITLE="Search for Courses",
    h1="Full Text Search",
    status=("Ready For Search"),
    EDIT_CSS=EDIT_CSS
)

file_loader = FileSystemLoader('..')
env = Environment(loader=file_loader)

template = env.get_template('search.html')

output = template.render(input_)

print(output)


