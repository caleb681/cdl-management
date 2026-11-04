# CDL Marketing: Website

Marketing site for CDL Marketing (growth services for flooring showrooms), served at https://cdlmanagement.com/.
This is a complete static site with a small Python generator and shared CSS/JavaScript. The Cloudflare Worker `cdl-management` deploys the default branch (`main`) to production.

Current rebuild: `codex/marketing-rebuild-20261104`, local review only. Do not merge or push main as a substitute for a reviewed release.

## Build and preview

Requires Python 3.9+ and Node 20.11+; the site build has no package dependencies.

```sh
npm run build
npm run preview
```

Preview: http://127.0.0.1:8796. It sends `X-Robots-Tag: noindex, nofollow`, never proxies the production API, and uses a local-only security policy to block external lead requests and advertising scripts. Public output itself is indexable. A separate loopback audit can use `PORT=8797 LOCAL_INDEXABILITY_AUDIT=1 npm run preview` to check production indexability; this does not publish anything. Browser tests bypass that local policy while intercepting every form and blocking every other external request.

Edit `tools/build.py` for pages, `assets/site.css` for layout, and `assets/site.js` for navigation/form behavior. Build rewrites the HTML and sitemap. `source/legacy/` contains the public pre-rebuild homepage, privacy page and articles; article prose and original publication dates are preserved by the generator. Tooling, tests and sources are excluded from the Worker upload by `.assetsignore`.

## Photo

The marked homepage portrait placeholder is intentional. No fictional person or generated composite is represented as real photography. After the owner approves the actual photo, place an optimized portrait at `assets/caleb-portrait.webp`, 700 × 850 pixels, and rebuild. Its dimensions, eager loading and high fetch priority are already in the template. Verify its focal point and rerun speed tests after replacement. The current placeholder build is not release-ready photography.

## Forms and tracking

The growth-audit form preserves its existing FormSubmit recipient and field names. The free-design form preserves `/api/intake`, adds the API's expected `name` field while retaining `contact_name`, and requires `{ok:true}` before success. The API is the separate existing `cdl-api` Worker; `functions/api/[[path]].js` is a historical stub, not the backend. No endpoint or CRM data is created by this build.

Forms require a positive acknowledgement. A rejected validation request preserves fields and permits correction; an uncertain delivery preserves fields and asks the visitor to contact the team before resending. No automatic retry. Existing `assets/track.js` is preserved byte-for-byte. Lead events fire only after acknowledgement. GA4 is still unconfigured in that original script; no ID is invented. The test suite intercepts all submissions and blocks external requests. Live recipient activation, inbox delivery and production API persistence need a separately authorized acceptance check.

## Verification

`npm run build` checks all 16 public routes, 640 local references, unique canonical URLs, sitemap, page headings, JSON-LD, image dimensions/alt text and asset exclusions. To install the optional test tools, use `npm install` and `npx playwright install chromium`, then run `npm test` while the preview server is running. Existing installations can be passed with `PLAYWRIGHT_MODULE` and `AXE_MODULE`; `EVIDENCE_DIR` controls where results/screenshots are saved. No real submissions are sent.

Preserve existing `/command/` and production route overlays such as `/api/*`, `/GoodNotes*` and `/seo*`. The rebuild does not alter or verify those separate Workers.

## Blog

- Index: `blog/index.html` (https://cdlmanagement.com/blog/)
- Posts live at `blog/SLUG/index.html` (https://cdlmanagement.com/blog/SLUG/).
- Existing article bodies come from `source/legacy/blog/`. To add a new article, extend the generator and `ARTICLE_INFO` list. Preserve meaningful original URLs and dates. The old `_templates/blog-post.html` remains as a reference, not a live build input.
- `_templates/` is not published (see `.assetsignore`).
