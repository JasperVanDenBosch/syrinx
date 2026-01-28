"""
    The user calls `syrinx new` to generate a starting workspace for their static site.

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
import os
import json
from pathlib import Path
from os.path import abspath, join, dirname
from importlib.metadata import version
from jinja2 import Environment, Template
from rich.console import Console
from rich.prompt import Prompt
from rich.tree import Tree
if TYPE_CHECKING:
    from argparse import Namespace


## Common variables needed for all scaffolds
COMMON_VARIABLES = [
    {
        "name": "title",
        "prompt": "Site title",
        "default": "My Site"
    },
    {
        "name": "description",
        "prompt": "Site description",
        "default": "A site built with Syrinx"
    },
    {
        "name": "domain",
        "prompt": "Domain name",
        "default": "example.com"
    },
    {
        "name": "syrinx_version",
        "prompt": "Syrinx version",
        "default": version('syrinx')
    }
]


def generate_scaffold(args: Namespace):
    """Generate a new site from a scaffold template."""
    
    console = Console()
    
    ## Target directory (where to output files)
    target_dir = abspath(args.dir)
    
    ## Scaffold choice
    scaffold_name = args.scaffold
    
    ## Get path to scaffolds directory
    syrinx_root = dirname(dirname(abspath(__file__)))
    scaffolds_dir = join(syrinx_root, 'scaffolds')
    scaffold_dir = join(scaffolds_dir, scaffold_name)
    
    ## Check if scaffold exists
    if not os.path.exists(scaffold_dir):
        console.print(f"[red]Error: Scaffold '{scaffold_name}' not found at {scaffold_dir}[/red]")
        return
    
    ## Load scaffold metadata
    scaffold_json_path = join(scaffold_dir, 'scaffold.json')
    if not os.path.exists(scaffold_json_path):
        console.print(f"[red]Error: scaffold.json not found in {scaffold_dir}[/red]")
        return
    
    with open(scaffold_json_path, 'r') as f:
        scaffold_meta = json.load(f)
    
    ## Display scaffold info
    console.print(f"\n[bold cyan]Creating new site: {scaffold_meta['name']}[/bold cyan]")
    console.print(f"[dim]{scaffold_meta['description']}[/dim]\n")
    
    ## Merge common variables with scaffold-specific variables
    all_variables = COMMON_VARIABLES + scaffold_meta.get('variables', [])
    
    ## Collect variable values from user
    scaffold_vars = {}
    
    if args.yes:
        ## Use defaults without prompting
        console.print("[yellow]Using default values (--yes flag)[/yellow]\n")
        for var in all_variables:
            scaffold_vars[var['name']] = var['default']
            console.print(f"  {var['prompt']}: [cyan]{var['default']}[/cyan]")
    else:
        ## Prompt user for each variable
        console.print("[bold]Please provide the following information:[/bold]\n")
        for var in all_variables:
            value = Prompt.ask(
                f"  {var['prompt']}", 
                default=var['default']
            )
            scaffold_vars[var['name']] = value
    
    console.print()
    
    ## Check if target directory exists
    if os.path.exists(target_dir) and os.listdir(target_dir):
        console.print(f"[yellow]Warning: Directory {target_dir} already exists and is not empty[/yellow]")
        if not args.yes:
            proceed = Prompt.ask("  Continue anyway?", choices=["y", "n"], default="n")
            if proceed.lower() != 'y':
                console.print("[red]Cancelled[/red]")
                return
    
    ## Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    ## Use alternative syntax with brackets for scaffolding phase
    env = Environment(
        block_start_string='[%',
        block_end_string='%]',
        variable_start_string='[[',
        variable_end_string=']]',
        comment_start_string='[#',
        comment_end_string='#]'
    )
    
    ## Process all files from scaffold
    console.print("[bold green]Generating files...[/bold green]\n")
    generated_files = []
    
    for root, dirs, files in os.walk(scaffold_dir):
        ## Skip scaffold.json
        if 'scaffold.json' in files:
            files.remove('scaffold.json')
        
        ## Calculate relative path from scaffold_dir
        rel_dir = os.path.relpath(root, scaffold_dir)
        if rel_dir == '.':
            target_subdir = target_dir
        else:
            target_subdir = join(target_dir, rel_dir)
        
        ## Create target subdirectory
        os.makedirs(target_subdir, exist_ok=True)
        
        ## Process each file
        for filename in files:
            source_file = join(root, filename)
            target_file = join(target_subdir, filename)
            
            ## Read source file content
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                ## Process with jinja2
                template = env.from_string(content)
                processed_content = template.render(scaffold=scaffold_vars)
                
                ## Write to target file
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(processed_content)
                
                ## Track generated file
                rel_path = os.path.relpath(target_file, target_dir)
                generated_files.append(rel_path)
                
            except UnicodeDecodeError:
                ## Binary file - just copy it
                import shutil
                shutil.copy2(source_file, target_file)
                rel_path = os.path.relpath(target_file, target_dir)
                generated_files.append(rel_path)
            except Exception as e:
                console.print(f"[red]Error processing {filename}: {e}[/red]")
    
    ## Display generated files as tree
    console.print("[bold green]✓ Site generated successfully![/bold green]\n")
    console.print("[bold]Generated files:[/bold]\n")
    
    tree = Tree(f"[bold blue]{os.path.basename(target_dir)}[/bold blue]")
    
    ## Build tree structure
    tree_nodes = {'.': tree}
    for file_path in sorted(generated_files):
        parts = Path(file_path).parts
        
        if not parts:
            continue
            
        current_path = '.'
        
        ## Create intermediate directory nodes
        for i, part in enumerate(parts[:-1]):
            parent_path = current_path
            current_path = str(Path(current_path) / part)
            
            if current_path not in tree_nodes:
                tree_nodes[current_path] = tree_nodes[parent_path].add(f"[blue]{part}/[/blue]")
        
        ## Add file node
        if len(parts) > 0:
            parent_path = str(Path(*parts[:-1])) if len(parts) > 1 else '.'
            tree_nodes[parent_path].add(f"[green]{parts[-1]}[/green]")
    
    console.print(tree)
    console.print()
    
    ## Display next steps
    console.print("[bold cyan]Next steps:[/bold cyan]")
    console.print(f"  1. cd {target_dir}")
    console.print(f"  2. syrinx serve")
    console.print()
