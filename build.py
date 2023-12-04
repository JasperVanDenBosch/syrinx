from __future__ import annotations
from os.path import abspath, relpath, isdir, basename, join
import shutil, os, glob
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import markdown
import sys

root_dir = abspath(sys.argv[1])
assert isdir(root_dir)
content_dir = join(root_dir, 'content')
template_dir = join(root_dir, 'theme')
dist_dir = join(root_dir, 'dist')

if isdir(dist_dir):
    shutil.rmtree(dist_dir)
os.makedirs(dist_dir, exist_ok=True)

env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape()
)
page_template = env.get_template('page.jinja2')


## maybe each article should be an object with html attached, and front matter
## this way we can also access children

for (dirpath, dirnames, fnames) in os.walk(content_dir):
    out_dir = dirpath.replace(content_dir, dist_dir)
    os.makedirs(out_dir, exist_ok=True)
    
    for fname in fnames:
        in_fpath = join(dirpath, fname)
        out_fpath = join(out_dir, fname.replace('.md', '.html'))

        with open(in_fpath) as fhandle:
            md_string = fhandle.read()
        content_html = markdown(md_string)
        html = page_template.render(content=content_html)
        with open(out_fpath, 'w') as fhandle:
            fhandle.write(html)



# ## copy images to dist 
# for fpath in glob.glob('static/*.jpg'):
#     shutil.copy(fpath, 'dist/')

# ## copy css file
# shutil.copy('styles/index.css', 'dist/styles.css')
