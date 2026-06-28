# NaamaInnovation Website

Static portfolio website for Naama Lavee, prepared for GitHub Pages at `https://naamainnovation.github.io`.

## Pages

- `/` - landing page
- `/about/` - about page
- `/works/` - projects page
- `/events/` - future events page
- `/contact/` - contact page
- `/gallery/` - gallery page
- `/admin/` - Decap CMS admin interface

## Editing Content

Update source files are stored in:

- `UPDATE/Projects.xlsx`
- `UPDATE/Event list.xlsx`
- `photos/Gallery/`

After editing the Excel files or adding gallery images, run:

- `UPDATE/update_site.bat`

This regenerates:

- `content/works.json`
- `content/events.json`
- the image list in `gallery/index.html`

To preview locally, run:

- `UPDATE/preview_site.bat`

After the repository is published and GitHub authentication is configured, the same content can be edited from `/admin/` without editing code.

## Publishing

Use this repository name on GitHub for the clean public address:

`NaamaInnovation.github.io`
