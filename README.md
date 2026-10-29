# CDL Marketing: Website

Marketing site for CDL Marketing (growth services for flooring showrooms), served at https://cdlmanagement.com/.
The homepage is a single self-contained HTML file (`index.html`). The Cloudflare Worker `cdl-management` deploys the default branch (`main`) to production.

Managed by Caleb with Claude. To update: open a pull request against main; merging deploys.

## Blog

- Index: `blog/index.html` (https://cdlmanagement.com/blog/)
- Posts live at `blog/SLUG/index.html` (https://cdlmanagement.com/blog/SLUG/).
- New posts start from `_templates/blog-post.html`. The steps are in the comment at the top of that file: fill every placeholder, remove the noindex line, add a card to the blog index and a `<url>` to `sitemap.xml`.
- `_templates/` is not published (see `.assetsignore`).
