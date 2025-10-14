from __future__ import annotations
from typing import TYPE_CHECKING, Callable
from os.path import isdir, join, isfile
import shutil, os, logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
from syrinx.exceptions import ThemeError
from syrinx.sitemap import collect_urls, generate_sitemap
if TYPE_CHECKING:
    from syrinx.read import ContentNode
    from syrinx.config import SyrinxConfiguration
logger = logging.getLogger(__name__)

def choose_template_file(
            node: ContentNode,
            isfile: Callable[[str], bool],
            dir: str
        ) -> str:
    name = node.name or 'root'
    template_names = (name, 'leaf', 'page') if node.isLeaf else (name, 'page')
    for tem_name in template_names:
        if isfile(join(dir, f'{tem_name}.jinja2')):
            return f'{tem_name}.jinja2'
    else:
        raise ThemeError(f'Missing template for "{node.name}"')


def dir_exists_not_empty(path: str) -> bool:
    if isdir(path):
        if len(os.listdir(path)):
            return True
    return False


def build_node(
        node: ContentNode,
        root: ContentNode,
        parent_path: str,
        template_dir: str,
        env: Environment
    ):
    """Recursive function to render page, then move on to children
    """
    node_path = join(parent_path, node.name)
    os.makedirs(node_path, exist_ok=True)
    if node.buildPage:
        fname_tem = choose_template_file(node, isfile, template_dir)
        page_template = env.get_template(fname_tem)
        html = page_template.render(index=node, root=root)
        out_fpath = join(node_path, f'{node.name}.html' if node.isLeaf else 'index.html')
        with open(out_fpath, 'w') as fhandle:
            fhandle.write(html)
        rel_path = out_fpath.replace(out_fpath.split('dist/')[0], '')
        logger.info(f'Built {rel_path}')

    for child in node.branches+node.leaves:
        build_node(child, root, node_path, template_dir, env)


def build(root: ContentNode, root_dir: str, config: SyrinxConfiguration):

    assert isdir(root_dir)
            
    theme_dir = join(root_dir, 'theme')
    template_dir = join(theme_dir, 'templates')
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape()
    )

    ## locate and clear target directory
    dist_dir = join(root_dir, 'dist')
    if isdir(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)

    build_node(root, root, dist_dir, template_dir, env)

    dist_assets_dir = join(dist_dir, 'assets')

    ## copy theme assets tree to dist 
    theme_assets_dir = join(theme_dir, 'assets')
    if dir_exists_not_empty(theme_assets_dir):
        shutil.copytree(theme_assets_dir, dist_assets_dir)

    ## copy assets tree to dist 
    content_assets_dir = join(root_dir, 'assets')
    if dir_exists_not_empty(content_assets_dir):
        shutil.copytree(content_assets_dir, dist_assets_dir, dirs_exist_ok=True)

    sitemap_fpath = join(dist_dir, 'sitemap.xml')
    urls = collect_urls(root)
    if urls:
        with open(sitemap_fpath, 'w') as fhandle:
            fhandle.write(generate_sitemap(urls))
        logger.info(f'Created sitemap.xml')
