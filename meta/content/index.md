+++
Description = "Simple, python-powered static site generator"
LastModifiedBranch = "sitemap-inclusion-options"
+++

# Syrinx 

> *Spreadsheet to website*

Syrinx is a super simple python package for generating a static website

* [github](https://github.com/JasperVanDenBosch/syrinx)

## Example

```bash
pip install syrinx
touch content/index.md
syrinx serve
```

## Conventions

Organize your content with some standard structure and syrinx will interpret it.


### Content

1. a `content/` directory with markdown file `index.md`
2. Frontmatter: Markdown files start with a standard header or *"frontmatter"* that is surrounded by either dashes `---` for YAML or pluses `+++` for TOML. 
3. in content directories other than root, `index.md` is optional. Leaving it out signifies that you do not want a separate page build for this branch.
4. Special frontmatter entries:
    - `SequenceNumber`: Used by templates to order child items in menu's and lists.
    - `Archetype`: The name of the template used to import these table data
    - `LastModified`: Date and time when the content was last changed. If listed, this will be used in the sitemap as `<lastmod>` element.


### Templating and style

1. Templates are written in *jinja2* and go into the `theme/templates/` directory.
2. The default template used is `page.jinja2`. If a template is found matching the name of the node (e.g. `foo.jinja2`), or `root.jinja2` for the top-most page, this takes precedence.
3. CSS, images and other assets go into `theme/assets/`.


### Table Data

Syrinx can generate content (markdown) files from CSV tables in the `data/` directory.

1. The archetype file used will be based on the filename of the data file.
2. Each row is considered one record.
3. The header (1st) row will be used as keys.
4. The first column is used as name for the content item.
5. Each column will be converted to a variable in the front matter 

### Configuration

You can configure syrinx behavior with a `syrinx.cfg` file in the project root directory, 
or use commandline arguments (which will override any settings in the configuration file).
For options, run `syrinx -h`.