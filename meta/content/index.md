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

1. a `content/` directory with markdown file `index.md`
2. *Toml* style frontmatter: Markdown files start with a standard header or *"frontmatter"* that is surrounded by triple pluses `+++`. 
3. Templates are written in *jinja2* and go into the `theme/defaults/` directory.
4. CSS, images and other assets go into `theme/assets/`.
5. Syrinx can generate content (markdown) files from CSV tables in the `data/` directory, based on matching templates in the `archetypes/` directory. Columns become *frontmatter* attributes.