# NovaSteel Website

This folder contains the source of the **NovaSteel** institutional website,
built with [MkDocs](https://www.mkdocs.org/) and the
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.

## Structure

```
website/
├── mkdocs.yml          # MkDocs configuration and navigation
├── requirements.txt    # Python dependencies
└── docs/               # Markdown content
    ├── index.md        # Home page
    ├── company/        # About, activities, sustainability
    ├── products/       # Products and markets
    ├── steel/          # How steel and other metals are made
    └── contact.md      # Contact information
```

## Local development

```bash
cd website
pip install -r requirements.txt
mkdocs serve
```

Then open <http://127.0.0.1:8000/> in your browser.

## Build

```bash
cd website
mkdocs build
```

The static site is generated in `website/site/` (ignored by Git).

## Deployment

The site is built and published automatically to GitHub Pages by the
[`deploy-website.yml`](../.github/workflows/deploy-website.yml) workflow
whenever files in the `website/` folder change on the default branch, or when
the workflow is triggered manually from the **Actions** tab.
