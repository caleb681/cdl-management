# -*- coding: utf-8 -*-
"""Restoration section of the CDL Marketing site: /restoration/ and everything under it.

Called from build.py as build_restoration(build_module). Copy rules: never name any business we
own, no invented numbers, no prices, no lead guarantee. Every figure about "our own restoration
company" comes from that company's real ad accounts (Aug 2026), and every search figure from the
Google Ads volume data read on 2026-11-18.
"""

R = '/restoration/'
PUBLISHED = '2026-11-18'
DATA_NOTE = 'Google Ads keyword data for the United States, read November 18, 2026. Google rounds these figures.'

SERVICES = [
 ('seo', 'SEO for restoration companies', 'Be the company they find.', 'Your Google listing, service pages and town pages, built around what people type when the floor is wet.'),
 ('water-damage-leads', 'Water damage leads', 'Calls from your own ads.', 'Google Ads and Local Services Ads in your own accounts, so every call is yours alone.'),
 ('websites', 'Restoration websites', 'A page that gets the call.', 'Fast pages with the phone number first, built for someone standing in water with a phone.'),
 ('ai-search', 'AI search', 'Be the name AI gives.', 'Clear company facts and plain answers that ChatGPT and Google AI answers can read and repeat.'),
]
ARTICLES = [
 ('restoration-company-marketing', 'Guide', 'Restoration company marketing: a plain guide', 'What to fix first, where the calls come from, and what we learned running our own restoration company.'),
 ('how-to-get-water-damage-leads', 'Leads', 'How to get water damage leads without buying shared ones', 'Six sources of water damage jobs, what each one costs you, and the questions to ask a lead seller.'),
 ('mold-remediation-leads', 'Mold', 'Mold remediation leads: a planned job, not an emergency', 'Mold customers research for days. That changes the ads, the page and the offer.'),
 ('facebook-ads-for-restoration-companies', 'Facebook', 'Facebook ads for restoration companies: what our own money taught us', 'We spent $1,412 on Facebook water damage ads and got zero form leads. Here is what did work.'),
]
SERVICE_LABEL = {s[0]: s[1] for s in SERVICES}
ARTICLE_LABEL = {a[0]: a[2] for a in ARTICLES}

OWN = 'CDL Management, the company behind CDL Marketing, also owns and runs a disaster restoration company that handles water, fire and mold jobs.'


def header():
 nav = ''.join(f'<a href="{R}{s[0]}/">{s[1]}</a>' for s in SERVICES)
 return f'''<a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="{R}"><b>CDL</b>Marketing<small>Marketing for restoration companies</small></a><nav class="desktop-nav" aria-label="Main navigation"><details class="nav-services"><summary>Services</summary><div class="nav-popover">{nav}</div></details><a href="{R}#why">Why CDL</a><a href="{R}insights/">Insights</a><a href="{R}contact/" class="btn">Free audit <span aria-hidden="true">↗</span></a></nav></div><details class="mobile-disclosure"><summary class="menu-toggle" aria-controls="mobile-menu">Menu <span aria-hidden="true">☰</span></summary><nav id="mobile-menu" class="mobile-nav" aria-label="Mobile navigation"><a href="{R}">Restoration marketing</a>{nav}<a href="{R}#why">Why CDL</a><a href="{R}insights/">Insights</a><a href="{R}contact/">Free audit</a></nav></details></header>'''


def footer():
 services = ''.join(f'<a href="{R}{s[0]}/">{s[1]}</a>' for s in SERVICES)
 reads = ''.join(f'<a href="{R}insights/{a[0]}/">{a[2].split(":")[0]}</a>' for a in ARTICLES)
 return f'''<footer class="site-footer"><div class="wrap"><div class="footer-top"><div><a class="brand" href="{R}"><b>CDL</b>Marketing</a><p>Marketing for restoration companies.<br>From people who run one, too.</p><a href="tel:+12172171705">(217) 217-1705</a><br><a href="mailto:caleb@cdl1.net">caleb@cdl1.net</a></div><nav class="footer-links" aria-label="Service links"><b>What we do</b><a href="{R}">Restoration marketing</a>{services}</nav><nav class="footer-links" aria-label="Company links"><b>Read and reach us</b>{reads}<a href="{R}insights/">All restoration insights</a><a href="/about/">About CDL Marketing</a><a href="{R}contact/">Free marketing audit</a><a href="/">Marketing for flooring stores</a><a href="/privacy/">Privacy policy</a></nav></div><details id="privacy-choices" class="privacy-choices"><summary>Privacy choices</summary><p data-privacy-status role="status" aria-live="polite">Advertising measurement is off unless you allow it. Forms work either way.</p><div class="privacy-actions"><button type="button" class="privacy-choice" data-privacy-choice="allow" disabled>Allow advertising measurement</button><button type="button" class="privacy-choice" data-privacy-choice="decline" disabled>Decline advertising measurement</button><button type="button" class="privacy-choice" data-privacy-reload hidden>Reload to apply fully</button></div></details><div class="footer-bottom"><span>© 2026 CDL Management · CDL Marketing · Kirksville, Missouri</span><span>Restoration experience. Clear answers.</span></div></div></footer>'''


def org(base):
 o = dict(base)
 o['knowsAbout'] = list(base['knowsAbout']) + ['Restoration company marketing', 'SEO for restoration companies', 'Water damage lead generation', 'Google Ads and Local Services Ads for restoration companies', 'Restoration company website design']
 o['description'] = 'CDL Marketing is a marketing agency for independent restoration companies and independent flooring stores in the United States: websites, local SEO, Google Ads, Local Services Ads and AI search visibility.'
 o['disambiguatingDescription'] = "A marketing agency in Kirksville, Missouri for independent restoration companies and flooring stores. Not connected with commercial driver's license (CDL) training, trucking or driver recruitment companies."
 return o


def crumb_parent(path):
 if path.startswith(R + 'insights/') and path != R + 'insights/': return ('Restoration insights', R + 'insights/')
 if path.startswith(R) and path != R: return ('Restoration', R)
 return None


def cta(b):
 return '<section class="cta-band"><div class="wrap"><div><h2>Let’s look at your company.</h2><p>Start with a free marketing audit. No pressure. No obligation.</p></div>' + b.link(R + 'contact/', 'Get my free audit', 'btn') + '</div></section>'


def table(caption, head, rows):
 th = ''.join(f'<th scope="col">{h}</th>' for h in head)
 body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
 return f'<div class="tbl fit" role="region" aria-label="{caption}" tabindex="0"><table><caption>{caption}</caption><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


HOMEOWNER_ROWS = [
 ('water damage restoration near me', '246,000', '$41.70'),
 ('water damage restoration', '90,500', '$50.76'),
 ('mold remediation', '90,500', '$37.94'),
 ('mold removal', '74,000', '$31.91'),
 ('fire damage restoration', '60,500', '$37.72'),
 ('mold inspection near me', '33,100', '$26.97'),
 ('restoration companies near me', '18,100', '$30.77'),
 ('water damage repair', '9,900', '$63.64'),
 ('emergency water removal', '5,400', '$90.75'),
 ('flooded basement', '5,400', '$60.66'),
 ('burst pipe', '2,400', '$63.59'),
 ('sewage cleanup', '1,900', '$51.41'),
]


def homeowner_table():
 return table('What homeowners search, United States, per month', ['Search', 'Searches a month', 'Average ad click price'], HOMEOWNER_ROWS) + f'<p class="scope-note">Source: {DATA_NOTE} Click prices are national averages and your town will differ.</p>'


def keep_reading(slugs_services=(), slugs_articles=()):
 items = ''.join(f'<li><a href="{R}{s}/">{SERVICE_LABEL[s]}</a></li>' for s in slugs_services)
 items += ''.join(f'<li><a href="{R}insights/{a}/">{ARTICLE_LABEL[a]}</a></li>' for a in slugs_articles)
 return f'<h2>Keep reading</h2><ul>{items}<li><a href="{R}">Restoration marketing: how we work</a></li></ul>'


def aside_scope():
 return f'<aside><b>Month to month</b><p>No long contract. We agree the work and the fee in writing before anything starts, and your ad budget is paid straight to Google, never through us. If we don’t do what we say, let us go.</p><a href="{R}contact/">Ask for a free audit</a></aside>'


# ---------------------------------------------------------------- hub

HUB_FAQ = [
 ('What is restoration marketing?', 'Restoration marketing is the work that gets a water, fire or mold company found and called: your Google Business Profile, your website, Google Ads, Local Services Ads, reviews and now AI search. Most water jobs start with a phone search in an emergency, so the work is about being found fast and answering the call.'),
 ('Who do you work with?', 'Independent restoration companies in the United States that do water, fire and mold work with their own crew. We are built for the owner who is not part of a national franchise and has no corporate marketing department behind them.'),
 ('Do you sell leads?', 'No. We do not sell or resell leads. We build and run marketing in your own Google accounts, so the calls come to your number and go to nobody else. If you stop working with us, the accounts, the listing and the website stay yours.'),
 ('Is there a contract?', 'Marketing is month to month. We agree the work, the fee and the notice period in writing before anything starts. There is no 12-month term.'),
 ('What does it cost?', 'It depends on what you need, so we quote in writing after the free audit. Your ad budget is separate and is paid straight to Google. Water damage clicks are expensive almost everywhere, so we talk through a realistic budget for your market before you spend anything.'),
 ('Do you guarantee leads or rankings?', 'No. Nobody controls Google, the weather or how many pipes burst in your town. We promise the work, show it to you every month, and compare it with the calls and jobs you can verify.'),
 ('How long does it take?', 'Ads and Local Services Ads can bring calls within days of going live. Google listing and website changes usually take weeks to show. Ranking for the main phrases in a competitive city takes months.'),
]


def hub(b):
 cards = ''.join(f'<article class="service-card"><span class="article-type">0{i} · {s[2]}</span><h3>{s[1]}</h3><p>{s[3]}</p>{b.link(R + s[0] + "/", "See how it works")}</article>' for i, s in enumerate(SERVICES, 1))
 reads = ''.join(f'<article class="service-card"><span class="article-type">{a[1]}</span><h3>{a[2]}</h3><p>{a[3]}</p>{b.link(R + "insights/" + a[0] + "/", "Read it")}</article>' for a in ARTICLES[:3])
 body = f'''<section class="hero" id="top"><div class="wrap"><div class="hero-copy"><span class="eyebrow">For independent restoration companies</span><h1>Restoration marketing.<br><span>From people who run one.</span></h1><p class="intro">CDL Marketing does marketing for independent water, fire and mold restoration companies. We own and run a restoration company ourselves, so we have paid for these clicks with our own money. SEO, Google Ads, Local Services Ads, websites and AI search. Month to month.</p><div class="hero-actions">{b.link(R + 'contact/', 'Get my free marketing audit', 'btn')}{b.link(R + 'insights/restoration-company-marketing/', 'Read the guide')}</div><p class="hero-note">We look at your Google listing, your website and your ads, and send three things to fix.<br>Free, with no obligation. Or call <a href="tel:+12172171705">(217) 217-1705</a>.</p></div></div></section><div class="trust-strip"><div class="wrap trust-inner"><span>We run a restoration company too</span><span>Water</span><span>Fire</span><span>Mold</span></div></div>
 <section class="section" id="services"><div class="wrap"><div class="section-heading"><span class="eyebrow">What we do</span><h2>Four jobs.<br>One goal: the phone rings.</h2><p>A burst pipe does not wait, and neither does the homeowner. They search on a phone, call the first company that looks real, and the job is gone in minutes. Everything we do is built around that moment.</p></div><div class="cards two-cards">{cards}</div></div></section>
 <section class="section light" id="why"><div class="wrap split"><div><span class="eyebrow">Why CDL</span><h2>We have paid for<br>these clicks ourselves.</h2><p>{OWN} We run its Google Ads, its Local Services Ads, its website and its Google listing, and we judge all of it on booked jobs.</p><p>That means the advice on this site is not theory. Some of what we found in our own accounts:</p><ul class="reason-list"><li><b>The lead is a phone call.</b> Over one 30-day stretch, every lead our Google accounts recorded was a call. In one market, 5 came from search ads and 12 from Local Services Ads.</li><li><b>Water clicks are expensive, even in a small town.</b> Google’s first-page price on our water damage searches ran from $15.53 to $59.43 a click.</li><li><b>Facebook did not sell water damage.</b> We spent $1,412 on two campaigns and got zero form leads. It did sell mold inspections and cleaning jobs.</li><li><b>Money leaks quietly.</b> In one campaign, about 83% of the spend was going to people who searched our own company name.</li></ul>{b.link(R + 'insights/facebook-ads-for-restoration-companies/', 'See the Facebook numbers')}</div><div class="quote-panel"><span class="eyebrow">Our approach is different</span><h3>No long contract.<br>Just the work.</h3><p class="muted">Plenty of restoration owners have signed a 12-month marketing contract and watched very little happen. Our approach is different. If we don’t do what we say, you can let us go and move on.</p><p class="muted">Google changes all the time. So we check the work days later, not a year later, and adjust. Your accounts, your listing and your website stay yours the whole way through.</p><p class="scope-note">We do not sell shared leads, and we do not promise a number of jobs. We promise the work and show it to you.</p></div></div></section>
 <section class="section"><div class="wrap article-layout"><span class="eyebrow">What your customers type</span><h2>The searches behind your next job</h2><p>These are real monthly search counts from Google for the whole country. The click prices show why a wasted click hurts more in restoration than in almost any other trade.</p>{homeowner_table()}<p>Two things stand out. Emergency water searches are the most expensive clicks, so the page and the phone number have to be right before you pay for them. And mold is searched almost as often as water, by people who are planning, not panicking. They need a different page and a different ad.</p><p>{b.link(R + 'seo/', 'How we approach SEO for restoration companies')}</p></div></section>
 <section class="section light"><div class="wrap"><div class="section-heading"><span class="eyebrow">How it starts</span><h2>Know the next step.<br>Know what you are buying.</h2></div><div class="process"><article><span class="step-number">01</span><h3>A free audit.</h3><p>We look at your Google listing, your website on a phone and any ads you run. You get three things to fix, in plain words.</p></article><article><span class="step-number">02</span><h3>A written plan.</h3><p>What we will do, what it costs, what we need from you and a realistic ad budget for your market. You approve it before it starts.</p></article><article><span class="step-number">03</span><h3>Work you can check.</h3><p>Calls are tracked to the ad or page that caused them. Each month we show what changed and compare it with the jobs you booked.</p></article></div></div></section>
 <section class="section"><div class="wrap faq-layout"><div class="section-heading"><span class="eyebrow">Straight answers</span><h2>Before you<br>choose an agency.</h2><p>How we work and what to expect.</p>{b.link(R + 'contact/', 'Ask us something else')}</div>{b.faqs(HUB_FAQ)}</div></section>
 <section class="section light"><div class="wrap"><div class="section-heading"><span class="eyebrow">Notes from the job</span><h2>Useful answers.<br>No marketing lecture.</h2></div><div class="cards">{reads}</div><p class="inline-note">{b.link(R + 'insights/', 'Read all restoration insights')}</p></div></section>''' + cta(b)
 desc = 'Restoration marketing for independent water, fire and mold companies, from a team that runs a restoration company: SEO, Google Ads, websites and AI search.'
 schema = [{'@type': 'Service', 'name': 'Restoration marketing', 'serviceType': 'Marketing for restoration companies', 'provider': {'@id': b.DOMAIN + '/#organization'}, 'areaServed': {'@type': 'Country', 'name': 'United States'}, 'audience': {'@type': 'BusinessAudience', 'name': 'Independent water, fire and mold restoration companies'}, 'url': b.DOMAIN + R, 'description': desc}, b.faq_schema(HUB_FAQ)]
 b.write(R, 'Restoration Marketing for Independent Companies | CDL', desc, body, schema, section='restoration')


# ---------------------------------------------------------------- service pages

SEO_FAQ = [
 ('What is SEO for a restoration company?', 'It is the work that gets your company shown when someone nearby searches for water damage, fire damage or mold help: a complete Google Business Profile, a page for each service, a page for each town you really serve, steady reviews and a website that loads fast on a phone.'),
 ('How long does restoration SEO take?', 'Google listing fixes can show within a few weeks. Ranking a service page in a mid-size city usually takes several months, and longer where national franchises and lead sellers already hold the top spots. We tell you which phrases are realistic before we start.'),
 ('Do I still need ads if I do SEO?', 'For emergency water jobs, usually yes. Ads and Local Services Ads sit above the map and the normal results, and that is where a panicked homeowner taps. SEO lowers what you depend on ads for over time, and it carries mold and fire searches where people read before they call.'),
 ('Should I have a page for every town?', 'Only for towns you really serve, and only if each page says something true and specific: drive time, the kinds of homes, jobs you have done there. Fifty copies of one page with the town name swapped do not rank and can hurt the site.'),
 ('Can you rank me above the franchises?', 'In the map results, an independent with a complete listing, real reviews and a nearby address often does. In the normal results for a big city it is harder. We do not promise positions. We show you where you stand now and report honestly as it moves.'),
]

LEADS_FAQ = [
 ('How do I get water damage leads?', 'The steady sources are Google Local Services Ads, Google search ads, your Google Business Profile, your own website, plumber and insurance agent referrals, and past customers. Paid lead lists are a seventh source, and usually the most expensive per booked job because the same lead is sold to several companies.'),
 ('How much does a water damage lead cost?', 'It varies a lot by market. Nationally, Google reports average click prices of about $42 to $91 on emergency water searches, and it takes several clicks to make one call. In our own small markets, Google’s first-page price ran from $15.53 to $59.43 a click. We work out a realistic cost per call for your town before you spend.'),
 ('Should I buy water damage leads?', 'Sometimes it makes sense as a top-up, but ask first whether the lead is exclusive, how old it is, how it was generated and what the refund rule is. A lead generated in your own account is yours alone and builds your own listing and reviews. A bought lead builds the seller’s.'),
 ('Are Local Services Ads better than Google Ads?', 'They do different jobs and most restoration companies should run both. Local Services Ads sit at the very top, charge per lead and lean heavily on your reviews and how fast you answer. Search ads give you control over the exact searches, towns and hours. In one of our own markets, Local Services Ads brought 12 leads in a month and search ads brought 5.'),
 ('Do you sell leads or use shared call numbers?', 'No. The ads run in your own Google accounts and the calls ring your own phone. We add a tracking number so you can see which ad caused each call, and that number is yours.'),
]

WEB_FAQ = [
 ('What should a restoration company website have?', 'The phone number at the top of every page as a button, a clear list of what you do and where, proof that you are real (reviews, photos of your own crew and trucks, licenses and certifications you actually hold), a page for each service, and a short form for people who are not in an emergency.'),
 ('Do I need a new website?', 'Not always. If your current site loads fast on a phone, shows the number first and you can edit it, we can work with it. We check that in the free audit before recommending a rebuild.'),
 ('Why does speed matter so much?', 'Because the visitor is often standing in water. If the page takes six seconds to load on a phone, they go back and tap the next company. Every paid click that leaves before the page loads is money spent on nothing.'),
 ('Who owns the website?', 'You do. Your domain and your accounts stay in your name. If you stop working with us, you keep the site.'),
 ('Can you use stock photos?', 'We would rather not. Real photos of your crew, trucks and equipment do more to prove you are a real local company than any stock picture. A phone photo is fine. We never use a customer’s home or name without their permission.'),
]

AI_FAQ = [
 ('Do people really ask AI for a restoration company?', 'Some do, and Google now shows AI answers above the normal results for many searches. It matters most for the research questions: what to do after a flood, whether insurance covers it, what mold remediation involves, and who in town does it.'),
 ('How does an AI tool decide which company to name?', 'It reads what is published about you: your website, your Google Business Profile, reviews, directories and local news. It repeats companies whose facts are clear and the same everywhere. Nobody can pay to be named in the answer itself.'),
 ('Is AI search a replacement for SEO?', 'No. It is the same groundwork: accurate company facts, useful pages and real reviews. AI search work makes those facts easier for a machine to read and quote.'),
 ('Can you guarantee ChatGPT will recommend us?', 'No, and nobody honestly can. We can make your facts clear, consistent and easy to quote, check what the main AI tools say about you today, and report how that changes.'),
]

SERVICE_PAGES = {
 'seo': {
  'title': 'SEO for Restoration Companies | Water Damage SEO | CDL',
  'desc': 'SEO for restoration companies: Google Business Profile, service and town pages, reviews and speed, from a team that runs its own restoration company.',
  'label': 'SEO for restoration companies',
  'h1': 'SEO for restoration companies that need the phone to ring.',
  'intro': 'Your Google listing, your service pages and your reviews, worked on every month by people who run a restoration company themselves.',
  'answer': 'SEO for a restoration company means showing up when someone nearby types "water damage restoration near me" or "mold removal", and looking like the obvious company to call. Most of it comes down to four things: a complete Google Business Profile, a real page for each service, steady reviews, and a site that loads fast on a phone.',
  'toc': [('searches', 'What people search'), ('map', 'The map comes first'), ('pages', 'Service and town pages'), ('reviews', 'Reviews'), ('honest', 'What SEO will not do'), ('work', 'What we do each month')],
  'body': lambda b: f'''<section id="searches"><h2>What people actually search</h2><p>Before aiming a page at a phrase, check that people type it. These are real monthly counts for the United States.</p>{homeowner_table()}<p>"Near me" searches dwarf everything else. Google answers those from the map, using where the searcher is standing, so your listing matters more than any blog post.</p></section>
<section id="map"><h2>The map comes first</h2><p>For an emergency search, Google shows ads, then Local Services Ads, then three companies on a map. Many people never scroll past that. To be one of the three you need:</p><ul><li><b>The right categories.</b> Water damage restoration as the main one, with fire and mold added if you do them.</li><li><b>Every service listed.</b> Water extraction, drying, sewage cleanup, mold remediation, board-up, contents. Google matches searches to these.</li><li><b>Real hours.</b> If you answer at 2 am, the listing should say open 24 hours.</li><li><b>Fresh photos.</b> Your trucks, your crew and your equipment, added every week or two.</li><li><b>An address that is really yours.</b> Google ranks nearby companies first, and fake addresses get listings suspended.</li></ul></section>
<section id="pages"><h2>Service and town pages</h2><p>One page that says "we do water, fire and mold" will not rank for all three. Each service needs its own page that answers the questions a homeowner has: what happens first, how long drying takes, whether you work with their insurance, what it might cost.</p><p>Town pages work when they are true. If you really serve a town 30 minutes away, say how fast you get there and what you see in those homes. Do not publish fifty copies of one page with the town name swapped. It does not rank, and it makes the whole site look thin.</p></section>
<section id="reviews"><h2>Reviews</h2><p>Reviews decide who gets the call when three companies look the same. They also weigh heavily in Local Services Ads. The simple system that works: ask every customer when the job is finished, by text, with a direct link. Reply to every review, good or bad, within a couple of days. Write the reply for the next person reading, not the upset one.</p></section>
<section id="honest"><h2>What SEO will not do</h2><p>It will not make it rain, and it will not beat an ad to the top of the screen. In our own restoration company, emergency water calls come mostly from paid placements, because that is where a person in a hurry taps. SEO earns its keep on the map, on mold and fire searches where people read first, and by making every ad click land on a page that looks trustworthy.</p><p>It also takes time. In a big city, the first page for "water damage restoration" is held by national franchises and lead sellers. We tell you which phrases are realistic for your market before we start.</p></section>
<section id="work"><h2>What we do each month</h2><ul><li>Keep the Google listing complete: services, hours, photos, posts and questions answered.</li><li>Write or improve one service or town page.</li><li>Send review requests and draft replies.</li><li>Check phone speed and fix what slows the site.</li><li>Check where you show on the map from several points around town, not just from your office.</li><li>Send a plain report: what we did, what moved, how many calls came in.</li></ul></section>''',
  'faq': SEO_FAQ, 'related_s': ['water-damage-leads', 'websites'], 'related_a': ['restoration-company-marketing', 'mold-remediation-leads'],
 },
 'water-damage-leads': {
  'title': 'Water Damage Leads Without Shared Lead Lists | CDL',
  'desc': 'Water damage leads from your own Google Ads and Local Services Ads, not shared lists. Real click prices and lessons from our own restoration company.',
  'label': 'Water damage leads',
  'h1': 'Water damage leads that ring your phone and nobody else’s.',
  'intro': 'Google Ads and Local Services Ads built in your own accounts, by people who have paid for these clicks themselves.',
  'answer': 'The most reliable way to get water damage leads is to be at the top of Google when a pipe bursts: Local Services Ads first, search ads second, the map third. Those leads are calls to your own number. A bought lead is usually sold to several companies at once.',
  'toc': [('why', 'Why the lead is a call'), ('lsa', 'Local Services Ads'), ('search', 'Google search ads'), ('leaks', 'Where the money leaks'), ('bought', 'Buying leads'), ('work', 'What we do')],
  'body': lambda b: f'''<section id="why"><h2>Why the lead is a phone call</h2><p>Nobody fills in a form with water coming through the ceiling. In our own restoration company, over one 30-day stretch every lead our Google accounts recorded was a phone call. The website form recorded none.</p><p>So the whole setup has to serve the call: the number at the top of the page as a button, call tracking so you know which ad caused it, and someone who answers. An ad that rings a phone nobody picks up is the most expensive mistake in this trade.</p></section>
<section id="lsa"><h2>Google Local Services Ads</h2><p>These are the boxes at the very top of Google with a badge, your star rating and a call button. You pay per lead, not per click. To run them you go through Google’s checks on your license and insurance.</p><p>In one of our own markets, Local Services Ads brought 12 leads in a month and regular search ads brought 5. What moves you up is mostly reviews, how close you are, and how quickly you answer. Miss the calls and Google shows you less.</p></section>
<section id="search"><h2>Google search ads</h2><p>Search ads let you choose the exact searches, towns and hours. They are also where restoration money gets burned, because the clicks cost so much.</p>{table('Emergency water searches, United States', ['Search', 'Searches a month', 'Average ad click price'], [r for r in HOMEOWNER_ROWS if r[0] in ('water damage restoration near me', 'water damage restoration', 'water damage repair', 'emergency water removal', 'flooded basement', 'burst pipe', 'sewage cleanup')])}<p class="scope-note">Source: {DATA_NOTE}</p><p>Even in our own small markets, Google’s first-page price on water damage searches ran from $15.53 to $59.43 a click. When our bids were capped at $15, the ads barely showed. Raising the cap to $30 is what got them seen. A budget that is too small for your market does not buy cheap leads. It buys none.</p></section>
<section id="leaks"><h2>Where the money leaks</h2><p>These all came out of our own accounts.</p><ul><li><b>Paying for your own name.</b> In one water damage campaign, about 83% of the spend was going to people searching our company name, at up to $26 a click. They would have found us anyway. We blocked our name in that campaign.</li><li><b>The wrong location setting.</b> Google’s default shows ads to people "interested in" your area, not only people in it. We switched every campaign to people physically there.</li><li><b>Desktop clicks.</b> In one campaign, desktop cost about $300 in a month at about $23 a click and produced no recorded leads, three periods in a row. We cut desktop bids by 80%.</li><li><b>Mold clicks in a water campaign.</b> Blocking "mold" is not enough. Google treats "mildew" and "mould" as different words, so each has to be blocked.</li><li><b>No tracking.</b> We found a booking page with no ad tracking on it at all, so the ads sending people there could not report one booking. If you cannot see which ad made the phone ring, you cannot fix anything.</li></ul></section>
<section id="bought"><h2>Buying leads</h2><p>Lead sellers rank well for "water damage leads" because that is their business. Some are fine as a top-up. Before you pay, ask:</p><ul><li>Is the lead sold to me only, or to several companies?</li><li>Is it a live call, or a form filled in an hour ago?</li><li>How was it generated, and under whose name?</li><li>What is the refund rule for wrong numbers and out-of-area calls?</li><li>Can I stop any month?</li></ul><p>The deeper cost: a bought lead builds the seller’s listing and reviews, not yours. {b.link(R + 'insights/how-to-get-water-damage-leads/', 'More on the six sources of water damage jobs')}</p></section>
<section id="work"><h2>What we do</h2><ul><li>Set up or clean up Local Services Ads and search ads in your own Google accounts.</li><li>Split water, fire and mold into separate campaigns with their own pages.</li><li>Put call tracking on every ad and page, with numbers you own.</li><li>Check search terms every week and block the waste.</li><li>Agree a realistic budget for your market first. The ad money goes straight to Google.</li><li>Report cost per call and, with your help, cost per booked job.</li></ul></section>''',
  'faq': LEADS_FAQ, 'related_s': ['seo', 'websites'], 'related_a': ['how-to-get-water-damage-leads', 'facebook-ads-for-restoration-companies'],
 },
 'websites': {
  'title': 'Restoration Company Websites That Get the Call | CDL',
  'desc': 'Restoration company website design built for a phone in an emergency: number first, fast pages, a page per service and call tracking on every button.',
  'label': 'Restoration websites',
  'h1': 'A restoration company website built for someone standing in water.',
  'intro': 'Fast pages, the phone number first, and a separate page for water, fire and mold. Built by people who run a restoration company.',
  'answer': 'A restoration company website has one main job: turn a worried visitor on a phone into a call within seconds. That means the number at the top as a button, a page that loads fast, plain proof that you are a real local company, and a separate page for each service.',
  'toc': [('first', 'The first screen'), ('service', 'One page per service'), ('proof', 'Proof you are real'), ('speed', 'Speed'), ('tracking', 'Tracking'), ('work', 'What we build')],
  'body': lambda b: f'''<section id="first"><h2>The first screen</h2><p>Most visitors decide before they scroll. On our own restoration pages the call button sits directly under the headline, and a call bar stays on screen as the visitor moves down the page. The first screen should answer three questions without a single tap:</p><ul><li>Do you do what I need?</li><li>Do you come to my town?</li><li>How do I reach a person right now?</li></ul></section>
<section id="service"><h2>One page per service</h2><p>A water damage customer and a fire customer are in different places. Our fire pages are written around the hours after the fire department leaves: board-up, securing the house, what to keep and what not to touch. Our mold pages are written around an honest inspection, because that customer is deciding who to trust, not racing a clock.</p><p>Separate pages also let each ad land on the right message, which lowers what you pay per call.</p></section>
<section id="proof"><h2>Proof you are real</h2><p>The visitor is about to let a stranger into a damaged home. Show them:</p><ul><li>Your real Google rating and a few real reviews, used with permission.</li><li>Photos of your own crew, trucks and equipment.</li><li>The certifications and licenses you actually hold.</li><li>How long you have been doing this, if it is true and you can back it up.</li><li>The towns you serve, by name.</li></ul><p>Do not invent any of it. One wrong date or fake badge undoes the rest.</p></section>
<section id="speed"><h2>Speed</h2><p>A paid water damage click often costs $40 or more. If the page takes six seconds to appear on a phone, part of that money leaves before your headline shows. We load fonts and pictures so the text and the call button appear at once, even on a weak signal in a basement.</p></section>
<section id="tracking"><h2>Tracking</h2><p>Every call button and every form reports back to the ad that caused it. That sounds basic, and it is often missing. We have found it missing on a page of our own. Without it, every decision about the ad budget is a guess.</p></section>
<section id="work"><h2>What we build</h2><ul><li>A home page and a separate page each for water, fire and mold, plus the towns you really serve.</li><li>Phone number first, call bar on every page, a short form for non-emergencies.</li><li>Call and form tracking tied to your ads.</li><li>Pages written in plain words, with your real photos and reviews.</li><li>Your domain and accounts stay in your name.</li></ul><p>You may not need a new site at all. We check your current one in the {b.link(R + 'contact/', 'free audit')} first.</p></section>''',
  'faq': WEB_FAQ, 'related_s': ['water-damage-leads', 'seo'], 'related_a': ['restoration-company-marketing'],
 },
 'ai-search': {
  'title': 'AI Search for Restoration Companies | CDL Marketing',
  'desc': 'Help ChatGPT and Google AI answers find and name your restoration company: clear company facts, useful answers and consistent listings. No promises.',
  'label': 'AI search',
  'h1': 'AI search for restoration companies: be the name the answer gives.',
  'intro': 'People now ask ChatGPT and Google’s AI answers who to call. We make your company’s facts clear enough to be read and repeated.',
  'answer': 'AI search work for a restoration company means making sure tools like ChatGPT and Google’s AI answers can find accurate facts about you: what you do, where, how to reach you and what customers say. It rests on the same groundwork as SEO, written so a machine can quote it.',
  'toc': [('where', 'Where it matters'), ('how', 'How AI picks a company'), ('work', 'What we do'), ('honest', 'What we cannot promise')],
  'body': lambda b: f'''<section id="where"><h2>Where it matters for restoration</h2><p>Someone with water on the floor still taps the first call button they see. AI answers matter more for the questions people ask before and after that moment:</p><ul><li>"What should I do first after a pipe bursts?"</li><li>"Does homeowners insurance cover water damage?" (about 1,600 searches a month)</li><li>"How much does mold remediation cost?" (about 9,900 a month for "mold remediation cost")</li><li>"Who does fire damage cleanup near me?"</li></ul><p>A company whose website answers these plainly is the one an AI tool can quote and name.</p><p class="scope-note">Source: {DATA_NOTE}</p></section>
<section id="how"><h2>How an AI tool picks a company</h2><p>It reads what is published about you and repeats what it finds in more than one place. So the basics decide it:</p><ul><li>Your name, address, phone and services are the same on your site, your Google listing and the main directories.</li><li>Your website states plainly what you do and where, in words, not only in pictures.</li><li>You have real reviews that mention the kind of work.</li><li>Your pages answer real questions in short, direct paragraphs.</li></ul><p>Nobody can pay to be named in the answer.</p></section>
<section id="work"><h2>What we do</h2><ul><li>Check what ChatGPT, Google’s AI answers and others say about you today, and what they get wrong.</li><li>Fix company facts that differ from one place to another.</li><li>Add the behind-the-page data that tells machines who you are, what you do and where.</li><li>Write plain answers to the questions your customers ask, on your own site.</li><li>Re-check and report every month.</li></ul></section>
<section id="honest"><h2>What we cannot promise</h2><p>AI answers change from day to day and from person to person. We cannot promise you will be named, and you should be careful with anyone who does. What we can do is make your facts clear, consistent and easy to quote, and show you honestly what the tools say.</p><p>Google’s own guidance says the same basics apply: <a href="https://developers.google.com/search/docs/appearance/ai-features">Google Search Central: AI features and your website</a>.</p></section>''',
  'faq': AI_FAQ, 'related_s': ['seo', 'websites'], 'related_a': ['restoration-company-marketing'],
 },
}


def service_pages(b):
 for slug, d in SERVICE_PAGES.items():
  path = R + slug + '/'
  toc = '<nav class="toc" aria-label="On this page"><b>On this page</b>' + ''.join(f'<a href="#{i}">{t}</a>' for i, t in d['toc']) + '</nav>'
  faq = '<section class="section light" id="questions"><div class="wrap faq-layout"><div class="section-heading"><span class="eyebrow">Common questions</span><h2>' + d['label'] + '<br>questions.</h2></div>' + b.faqs(d['faq']) + '</div></section>'
  body = b.subhero(d['label'], d['h1'], d['intro'], path) + f'<section class="section"><div class="wrap article-layout"><p class="answer">{d["answer"]}</p>{toc}{d["body"](b)}{aside_scope()}<aside><b>Why listen to us</b><p>{OWN} The figures on this page that say "our own" come from its real ad accounts.</p><a href="{R}#why">Why CDL</a></aside>{keep_reading(d["related_s"], d["related_a"])}</div></section>' + faq + cta(b)
  schema = [{'@type': 'Service', 'name': d['label'][0].upper() + d['label'][1:] + (' for restoration companies' if 'restoration' not in d['label'].lower() and 'water' not in d['label'].lower() else ''), 'serviceType': d['label'], 'provider': {'@id': b.DOMAIN + '/#organization'}, 'areaServed': {'@type': 'Country', 'name': 'United States'}, 'audience': {'@type': 'BusinessAudience', 'name': 'Independent water, fire and mold restoration companies'}, 'url': b.DOMAIN + path, 'description': d['desc']}, b.faq_schema(d['faq'])]
  b.write(path, d['title'], d['desc'], body, schema, section='restoration')


# ---------------------------------------------------------------- articles

GUIDE_FAQ = [
 ('How do I market a restoration company?', 'Start with the Google Business Profile and a fast website with the phone number first. Add Local Services Ads and search ads for emergency water jobs, a steady review system, and referral relationships with plumbers and insurance agents. Track every call back to its source so you know what to keep.'),
 ('What is the best advertising for water damage restoration?', 'Paid placements at the top of Google: Local Services Ads and search ads. Emergency customers call from there. In our own restoration company, Facebook ads did not sell water damage at all.'),
 ('How much should a restoration company spend on marketing?', 'There is no honest single number. It depends on what clicks cost in your market, how many jobs your crew can take and what a job is worth to you. Work backwards: cost per call, calls per booked job, and what you can afford to pay for a job.'),
 ('Does social media work for restoration companies?', 'Not for emergencies. It can work for planned services such as mold inspections, carpet cleaning and duct cleaning, and it helps people recognize your name later.'),
]

LEADGUIDE_FAQ = [
 ('What is the cheapest way to get water damage leads?', 'A complete Google Business Profile, a steady flow of reviews and referrals from plumbers and insurance agents cost time rather than ad money. They build slowly. Ads bring calls sooner at a higher price.'),
 ('Are exclusive water damage leads worth it?', 'An exclusive live call can be worth paying for. Check that exclusive really means sold to one company, that it is a live call and not an old form, and that there is a refund rule in writing.'),
 ('How many clicks does it take to get a water damage call?', 'It depends on the page, the hour and the market, so measure it in your own account instead of trusting an average. That is why call tracking has to be in place before you judge a campaign.'),
 ('Why are water damage clicks so expensive?', 'Because one job can be worth thousands of dollars, and franchises, lead sellers and local companies all bid on the same few searches. Google reports national average click prices of about $42 to $91 on emergency water searches.'),
]

MOLD_FAQ = [
 ('How do I get mold remediation leads?', 'Run mold as its own campaign with its own page. Mold customers research before they call, so they respond to a clear inspection offer, plain answers about cost and health, and reviews. Search ads, your Google listing and Facebook can all work for mold.'),
 ('Do Facebook ads work for mold remediation?', 'In our own restoration company, yes, for inspections. Mold inspection leads from Facebook cost us $57.80 each, while water damage ads on Facebook produced no form leads at all.'),
 ('Should I offer free mold inspections?', 'Only if you really do them free and can keep up with the requests. Do not advertise a free inspection you do not offer. An honest, clearly priced inspection also works, and it brings fewer people who were never going to buy.'),
 ('Why keep mold and water in separate campaigns?', 'Different customer, different urgency, different click price. Mixed together, mold searches eat a water budget. Block mold, mildew and mould in the water campaign, because Google treats each as a different word.'),
]

FB_FAQ = [
 ('Do Facebook ads work for water damage restoration?', 'Not in our experience. We spent $1,412 on two Facebook water damage campaigns for our own restoration company and got zero form leads. Thirteen calls were placed and two were confirmed. Emergency customers search Google. They are not scrolling Facebook.'),
 ('What restoration services sell on Facebook?', 'Planned ones. In our own account, carpet cleaning leads cost $41.06, duct cleaning $48.82 and mold inspections $57.80.'),
 ('Should I target a small area on Facebook?', 'Be careful. When we narrowed our Facebook ads to a tight local area, cost per lead roughly tripled: carpet cleaning went from $41.06 to $127.50 and duct cleaning from $48.82 to $140.62.'),
 ('Are Facebook giveaways good for leads?', 'They are cheap and mostly worthless as leads. Ours cost $2.13 to $6.24 each, and the people were entering a contest, not buying a service.'),
]


def a_guide(b):
 return f'''<p class="answer">Restoration company marketing comes down to one moment: someone has water, smoke or mold in the house, searches on a phone and calls the first company that looks real. This guide covers what to fix first, where the calls come from and what we learned running our own restoration company.</p>
<h2>Start with how your customer finds you</h2><p>There are two kinds of restoration customer, and they need different marketing.</p><ul><li><b>The emergency.</b> A burst pipe, a flooded basement, a fire. They search, tap a call button and hire whoever answers. This is decided in minutes.</li><li><b>The planned job.</b> Mold, a musty crawl space, smoke smell, carpet and duct cleaning. They read, compare and ask around for days.</li></ul><p>Most wasted restoration marketing comes from treating the two the same.</p>{homeowner_table()}
<h2>Fix these first, in this order</h2><ol><li><b>Answer the phone.</b> Day and night, by a person. Every other step sends more calls to this one.</li><li><b>Your Google Business Profile.</b> Right categories, every service listed, real hours, fresh photos of your own trucks and crew.</li><li><b>Your website on a phone.</b> Number at the top as a button. Loads in a couple of seconds. A separate page for water, fire and mold.</li><li><b>Call tracking.</b> A number per source so you know what caused each call.</li><li><b>Reviews.</b> Ask every customer when the job is done. Reply to every one.</li></ol><p>None of this costs ad money, and all of it makes ads cheaper when you add them. {b.link(R + 'seo/', 'More on SEO for restoration companies')}</p>
<h2>Then add paid placements</h2><p>For emergency water jobs, the top of Google is paid. Local Services Ads come first, then search ads, then the map.</p><p>In our own restoration company, over one 30-day stretch every lead our Google accounts recorded was a phone call. In one market, 12 came from Local Services Ads and 5 from search ads. We also learned that a budget too small for the market buys nothing: with bids capped at $15 our ads barely showed, because Google’s first-page price there ran from $15.53 to $59.43 a click. {b.link(R + 'water-damage-leads/', 'How we run water damage ads')}</p>
<h2>Do not skip the old-fashioned sources</h2><p>Plumbers, insurance agents, property managers and past customers send the best jobs many restoration companies get. No agency can build those relationships for you. What marketing can do is make you easy to recommend: a name people recognize, a site that looks trustworthy and reviews that back up the referral.</p>
<h2>What we would not spend on</h2><ul><li><b>Facebook ads for water damage.</b> We spent $1,412 and got zero form leads. {b.link(R + 'insights/facebook-ads-for-restoration-companies/', 'The full numbers')}</li><li><b>Giveaways.</b> Cheap entries, not customers.</li><li><b>Fifty copied town pages.</b> They do not rank.</li><li><b>A long contract.</b> You should be able to leave any month.</li></ul>
<h2>How to judge any marketing, ours included</h2><p>Count booked jobs, not clicks or impressions. For each source, know three numbers: what you spent, how many real calls came in and how many became jobs. If your agency cannot show you those, ask why.</p>'''


def a_leads(b):
 return f'''<p class="answer">You can get water damage leads from six places: Local Services Ads, Google search ads, your Google listing, your own website, referrals and past customers. Bought lead lists are a seventh. The first six ring your own phone and build your own name. Here is what each costs and how to choose.</p>
<h2>The six sources you own</h2>{table('Where water damage jobs come from', ['Source', 'What you pay', 'How fast', 'Watch out for'], [
 ('Google Local Services Ads', 'Per lead', 'Days', 'Missed calls push you down'),
 ('Google search ads', 'Per click, often $40 or more', 'Days', 'Waste: wrong searches, wrong places'),
 ('Google Business Profile', 'Time', 'Weeks', 'Needs steady reviews and photos'),
 ('Your website and SEO', 'Time', 'Months', 'Slow in big cities'),
 ('Plumbers, agents, property managers', 'Time and trust', 'Months', 'Only you can build it'),
 ('Past customers', 'Almost nothing', 'Ongoing', 'They forget your name'),
])}
<h2>What a click really costs</h2><p>Google reports these national averages for emergency water searches.</p>{table('Emergency water searches, United States', ['Search', 'Searches a month', 'Average ad click price'], [r for r in HOMEOWNER_ROWS if r[0] in ('water damage restoration near me', 'water damage restoration', 'water damage repair', 'emergency water removal', 'flooded basement', 'burst pipe')])}<p class="scope-note">Source: {DATA_NOTE}</p><p>In our own restoration company’s small markets, Google’s first-page price on water searches ran from $15.53 to $59.43 a click. It takes more than one click to make a call, so work out your own cost per call before judging a month.</p>
<h2>Buying leads: seven questions</h2><p>Sellers of water damage leads rank at the top of Google for that phrase. Before you sign up, ask:</p><ol><li>Is each lead sold only to me?</li><li>Is it a live phone call or a form?</li><li>How old is it when I get it?</li><li>Whose name was on the ad or page that produced it?</li><li>What is refunded: wrong numbers, out of area, renters with no authority?</li><li>Is there a minimum spend or a contract?</li><li>What happens to my leads if I stop?</li></ol><p>A bought lead can fill a slow week. But it builds the seller’s listing, reviews and rankings, never yours. The day you stop paying, you have nothing left.</p>
<h2>What to do this week</h2><ul><li>Call your own number at 9 pm and see who answers.</li><li>Open your website on a phone on mobile data. Count the seconds until the call button shows.</li><li>Search "water damage restoration near me" from three places in your service area and see whether you are on the map.</li><li>Check that every ad and page has its own tracking number.</li></ul><p>If you want a second pair of eyes, {b.link(R + 'contact/', 'ask for a free audit')}. {b.link(R + 'water-damage-leads/', 'Or see how we run water damage ads')}</p>'''


def a_mold(b):
 return f'''<p class="answer">Mold remediation leads come from people who are planning, not panicking. They search for days, read about health and cost, and compare companies. That makes mold cheaper to advertise than water damage, and it means the page, the ad and the offer all have to be different.</p>
<h2>How big the mold market is</h2>{table('Mold searches, United States', ['Search', 'Searches a month', 'Average ad click price'], [
 ('mold remediation', '90,500', '$37.94'), ('mold removal', '74,000', '$31.91'), ('mold remediation near me', '49,500', '$35.67'), ('mold inspection near me', '33,100', '$26.97'), ('mold testing near me', '33,100', '$26.97'), ('mold inspection', '22,200', '$23.32'), ('black mold removal', '9,900', '$20.44'), ('mold remediation cost', '9,900', '$20.78'),
])}<p class="scope-note">Source: {DATA_NOTE}</p><p>Mold is searched almost as often as water damage, and the clicks cost less. Many restoration companies treat it as an afterthought.</p>
<h2>Give mold its own campaign and page</h2><p>If mold shares a campaign with water, two things go wrong. Mold searches drain the water budget, and mold customers land on a page shouting about emergencies they do not have.</p><p>In our own restoration company’s accounts we block mold words in the water campaign. One detail matters: Google does not treat "mold", "mildew" and "mould" as the same word, so all three have to be blocked.</p>
<h2>What a mold customer needs to see</h2><ul><li><b>An honest inspection.</b> What you look at, what it costs or whether it is free, and what happens next. Do not advertise a free inspection unless you really offer one.</li><li><b>Plain answers.</b> Is it dangerous, do I have to move out, will insurance pay, how long does it take.</li><li><b>No scare tactics.</b> This customer has read a lot of frightening things already. Calm and specific wins.</li><li><b>Reviews that mention mold.</b></li><li><b>A form as well as a phone number.</b> Unlike water customers, mold customers do fill in forms.</li></ul>
<h2>Where Facebook fits</h2><p>Facebook did nothing for our water damage jobs, but it did work for mold. Mold inspection leads cost us $57.80 each there. People with a musty basement are not in a rush, and an ad can reach them before they search. {b.link(R + 'insights/facebook-ads-for-restoration-companies/', 'All our Facebook numbers')}</p>
<h2>Mold travels better than water</h2><p>A water job needs a truck there within the hour. A mold job can be booked for Thursday. So you can advertise mold across a wider area than emergency work without breaking a promise about response time.</p>'''


def a_facebook(b):
 return f'''<p class="answer">We have spent about $18,000 on Facebook ads for our own restoration company, across 11 campaigns. The short version: Facebook does not sell water damage, it does sell planned services such as mold inspections and cleaning, and two popular tactics made our results worse.</p>
<h2>The numbers</h2>{table('Facebook results in our own restoration company', ['What we advertised', 'Result'], [
 ('Water damage, two campaigns, $1,412', 'Zero form leads. 13 calls placed, 2 confirmed.'),
 ('Carpet cleaning', '$41.06 a lead'),
 ('Duct cleaning', '$48.82 a lead'),
 ('Mold inspections', '$57.80 a lead'),
 ('Carpet cleaning, tight local targeting', '$127.50 a lead'),
 ('Duct cleaning, tight local targeting', '$140.62 a lead'),
 ('Giveaways', '$2.13 to $6.24 an entry'),
])}<p class="scope-note">From our own ad account, read August 2026. One company in small Midwest markets. Your results will differ.</p>
<h2>Why water damage failed</h2><p>Nobody scrolling Facebook has a burst pipe at that moment, and the person who does is not on Facebook. They are on Google with a phone in a wet hand. An emergency service has to be where the emergency search happens: Local Services Ads, search ads and the map. {b.link(R + 'water-damage-leads/', 'How we get water damage calls instead')}</p>
<h2>Why planned services worked</h2><p>Carpet cleaning, duct cleaning and mold inspections are things people have been meaning to do. An ad reminds them. They can fill in a form and book for next week. That is what Facebook is good at.</p>
<h2>Two tactics that backfired</h2><h3>Narrowing the area</h3><p>It feels sensible to show ads only to a tight circle around your town. On Facebook it roughly tripled our cost per lead. The audience got so small that Facebook charged more to reach it. Narrow targeting is right for Google search. On Facebook, give it room.</p><h3>Giveaways</h3><p>A giveaway produced "leads" at $2.13 to $6.24 each, which looks wonderful on a report. They were people entering a contest. Judge Facebook on booked jobs, never on cost per lead alone.</p>
<h2>What we would do with a restoration Facebook budget</h2><ul><li>Spend nothing on emergency water or fire.</li><li>Run mold inspection and cleaning offers with a simple form.</li><li>Keep the audience wide across your whole service area.</li><li>Use real photos of your own crew and trucks.</li><li>Count booked jobs each month, and stop what does not book.</li></ul>'''


ARTICLE_PAGES = {
 'restoration-company-marketing': ('Restoration Company Marketing: A Plain Guide | CDL', 'Restoration company marketing from a team that runs one: what to fix first, where water, fire and mold calls come from, and where the money gets wasted.', 'Restoration company marketing: a plain guide for owners.', a_guide, GUIDE_FAQ, ['seo', 'water-damage-leads'], ['how-to-get-water-damage-leads', 'mold-remediation-leads']),
 'how-to-get-water-damage-leads': ('How to Get Water Damage Leads Without Buying Them | CDL', 'Six sources of water damage restoration leads you own, real Google click prices, and seven questions to ask before buying leads from a seller.', 'How to get water damage leads without buying shared ones.', a_leads, LEADGUIDE_FAQ, ['water-damage-leads', 'seo'], ['restoration-company-marketing', 'facebook-ads-for-restoration-companies']),
 'mold-remediation-leads': ('Mold Remediation Leads: Marketing a Planned Job | CDL', 'How to get mold remediation leads: real search numbers, why mold needs its own campaign and page, and where Facebook works when it fails for water.', 'Mold remediation leads: how to market a planned job.', a_mold, MOLD_FAQ, ['seo', 'water-damage-leads'], ['facebook-ads-for-restoration-companies', 'restoration-company-marketing']),
 'facebook-ads-for-restoration-companies': ('Facebook Ads for Restoration Companies: Real Numbers', 'We spent $1,412 on Facebook water damage ads and got zero form leads. What worked instead, with real cost per lead from our own restoration company.', 'Facebook ads for restoration companies: what our own money taught us.', a_facebook, FB_FAQ, ['water-damage-leads'], ['mold-remediation-leads', 'restoration-company-marketing']),
}


def article_pages(b):
 pretty = b.date.fromisoformat(PUBLISHED).strftime('%B %-d, %Y')
 for slug, (title, desc, h1, fn, faq, rs, ra) in ARTICLE_PAGES.items():
  path = R + 'insights/' + slug + '/'
  url = b.DOMAIN + path
  faq_html = '<h2 id="questions">Common questions</h2>' + b.faqs(faq)
  body = b.subhero('Restoration insights', h1, 'Practical guidance from a team that runs a restoration company.', path, crumb=b.ESC(title.split(' | ')[0])) + f'<section class="section"><div class="wrap article-layout"><p class="article-meta">By <a href="/about/#caleb-foglesong">Caleb Foglesong</a> · Published {pretty}</p>{fn(b)}{faq_html}{aside_scope()}<aside><b>About the author</b><p>Caleb Foglesong runs CDL Marketing. {OWN}</p><a href="{R}#why">Why CDL</a></aside>{keep_reading(rs, ra)}<p><a href="{R}insights/">← All restoration insights</a></p></div></section>' + cta(b)
  schema = [{'@type': 'Article', 'headline': title.split(' | ')[0], 'description': desc, 'datePublished': PUBLISHED, 'dateModified': PUBLISHED, 'author': {'@type': 'Person', 'name': 'Caleb Foglesong', '@id': b.DOMAIN + '/about/#caleb-foglesong', 'url': b.DOMAIN + '/about/'}, 'publisher': {'@id': b.DOMAIN + '/#organization'}, 'mainEntityOfPage': {'@id': url + '#page'}, 'image': b.OG_IMAGE, 'about': 'Marketing for restoration companies'}, b.faq_schema(faq)]
  b.write(path, title, desc, body, schema, section='restoration')
 cards = ''.join(f'<article class="service-card"><span class="article-type">{a[1]}</span><h2>{a[2]}</h2><p>{a[3]}</p>{b.link(R + "insights/" + a[0] + "/", "Read it")}</article>' for a in ARTICLES)
 b.write(R + 'insights/', 'Restoration Marketing Insights | CDL Marketing', 'Plain guides to restoration company marketing, water damage leads, mold leads and Facebook ads, from a team that runs its own restoration company.', b.subhero('Insights', 'Restoration marketing insights<br>from the job.', 'Straight answers for owners of water, fire and mold companies, with real numbers from our own.', R + 'insights/') + '<section class="section"><div class="wrap cards two-cards">' + cards + '</div></section>' + cta(b), section='restoration')


# ---------------------------------------------------------------- contact

def contact(b):
 path = R + 'contact/'
 body = b.subhero('Free marketing audit', 'A free look at your<br>restoration marketing.', 'We check your Google listing, your website on a phone and your ads, then send three things to fix. No obligation.', path) + f'<section class="section"><div class="wrap contact-grid"><div class="contact-intro"><span class="eyebrow">What you get</span><h2>Three priorities.<br>In plain words.</h2><p>Tell us your company and your town. We look at what a homeowner sees when they search for water, fire or mold help near you, and send back three things worth fixing first.</p><ol><li>Where you show on Google and the map.</li><li>How your website loads and reads on a phone.</li><li>Where your ads, if you run any, are leaking money.</li></ol><p>The audit is free and you do not have to hire us. We work with independent restoration companies, month to month.</p><div class="contact-links"><a href="tel:+12172171705">(217) 217-1705</a><a href="mailto:caleb@cdl1.net">caleb@cdl1.net</a></div></div>{b.form("audit", who="restoration")}</div></section>'
 b.write(path, 'Free Restoration Marketing Audit | CDL Marketing', 'Request a free marketing audit for your restoration company: Google listing, website and ads. Call (217) 217-1705 or send the short form.', body, section='restoration')


def build_restoration(b):
 hub(b); service_pages(b); article_pages(b); contact(b)
