+++
+++

# Syrinx

Syrinx is a super simple python package for generating a static website

* [github](https://github.com/JasperVanDenBosch/syrinx)

## Example

```
pip install syrinx
touch content/index.md
syrinx .
python -m http.server -d dist
```

## Conventions

Organize your content with some standard structure and syrinx will interpret it.


### Content

1. a `content/` directory with markdown file `index.md`
2. *Toml* style frontmatter: Markdown files start with a standard header or *"frontmatter"* that is surrounded by triple pluses `+++`. 


### Templating and style

1. Templates are written in *jinja2* and go into the `theme/defaults/` directory.
2. CSS, images and other assets go into `theme/assets/`.


### Table Data

Syrinx can generate content (markdown) files from CSV tables in the `data/` directory.

1. The archetype file used will be based on the filename of the data file.
2. Each row is considered one record.
3. The header (1st) row will be used as keys.
4. The first column is used as name for the content item.
5. Each column will be converted to a variable in the front matter 