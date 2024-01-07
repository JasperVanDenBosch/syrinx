"""Convert data files to content

The archetype used will be based on the filename of the data file.
Each row is considered one record.
The header (1st) row will be used as keys.
The first column is used as name for the content item.
Each column will be converted to a variable in the front matter 
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict
from os.path import join, isdir, abspath, basename
from os import makedirs
from glob import glob
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pandas import read_csv
if TYPE_CHECKING:
    from jinja2 import Template

root_dir = abspath(sys.argv[1])
assert isdir(root_dir)

archetype_files = glob(join(root_dir, 'archetypes', '*.md'))
archetypes: Dict[str, Template] = dict()
env = Environment(
    loader=FileSystemLoader(join(root_dir, 'archetypes')),
    autoescape=select_autoescape()
)

for fpath in archetype_files:
    fname = basename(fpath)
    archetype_name = fname.split('.')[0]
    archetypes[archetype_name] = env.get_template(fname)

data_files = glob(join(root_dir, 'data', '*.tsv'))

for fpath in data_files:
    archetype_name = basename(fpath).split('.')[0]
    if archetype_name not in archetypes:
        raise ValueError(f'No archetype for {archetype_name}')
    archetype = archetypes[archetype_name]

    collection_dir = join(root_dir, 'content', archetype_name)
    makedirs(collection_dir, exist_ok=True)

    df = read_csv(fpath, sep='\t', index_col=0)
    for label, row in df.iterrows():
        output = archetype.render(dict(row))
        with open(join(collection_dir, f'{label}.md'), 'w') as fhandle:
            fhandle.write(output)
