#!/usr/bin/python3

from jinja2 import Environment, FileSystemLoader



templates = [
    dict(id=1, description="Cereal"),
    dict(id=2, description="HMR 800"),
    ]
input_ = dict(
    title="Create Course From Template",
    h1="Choose Template",
    templates=templates,
    )

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("picktemplate.html")


output = template.render(input_)

print(output)

