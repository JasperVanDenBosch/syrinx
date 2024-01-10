from __future__ import annotations
from typing import List, Dict, TYPE_CHECKING
from os.path import abspath, dirname, isdir, basename, join
import shutil, os
from jinja2 import Environment, FileSystemLoader, select_autoescape
if TYPE_CHECKING:
    from syrinx.read import ContentNode

def build(root: ContentNode, root_dir: str):

    assert isdir(root_dir)


    ## TODO: preprocess adds archetype to frontmatter; build can use this to match template
    ## can distinguish page template from section/fragment template
            
    ## ready templated
    theme_dir = join(root_dir, 'theme')
    env = Environment(
        loader=FileSystemLoader(theme_dir),
        autoescape=select_autoescape()
    )
    page_template = env.get_template('page.jinja2')

    ## locate and clear target directory
    dist_dir = join(root_dir, 'dist')
    if isdir(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)


    def build_node(node: ContentNode, root: ContentNode, parent_path: str):
        html = page_template.render(node=node, root=root)
        node_path = join(parent_path, node.name)
        os.makedirs(node_path, exist_ok=True)
        out_fpath = join(node_path, 'index.html')
        with open(out_fpath, 'w') as fhandle:
            fhandle.write(html)
        for child in node.children:
            build_node(child, root, node_path)


    build_node(root, root, dist_dir)

    dist_assets_dir = join(dist_dir, 'assets')

    ## copy theme assets tree to dist 
    shutil.copytree(join(theme_dir, 'assets'), dist_assets_dir)

    ## copy assets tree to dist 
    shutil.copytree(join(root_dir, 'assets'), dist_assets_dir, dirs_exist_ok=True)
