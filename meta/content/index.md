+++
Description = "Simple, python-powered static site generator"
LastModifiedBranch = "site-templates"
+++

![Line drawing of a singing bird with a pan flute for vocal chords](/assets/logo_syrinx.png "Syrinx Logo")
# Syrinx

> *Spreadsheet to website*

Syrinx is a simple Python static site generator that converts markdown content into HTML websites.

* [GitHub](https://github.com/JasperVanDenBosch/syrinx)


## Quick Start

```bash
pip install syrinx
syrinx new --scaffold blog-webawesome
syrinx serve
```

Or start from scratch:

```bash
pip install syrinx
mkdir content
echo "# Hello World" > content/index.md
syrinx serve
```

Visit `http://localhost:8000` to see your site.


## How It Works

Syrinx follows a three-stage pipeline:

1. **Preprocess**: Generate markdown from TSV data files (optional)
2. **Read**: Parse the `content/` directory into a tree of nodes
3. **Build**: Render nodes to HTML using Jinja2 templates

Your project structure:

```
my-site/
├── syrinx.cfg          # Configuration (optional)
├── content/
│   └── index.md        # Your markdown content
├── data/               # TSV files for content generation (optional)
├── theme/
│   ├── templates/      # Jinja2 templates
│   └── assets/         # CSS, images, fonts
└── dist/               # Generated output
```


## Content

### Branches and Leaves

Syrinx organizes content as a tree:

- **Branch**: A directory containing `index.md` — becomes a section page
- **Leaf**: A non-index markdown file — becomes a child page (only built with `leaf_pages = true`)

If a directory has no `index.md`, it won't generate a page but its children are still processed.

### Frontmatter

Markdown files start with frontmatter in YAML (surrounded by `---`) or TOML (surrounded by `+++`):

```toml
+++
Title = "My Page"
SequenceNumber = 1
LastModified = 2025-01-15
IncludeInSitemap = true
+++

# Page content here...
```

**Frontmatter fields:**

| Field | Description |
|-------|-------------|
| `Title` | Page title (defaults to first heading) |
| `SequenceNumber` | Controls ordering in menus and lists |
| `LastModified` | Date for sitemap `<lastmod>` element |
| `LastModifiedBranch` | Git branch to track for last-modified date |
| `IncludeInSitemap` | Explicit sitemap inclusion (`true`/`false`) |
| `Archetype` | Template name for TSV data import |


## Templates

Templates use [Jinja2](https://jinja.palletsprojects.com/) and live in `theme/templates/`.

### Template Selection

Syrinx tries templates in this order:

1. `{node_name}.jinja2` — named after the content file/directory
2. `root.jinja2` — for the top-level page only
3. `leaf.jinja2` — for leaf nodes
4. `page.jinja2` — default fallback

### Available Variables

| Variable | Description |
|----------|-------------|
| `index` | The current node being rendered |
| `root` | The root node of the content tree |

### Node Properties

| Property | Description |
|----------|-------------|
| `title` | Page title |
| `content_html` | Rendered markdown content |
| `branches` | Child branch nodes |
| `leaves` | Child leaf nodes |
| `front` | Frontmatter dictionary |
| `path` | Filesystem path |
| `address` | URL path |


## Configuration

Create `syrinx.cfg` in your project root:

```ini
domain = "example.com"
sitemap = "opt-out"
urlformat = "filesystem"
leaf_pages = false
clean = true
environment = "production"
verbose = false
```

**Options:**

| Option | Values | Description |
|--------|--------|-------------|
| `domain` | string | Domain for canonical URLs and sitemap |
| `sitemap` | `opt-in`, `opt-out` | Default sitemap inclusion behavior |
| `urlformat` | `filesystem`, `mkdocs`, `clean` | URL structure style |
| `leaf_pages` | `true`, `false` | Whether to build pages for leaves |
| `clean` | `true`, `false` | Clean `dist/` before building |
| `environment` | string | Environment name (available in templates) |
| `verbose` | `true`, `false` | Enable detailed logging |

### CLI Commands

```bash
syrinx build                    # Build site to dist/
syrinx build --clean            # Clean dist/ first
syrinx build --leaf-pages       # Include leaf pages

syrinx serve                    # Dev server on port 8000
syrinx serve --port 3000        # Custom port

syrinx new --scaffold NAME      # Create new site from template
```

All config file options can be overridden via CLI flags. Run `syrinx <command> --help` for details.


## Advanced

### Generating Content from Data

Syrinx can generate markdown files from TSV spreadsheets — useful for sites with many similar pages (team members, products, blog posts, etc.).

**Setup:**

1. Create a TSV file in `data/` (e.g., `data/people.tsv`)
2. Create a matching archetype template in `archetypes/` (e.g., `archetypes/people.md`)
3. Run `syrinx build` — markdown files are generated in `content/{name}/` before the HTML build

The archetype filename must match the TSV filename (without extension). Archetypes use Jinja2 syntax for templating.

**Example TSV** (`data/people.tsv`):

```
PersonId	FullName	Role	Image
jsmith	Jane Smith	Lead	jane.jpg
bjones	Bob Jones	Developer	bob.jpg
```

**Example archetype** (`archetypes/people.md`):

```jinja
+++
Title = "{{ FullName }}"
SequenceNumber = {{ SequenceNumber }}
Image = "{{ Image }}"
+++

{{ FullName }} is a {{ Role }} on the team.
```

**Generated output** (`content/people/jsmith.md`):

```toml
+++
Title = "Jane Smith"
SequenceNumber = 0
Image = "jane.jpg"
+++

Jane Smith is a Lead on the team.
```

**How it works:**

- First column becomes the output filename (e.g., `jsmith` → `jsmith.md`)
- Column headers become Jinja2 template variables
- `SequenceNumber` is auto-generated if not in your TSV
- With `clean = true`, stale generated files are removed on each build

### Git Integration

If you set `LastModifiedBranch` in frontmatter, Syrinx will track the last commit date on that branch for the content file, automatically updating `LastModified` for your sitemap.


## Sites Built with Syrinx

- [#EEGManyLabs](https://eegmanylabs.org)
- [100 Years of EEG](https://eeg100.org)
- [Jasper's Blog](https://jaspervandenbosch.com)
- [This page](https://syrinx.site)
