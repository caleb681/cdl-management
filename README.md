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

Caleb requested an illustrative edit showing him standing in a flooring showroom and removal of Owner as his descriptor. The current hero uses `assets/caleb-showroom.webp` (800 × 1000, 108,820 bytes) and `assets/caleb-showroom-400.webp` (400 × 500, 32,812 bytes). Both are responsive technical encodings of the built-in image-generation edit of his supplied March portrait. The scene is illustrative, not a documentary photograph of a named store. Alt text reflects that distinction; the caption is Caleb Foglesong / CDL Marketing. The original photo and earlier derivatives are retained.

Source and prompt provenance live outside this public repository at `../research/conversion-upgrade/image-provenance.json` and `../research/conversion-upgrade/IMAGE-PROMPT.md`. No replacement job title is asserted. The Person schema and visible byline links use the same About identity.

## Commercial draft

The local site now presents the **proposed CDL Showroom Website plan for owner review**: **$500/month + $1,500 one-time setup**, one showroom/domain, up to eight content pages plus two client-supplied legal utility pages, two consolidated revision rounds and 45 minutes of monthly edits. Setup is $750 at start and $750 on accepted launch readiness; monthly billing begins at approved launch. Extra work requires approval at $125/hour or a written fixed quote. The plan is month-to-month after launch, with 30 days' notice, a prorated final month and a portable paid setup deliverable. Client domain/accounts stay client-controlled. Full scope and payment/ownership/export rules are in `/pricing/`; the source proposal is private at `../research/WEBSITE-OFFER.md`.

Commercial text is centralized in `tools/website_offer.py` and shared by the homepage, service pages, pricing, FAQs and CDL comparison cells. All monthly-price mentions include the mandatory setup fee, including page/OG/Twitter/schema descriptions. Public copy is written as the customer experience; **the proposal has not been adopted, published or activated**. Support response-time targets remain off the public pages until primary/backup staffing is confirmed. Before customer use, verify the actual monitoring, form delivery, export/restore, staffing and reviewed agreement. Local SEO campaigns, ongoing AI-search work, ad management/media and licensed product tools are separate; CRM integration remains future work.

### Proposed switching support

The lead is now **No long-term marketing contract**: month-to-month SEO and advertising with scope, fees and cancellation notice agreed in writing. This does not cancel an existing provider agreement or mean that no written agreement is needed. The $500/month + $1,500 setup website-only plan remains a recommendation; it is not silently made free by the transition proposals.

`tools/transition_offer.py` centralizes the visible **proposed** switching cards, review steps, notices and unresolved terms. `/switch/` is a normal crawlable page linked from the shared navigation, homepage, pricing, websites and comparison. Proposed path one is monthly website-service credits through the reviewed existing website contract end when purchasing both paid CDL SEO and advertising management; its maximum period and credit cap remain open. Path two is up to three months of monthly website-service credits for website-only transitions, subject to eligibility and written approval. These are not cash buyouts, reimbursements or payment of another provider's fees. Setup treatment is open for both paths; SEO/ad-management fees and platform media are separate. No automatic credit, universal competitor term, minimum transition purchase or final cap is invented.

The switching page explicitly leaves eligibility/evidence, paid marketing fees versus media, maximum combined-service credit period, start date, setup fee, total credit cap, cancellation effects and combining offers for review. It preserves URLs/domains and inquiry destinations through an agreement review, written scope/credit approval, build verification and controlled cutover. It creates no upload, checkout, credit activation or provider integration. Contact links point to `/contact/#switching`; the existing optional `goal` select adds two switching choices, with field names, payload handling and destinations retained. Form acceptance acknowledges the inquiry, not approval of a transition credit.

The shared social image is `/assets/og-marketing-20261105.jpg` (1200 × 630), replacing the older CRM-advertising card in generated OG/Twitter metadata. The older asset remains preserved.

The previous bundled fee table and 15-lead guarantee are removed from generated public copy, while untouched historical snapshots remain in `source/legacy/`. Existing `#pricing` and `#guarantee` anchors are retained with the current scope explanation. CRM is not a current product: `/services/flooring-crm/` explains later integration assessment and carries no Service schema or primary-service navigation. No rankings, AI mentions or lead count are promised.

Current public services: websites, local SEO, paid advertising and AI search visibility. Buyer pages are composed from the separate `tools/buyer_content.py` module at `/compare/broadlume/` and `/guides/choosing-a-flooring-marketing-agency/`.

## Retailer education

`tools/retailer_resources.py` builds `/guides/flooring-marketing-checklist/` and `/guides/your-first-marketing-review/`. Contact's after-call section, the agency buyer guide and shared footer link to them. The checklist is an educational self-review, not a crawl, performance score or quote. Its six native selections work as reading prompts without JavaScript.

Only the checklist loads `assets/diagnostic.js`. It uses fixed options to create a local discussion list, lists unknowns, hides stale results after edits and supports reset/browser print. It makes no network, storage or analytics calls and does not attach answers to inquiry forms or links. Shared optional advertising choices remain governed by the existing privacy controls. No new account access, automated report, service commitment or pricing is implied. The companion guide explains the first assessment, service fit and conditional transition steps with official-source links.

### Existing-provider readiness

`tools/switch_readiness.py` builds `/guides/switching-flooring-website-providers/`, linked from the switching page, Contact's switching section and the first-review guide. This static educational checklist separates verified records, reported details, unknowns and conflicting evidence. It covers actual renewal/notice, distinct domain/DNS/email control, account access, content/catalog rights, measurement, inquiry routing and staged cutover/recovery. No file upload, score, date calculator, new script or service activation is added. The detailed caller worksheet/workflow stays in private review material outside this public repository.

## Forms and tracking

Both inquiry forms use the same protected, same-origin intake system. Growth audit requests POST to `/api/intake/audit`; free-design requests POST to `/api/intake`. There is no FormSubmit fallback or dual delivery. Audit name, showroom, city/state and email remain required; phone, website, revenue and goal remain optional. Public payloads cannot change trusted leads or approve an offer. The actual backend remains in the private `cdl-management/api-worker` source; `functions/api/[[path]].js` is an excluded historical stub.

Success requires a durable receipt with `ok: true`, `status: received_unverified`, the matching route-derived `request_kind`, a UUID receipt ID and a boolean duplicate indicator. A legacy/generic acknowledgement or wrong-kind response stays uncertain, preserving entered details and preventing automatic resends. A duplicate shows that the request was already received and never counts as another conversion. Explicit validation/body/time/rate rejection permits a deliberate corrected retry; network/server/ambiguous outcomes direct the visitor to contact the team. The form code does not retry automatically or use an alternative processor. Browsers may replay a transport request: Chromium did so after a synthetic HTTP 408 timeout. Server-side no-write rejection and shared duplicate controls kept that replay to one saved inquiry.

Both request types share server validation, byte/time limits, durable duplicate and rate controls, an unverified owner review queue and one internal notification attempt. Migration and backend deployment must precede this frontend; strict receipt checks intentionally reject older backend responses. Audit fields and type require a separate additive expansion migration, preserving all existing receipts and the original mockup duplicate fingerprint. Review the private runbook and rollback plan before any authorized release. This static build neither applies migrations nor deploys the backend.

`assets/track.js` defaults advertising measurement off. Equal allow/decline controls are available in the footer. An explicit browser choice permits the existing Meta Pixel and PageView / Lead event names; GPC or DNT overrides allowance. A Lead event identifies the form type only, after a new valid receipt while tracking is allowed and loaded. No contact-field values or earlier requests are added/backfilled. Storage failures fail closed on the current page. Withdrawal stops this site's event requests; an explicit reload applies the off choice fully without automatically discarding form text. Provider-side behavior remains unverified. GA4 remains unconfigured.

`tools/privacy_policy.py` describes the local candidate: both forms use the site's intake service. Historical policy and FormSubmit source snapshots remain archived and excluded from publication. Synthetic tests intercept all submissions and SDK requests. Actual owner access, edge protections, internal alert delivery, provider configuration and production persistence still need separately authorized acceptance. Current local checks do not prove live receipts or approved commercial terms.

## Verification

`npm run build` checks all generated public routes and local references, unique canonical URLs, sitemap, page headings, JSON-LD, image dimensions/alt text and asset exclusions. To install the optional test tools, use `npm install` and `npx playwright install chromium`, then run `npm test` while the preview server is running. Existing installations can be passed with `PLAYWRIGHT_MODULE` and `AXE_MODULE`; `EVIDENCE_DIR` controls where results/screenshots are saved. No real submissions are sent.

Preserve existing `/command/` and production route overlays such as `/api/*`, `/GoodNotes*` and `/seo*`. The rebuild does not alter or verify those separate Workers.

## Blog

- Index: `blog/index.html` (https://cdlmanagement.com/blog/)
- Posts live at `blog/SLUG/index.html` (https://cdlmanagement.com/blog/SLUG/).
- Existing article bodies come from `source/articles/SLUG/index.html` when present, otherwise `source/legacy/blog/SLUG/index.html`. To add a new article, extend the generator and `ARTICLE_INFO` list. Preserve meaningful original URLs and dates. The old `_templates/blog-post.html` remains as a reference, not a live build input.
- `_templates/` is not published (see `.assetsignore`).

## Buying clarity and sample work

`tools/proof_content.py` generates `/work-samples/`: an illustrative three-priority audit, flooring page concept and monthly report format. These examples demonstrate the approach, not actual client results. `tools/service_examples.py` adds concrete flooring scenarios to each service page. The homepage presents website, local SEO and advertising choices before switching incentives, and links to AI search as related separately scoped work. The existing proposed prices, fees and terms remain proposed. No result history or ranking guarantee was added.
