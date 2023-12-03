import shutil, os, glob
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import markdown

if os.path.isdir('dist'):
    shutil.rmtree('dist')
os.mkdir('dist')

content = dict()
md_fpaths = glob.glob('content/*.md')
for fpath in md_fpaths:
    key = os.path.basename(fpath)[:-3]
    with open(fpath) as fhandle:
        md_string = fhandle.read()
    content[key] = markdown(md_string)

## maybe each article should be an object with html attached, and front matter
## this way we can also access children

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape()
)

template = env.get_template('index.html')

html = template.render(content=content)

with open('dist/index.html', 'w') as fhandle:
    fhandle.write(html)

## copy images to dist 
for fpath in glob.glob('static/*.jpg'):
    shutil.copy(fpath, 'dist/')

## copy css file
shutil.copy('styles/index.css', 'dist/styles.css')
