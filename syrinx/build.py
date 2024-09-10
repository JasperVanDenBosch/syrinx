from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import isdir, join
import shutil, os
from jinja2 import Environment, FileSystemLoader, select_autoescape
if TYPE_CHECKING:
    from syrinx.read import ContentNode


def dir_exists_not_empty(path: str) -> bool:
    if isdir(path):
        if len(os.listdir(path)):
            return True
    return False

def build(root: ContentNode, root_dir: str):

    assert isdir(root_dir)
            
    ## ready templated
    theme_dir = join(root_dir, 'theme')
    env = Environment(
        loader=FileSystemLoader(theme_dir),
        autoescape=select_autoescape()
    )
    page_template = env.get_template('defaults/index.jinja2')

    ## locate and clear target directory
    dist_dir = join(root_dir, 'dist')
    if isdir(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)

    def build_node(node: ContentNode, root: ContentNode, parent_path: str):
        html = page_template.render(index=node, root=root)
        node_path = join(parent_path, node.name)
        os.makedirs(node_path, exist_ok=True)
        out_fpath = join(node_path, 'index.html')
        with open(out_fpath, 'w') as fhandle:
            fhandle.write(html)
        for child in node.branches:
            build_node(child, root, node_path)


    build_node(root, root, dist_dir)

    dist_assets_dir = join(dist_dir, 'assets')

    ## copy theme assets tree to dist 
    theme_assets_dir = join(theme_dir, 'assets')
    if dir_exists_not_empty(theme_assets_dir):
        shutil.copytree(theme_assets_dir, dist_assets_dir)

    ## copy assets tree to dist 
    content_assets_dir = join(root_dir, 'assets')
    if dir_exists_not_empty(content_assets_dir):
        shutil.copytree(content_assets_dir, dist_assets_dir, dirs_exist_ok=True)
