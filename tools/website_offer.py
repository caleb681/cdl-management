"""Shared customer-facing website offer for the unpublished owner review.

Commercial source: ../../research/WEBSITE-OFFER.md. Keep pricing, summaries and
terms together so the same plan is described across the static site.
"""

MONTHLY = 500
SETUP = 1500
SETUP_INSTALLMENT = SETUP // 2
EXTRA_HOURLY = 125
CONTENT_PAGES = 8
UTILITY_PAGES = 2
EDIT_MINUTES = 45
REVISION_ROUNDS = 2
PRICE = f'${MONTHLY:,}/month + ${SETUP:,} one-time setup'
PRICE_HTML = f'${MONTHLY:,}<small> / month + ${SETUP:,} one-time setup</small>'
SUMMARY = (f'One showroom. Up to {CONTENT_PAGES} content pages, mobile design, '
           f'clear copy, search foundations, hosting and care. Includes {EDIT_MINUTES} '
           'minutes of updates each month.')
EXIT_SUMMARY = ('Month-to-month after launch. Cancel with 30 days’ notice, with a '
                'prorated final month. Your domain and accounts stay yours; a '
                'portable website handover is included after setup is paid.')
SEPARATE = ('Local SEO campaigns, ongoing AI-search work, advertising management '
            'and licensed product tools are quoted separately. Ad spend is extra. '
            'CRM integration is planned for later and is not included.')
PRICE_DESCRIPTION = (f'Recommended website plan: {PRICE}. Up to eight pages, hosting, care and '
                     '45 minutes of monthly edits. Marketing and ad spend are separate.')

PLAN_FAQ = (
    'What does the website plan include?',
    f'Our recommended standalone website plan is {PRICE}. {SUMMARY} Setup includes {REVISION_ROUNDS} consolidated revision rounds. '
    f'{EXIT_SUMMARY} {SEPARATE} <a href="/pricing/">See the full scope and terms.</a>'
)

PLAN_FAQS = [
    ('When do I pay, and when does the monthly service start?',
     f'Setup is ${SETUP_INSTALLMENT:,} to schedule and start the agreed work, then '
     f'${SETUP_INSTALLMENT:,} on accepted launch readiness, before you authorize publication. '
     'Recurring billing starts '
     'on the approved launch date, then bills monthly on that anniversary. There is '
     'no monthly website bill while we are building or waiting for your inputs. '
     f'Twelve paid months plus setup total ${SETUP + 12 * MONTHLY:,}, before applicable '
     'taxes and approved extras; that is an illustration, not a minimum commitment.'),
    ('How long does the build take?',
     'We agree your reserved start date before taking a start payment. Our target is '
     'a first full draft within ten business days of complete inputs, and launch '
     'readiness within twenty business days with prompt reviews. Please return one '
     'consolidated list of feedback within five business days per round. Access '
     'restrictions, missing inputs or delayed approval move the schedule. After '
     '30 days without required inputs, we re-plan the start date in writing. '
     'Silence is not approval, and we do not add an automatic restart fee.'),
    ('How do edits and extra work work?',
     f'Your monthly allowance is up to {EDIT_MINUTES} minutes of production and QA '
     'for supplied text, photos, hours or offers on existing pages. Send one '
     'consolidated request, with one active request at a time. Unused time does not '
     'roll over. New pages, redesigns, features and bulk imports need a separate '
     f'scope. Additional work is ${EXTRA_HOURLY}/hour or a written fixed quote, with '
     'the task and maximum charge approved before work begins. No automatic '
     'overages. Corrections to CDL-caused defects do not consume your allowance '
     'or incur an extra fee.'),
    ('Can I cancel, and will the price change?',
     'After launch, service is month-to-month with no fixed multi-month commitment '
     'and no early-termination buyout. Email caleb@cdl1.net with 30 calendar days’ '
     'notice. The notice period starts when we receive it; we confirm the end '
     'date and prorate any final partial month. Your agreed recurring rate stays '
     'the same for the first twelve continuous months. Later price changes require '
     'at least 60 days’ written notice, with the same right to cancel. Scope '
     'changes need a new written agreement.'),
    ('What do I own, and what happens if I leave?',
     'You remain the domain registrant and owner/admin of your Google, analytics, '
     'search and ad accounts. Your supplied content and assets remain yours. Once '
     'the setup milestones are paid, you own the commissioned client-specific '
     'copy and design deliverables and have a perpetual right to use and modify '
     'the delivered website. CDL retains its reusable templates, libraries and '
     'internal tools, with a perpetual license to the embedded components needed '
     'to run and modify your site. Third-party items keep their own licenses. '
     'One standard export is included without a buyout or export fee, within ten '
     'business days of a handover request after payment for the setup deliverables: '
     'public files, necessary source/build instructions, transferable media, '
     'redirect map and DNS/service inventory, plus one hour of transition help. '
     'New-host implementation, redesigns and replacement subscriptions are separate. '
     'We serve the site through the paid cancellation date and keep a recovery '
     'copy for 30 days after hosting ends. External forms and licensed tools may '
     'need replacement on another host; an export is not a one-click transfer '
     'of every provider.'),
    ('What if the project stops before launch or a payment is overdue?',
     'Before launch, we reconcile documented completed milestones, deliver paid '
     'client-specific work and refund unearned prepaid amounts. The whole deposit '
     'is not automatically earned on receipt, and extra work beyond the agreed '
     'setup ceiling needs approval. If a payment becomes overdue, we give clear '
     'notice and ten calendar days to resolve it before discretionary suspension, '
     'explain what would be affected and retain a recovery copy. Your domain and '
     'client-provided assets remain yours. Protective action for an active '
     'security incident is handled separately.'),
]


def pricing_content():
    """Return the full visible plan scope; expandable details are added by build."""
    return f'''<div class="callout"><span class="eyebrow">Recommended standalone website plan</span>
<h2>A better website for your flooring showroom.</h2>
<p class="answer"><strong>{PRICE}</strong></p><p>{SUMMARY}</p>
<p>{EXIT_SUMMARY}</p><p><a class="btn" href="/contact/">Discuss my website <span aria-hidden="true">→</span></a></p>
<p>This is the recommended website-only scope for review. Proposed switching credits need separate written approval; their setup-fee treatment is still open. <a href="/switch/">Review the two proposed transition paths.</a></p>
<p><a href="#included">See exactly what is included ↓</a></p></div>
<nav class="toc" aria-label="On this page"><b>Know the full scope</b><a href="#included">The build</a><a href="#care">Monthly care</a><a href="#separate">Separate costs</a><a href="#terms">Payments &amp; leaving</a></nav>
<section id="included"><h2>What setup includes</h2>
<ul><li><strong>One showroom, one primary domain, English content.</strong> Up to {CONTENT_PAGES} agreed content pages. For example: Home, About, Carpet, Luxury Vinyl, Hardwood, Installation, Projects and Contact. Choose the products and services in your outline before we build.</li>
<li><strong>A useful design and clear copy.</strong> One brand direction using our responsive section system, tailored colors, type and logo, one owner interview and up to 5,000 words from approved business facts. Optimize and place up to 20 supplied, permission-cleared images.</li>
<li><strong>Contact paths that get checked.</strong> One standard inquiry form with up to six agreed fields, spam protection and positive delivery acknowledgement, connected to one verified destination. The form can appear on several pages. Phone, email and map links are included.</li>
<li><strong>Sound search foundations.</strong> Titles, descriptions, headings, internal links, sitemap, canonical URLs, crawl controls and factual structured business information. Image performance, keyboard use and representative accessibility checks are part of the build. These are foundations, not ongoing SEO or accessibility certification.</li>
<li><strong>A careful changeover.</strong> Review important existing URLs and include up to 20 agreed one-to-one redirects. We assess valuable pages, co-op restrictions and migration needs before signing rather than discard useful content to fit a page limit.</li>
<li><strong>Measurement in your accounts.</strong> Connect one client-owned analytics property and one Search Console property, creating them with your authorization if needed. Verify agreed inquiry and phone-click events where consent permits. A phone click is not an answered call, and a submission is not a qualified lead or sale.</li>
<li><strong>Review before publication.</strong> {REVISION_ROUNDS} consolidated revision rounds, one on the design/content draft and one before launch. Correct CDL errors and missing agreed work without using a round. Check the exact build, mobile/desktop views, links, forms, redirects, export and rollback before your named approver accepts it and authorizes launch.</li>
<li><strong>Utility pages.</strong> Up to {UTILITY_PAGES} pages formatting your supplied privacy/legal text, plus a useful 404 page, outside the content-page allowance. Legal-policy drafting is separate.</li></ul>
<h3>What your team supplies</h3><p>Accurate showroom facts, products and offers; logo and real photography with permission to use them; brand requirements; required policy text; necessary delegated access; and one named approver. We confirm your outline, access and actual schedule before starting.</p></section>
<section id="care"><h2>What monthly care includes</h2><ul>
<li>Managed hosting and HTTPS, versioned copies of approved deployments and restoration of the delivered site.</li>
<li>Availability monitoring, monthly link/form checks and a short monthly care summary.</li>
<li>Corrections to CDL-caused defects in the delivered scope.</li>
<li>Up to <strong>{EDIT_MINUTES} minutes of changes to existing content each month</strong>, including production and QA. Supplied text, photos, hours and offers fit this allowance. Unused time does not roll over.</li>
</ul><p>Routine support hours are Monday–Friday, 9 a.m.–5 p.m. Central, excluding US federal holidays. We confirm your support contacts and coverage before launch. This is not 24/7 support or an uptime guarantee.</p></section>
<section id="separate"><h2>What is quoted separately</h2><p>{SEPARATE}</p>
<p>Also separate: manufacturer catalogs/feeds, room visualizers, sample ordering, ecommerce, payments, estimators, appointment engines, call tracking, SMS, email campaigns, customer portals, a self-service CMS, additional locations/languages, extensive content migration, photography and full redesigns.</p>
<p>You pay domain registration/renewal and business email directly. Any licensed tool is identified with its cost, owner and cancellation/export limits before you commit. No required tool is added silently after signing, and manufacturer or co-op access is not presumed transferable.</p>
<p>Additional work is <strong>${EXTRA_HOURLY}/hour or a written fixed quote</strong>. You approve the task and maximum charge before we begin. No automatic overage charges.</p></section>
<section id="terms"><h2>Payments, timing and a clean handover</h2><p>The plan below explains how setup, care and cancellation work. Your written agreement records the exact pages, client responsibilities, milestones and approved extras.</p></section>'''
