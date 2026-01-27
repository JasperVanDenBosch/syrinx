# Project Web Awesome Scaffold

A professional project/organization website scaffold using Web Awesome Pro components with a teal/navy color scheme inspired by Yorkshire MedTech's design.

## Features

- **Web Awesome Pro Components**: Uses `wa-page`, `wa-card`, `wa-button`, and other Web Awesome Pro components
- **Modern Color Scheme**: Teal primary (#00B5A5) with dark navy (#0A1628) accents
- **Responsive Layout**: Mobile-first design with adaptive navigation
- **Card-Based Content**: Uses syrinx "leaves" pattern for easy content management
- **Professional Typography**: Light headings with clean, readable body text

## Pages Included

| Page | Description |
|------|-------------|
| **Homepage** | Hero section, feature cards, CTA, and navigation to other sections |
| **About** | Organization information with value proposition cards |
| **Services** | Service offerings displayed as cards |
| **Contact** | Contact information and form placeholder |

## Content Structure

```
content/
├── index.md              # Homepage
├── feature-1.md          # Feature card (leaf)
├── feature-2.md          # Feature card (leaf)
├── feature-3.md          # Feature card (leaf)
├── about/
│   ├── index.md          # About page
│   ├── value-1.md        # Value card (leaf)
│   └── value-2.md        # Value card (leaf)
├── services/
│   ├── index.md          # Services page
│   ├── service-1.md      # Service card (leaf)
│   └── service-2.md      # Service card (leaf)
└── contact/
    └── index.md          # Contact page
```

## Scaffold Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `organization_name` | Organization or company name | Acme Corp |
| `project_name` | Project or initiative name | Innovation Hub |
| `tagline` | Mission statement or tagline | Driving innovation forward |
| `contact_email` | Contact email address | hello@example.com |
| `fa_kit_code` | Web Awesome Pro kit code | 0d7d37c081 |

## Usage

Create a new site using this scaffold:

```bash
syrinx new my-project --scaffold project-webawesome
```

## Theme Customization

The theme uses CSS custom properties for easy customization. Key variables in `theme/assets/css/index.css`:

```css
:root {
    --color-primary-teal: #00B5A5;
    --color-dark-navy: #0A1628;
    --section-padding-y: clamp(3rem, 8vw, 6rem);
    --content-max-width: 1200px;
}
```

## Web Awesome Configuration

This scaffold uses:
- Theme: `wa-theme-premium`
- Palette: `wa-palette-vogue`
- Brand: `wa-brand-cyan`

## Adding Content

### Adding Feature Cards (Homepage)

Create a new markdown file in `content/`:

```markdown
+++
Title = "New Feature"
Description = "Brief description"
SequenceNumber = 4
Icon = "icon-name"
+++
Feature content here...
```

### Adding Service Cards

Create a new markdown file in `content/services/`:

```markdown
+++
Title = "New Service"
Description = "Service description"
SequenceNumber = 3
Icon = "icon-name"
+++
Service details here...
```

## License

MIT
