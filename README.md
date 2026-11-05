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

Edit `tools/build.py` for pages, `assets/site.css` for layout, and `assets/site.js` for navigation/form behavior. Build rewrites the HTML and sitemap. `source/legacy/` contains the public pre-rebuild homepage, privacy page and articles; original snapshots remain unchanged. Corrected articles in `source/articles/SLUG/index.html` take precedence over the matching legacy snapshot. Article JSON-LD supplies the visible publication/update dates and Open Graph article dates. Tooling, tests and sources are excluded from the Worker upload by `.assetsignore`.

## Photo

The homepage uses Caleb's supplied real March portrait. The original remains unchanged at `../photo-review/isolated/CDL-Marketing/site/assets/caleb-portrait.jpg` (1574 × 2702, 934,083 bytes; SHA-256 `47fcf0d951289ebf4c787fa51722cc7bdba69c1fd746396dc893a8419b668af3`). `assets/caleb-portrait.webp` is a technical resize/encoding only: 700 × 1202, WebP quality 82, 110,534 bytes; SHA-256 `1e8cbc30e2e7e9138d8e6e3a8553b3dca511465971b8e1498adadaad36fe0c13`. `assets/caleb-portrait-400.webp` is a second technical resize/encoding from that same original: 400 × 687, WebP quality 80, 46,332 bytes; SHA-256 `c0f7a1f381b3ad2d60b16746a7e5e5db0f4de6b8a3086bf96efdea7478abf6a0`. The portrait uses 400w/700w `srcset` with viewport-aware `sizes`, retaining 700 × 1202 intrinsic dimensions and high fetch priority. No identity change, generative editing or face retouching. Explicit dimensions and high fetch priority are in the template. The derivative was visually inspected; inspect rendered focal point/caption and verify performance before release.

## Commercial draft

The $500/month amount is a **draft website-only price for owner review**, not final scope or terms. The final proposal must define setup and any setup fee, pages/content, ongoing care, optional tools, contract terms and acceptance before commitment. Local SEO, AI search work and ad management are separately quoted; media is always separate. No promise of unlimited pages, free setup, cancellation terms or domain rights is inferred.

The previous bundled fee table and 15-lead guarantee are removed from generated public copy, while untouched historical snapshots remain in `source/legacy/`. Existing `#pricing` and `#guarantee` anchors are retained with the current scope explanation. CRM is not a current product: `/services/flooring-crm/` explains later integration assessment and carries no Service schema or primary-service navigation. No rankings, AI mentions or lead count are promised.

Current public services: websites, local SEO, paid advertising and AI search visibility. Buyer pages are composed from the separate `tools/buyer_content.py` module at `/compare/broadlume/` and `/guides/choosing-a-flooring-marketing-agency/`.

## Forms and tracking

The growth-audit form preserves its existing FormSubmit recipient and field names. Name, showroom, city/state and email remain required; phone, revenue and goal are optional. The free-design form preserves `/api/intake`, adds the API's expected `name` field while retaining `contact_name`, and requires `{ok:true}` before success. The API is the separate existing `cdl-api` Worker; `functions/api/[[path]].js` is a historical stub, not the backend. No endpoint or CRM data is created by this build.

Forms require a positive acknowledgement. A rejected validation request preserves fields and permits correction; an uncertain delivery preserves fields and asks the visitor to contact the team before resending. No automatic retry. Existing `assets/track.js` is preserved byte-for-byte. Lead events fire only after acknowledgement. GA4 is still unconfigured in that original script; no ID is invented. The test suite intercepts all submissions and blocks external requests. Live recipient activation, inbox delivery and production API persistence need a separately authorized acceptance check.

## Verification

`npm run build` checks all generated public routes and local references, unique canonical URLs, sitemap, page headings, JSON-LD, image dimensions/alt text and asset exclusions. To install the optional test tools, use `npm install` and `npx playwright install chromium`, then run `npm test` while the preview server is running. Existing installations can be passed with `PLAYWRIGHT_MODULE` and `AXE_MODULE`; `EVIDENCE_DIR` controls where results/screenshots are saved. No real submissions are sent.

Preserve existing `/command/` and production route overlays such as `/api/*`, `/GoodNotes*` and `/seo*`. The rebuild does not alter or verify those separate Workers.

## Blog

- Index: `blog/index.html` (https://cdlmanagement.com/blog/)
- Posts live at `blog/SLUG/index.html` (https://cdlmanagement.com/blog/SLUG/).
- Existing article bodies come from `source/articles/SLUG/index.html` when present, otherwise `source/legacy/blog/SLUG/index.html`. To add a new article, extend the generator and `ARTICLE_INFO` list. Preserve meaningful original URLs and dates. The old `_templates/blog-post.html` remains as a reference, not a live build input.
- `_templates/` is not published (see `.assetsignore`).
