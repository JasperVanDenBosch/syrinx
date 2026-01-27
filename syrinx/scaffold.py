"""
    Collect values for variables from the user with the "rich" library.
    Each should have a default.

    Available scaffolds are in the scaffolds directory. Currently there is just one 
    but I will add more later.

    Files with placeholders ( marked with double brackets ) should be processed with jinja2
    by passing in a "scaffold" variable with the template variables as properties.

    Files without placeholders could simply be copied,
    but for simplicity it may make sense to just process them all with jinja2.

    a) which scaffold (or pass in as arg..)
    c) site title
    d) site description
    e) config options for syrinx.cfg
    f) template specific vars (to be defined in a json file in the scaffold directory):
        1) web awesome pro kit code "fa-kit-code"

    display generated files with as tree 
    give suggestion for next cli command: syrinx serve <dir>
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import abspath
from jinja2 import FileSystemLoader, Environment
if TYPE_CHECKING:
    from argparse import Namespace


def generate_scaffold(args: Namespace):

    ## True if user declined to have prompts, just apply defaults
    args.yes

    ## default target directory (where to output files)
    default_dir = abspath(args.dir)

    ## default choice of template site
    default_scaffold = args.scaffold

    ## Use alternative syntax with brackets for scaffolding phase
    env = Environment(
        loader=FileSystemLoader(), ## look in scaffolds/<scaffold>/*
        block_start_string='[%',
        block_end_string='%]',
        variable_start_string='[[',
        variable_end_string=']]',
        comment_start_string='[#',
        comment_end_string='#]'
    )
