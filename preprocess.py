"""Convert data files to content


The archetype used will be based on the filename of the data file.
Each row is considered one record.
The header (1st) row will be used as keys.
Each column will be converted to a variable in the front matter 

"""
from os.path import join, isdir, abspath, basename
from glob import glob
import sys
from pandas import read_csv

root_dir = abspath(sys.argv[1])
assert isdir(root_dir)

archetype_files = glob(join(root_dir, 'archetypes', '*.md'))
archetypes = dict()
env = Environment(
    loader=FileSystemLoader('templates'),
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
    df = read_csv(fpath, sep='\t')
    for label, row in df.iterrows():
        archetype.render()
