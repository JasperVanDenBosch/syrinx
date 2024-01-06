from __future__ import annotations
from typing import List, Dict
from os.path import abspath, dirname, isdir, basename, join
import shutil, os, glob
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import markdown
import sys

class ContentNode:
    name: str
    children: List[ContentNode]
    content_html: str
    front: Dict[str, str]
    out_fpath: str

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
tree: Dict[str, ContentNode] = dict()
root = ContentNode()
root.name = ''
for (dirpath, dirnames, fnames) in os.walk(content_dir):
    out_dir = dirpath.replace(content_dir, dist_dir)
    os.makedirs(out_dir, exist_ok=True)

    ## ideally process the index page first (not sure if this is necessary?)
    index_index = fnames.index('index.md')
    fnames.insert(0, fnames.pop(index_index))

    
    indexNode = ContentNode()
    indexNode.name = basename(dirpath)
    if dirpath == content_dir:
        indexNode = root
    else:
        parent = tree[dirname(dirpath)]
        parent.children.append(indexNode)
    tree[dirpath] = indexNode
    for fname in fnames:
        name = fname.split('.')[0]

        in_fpath = join(dirpath, fname)
        out_fpath = join(out_dir, fname.replace('.md', '.html'))

        with open(in_fpath) as fhandle:
            lines = fhandle.readlines()

        markers = [l for (l, line) in enumerate(lines) if line.strip() == '---']
        assert len(markers) == 2
        fm_lines = [line.strip() for line in lines[1:markers[1]]]
        fm_dict = dict()
        for line in fm_lines:
            parts = line.split(':')
            key = parts[0]
            val = line[(len(key)+1):].strip()
            fm_dict[key] = val

        md_content = ''.join(lines[markers[1]:])

        if name == 'index':
            node = indexNode
        else:
            node = ContentNode()
            node.name = name
            indexNode.children.append(node)
        
        node.out_fpath = out_fpath
        node.children = []
        node.front = fm_dict
        node.content_html = markdown(md_content)

        


def build_node(node: ContentNode, root: ContentNode):
    html = page_template.render(node=node, root=root)
    with open(node.out_fpath, 'w') as fhandle:
        fhandle.write(html)
    for child in node.children:
        build_node(child, root)


build_node(root, root)


# ## copy images to dist 
# for fpath in glob.glob('static/*.jpg'):
#     shutil.copy(fpath, 'dist/')

# ## copy css file
# shutil.copy('styles/index.css', 'dist/styles.css')
