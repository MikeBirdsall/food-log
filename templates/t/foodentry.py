from jinja2 import Environment, FileSystemLoader

file_loader = FileSystemLoader('..')
env = Environment(loader=file_loader)

template = env.get_template('foodentry.html')

output = template.render(
    title='Page Title',
    body='Stuff'
    )
print(output)
