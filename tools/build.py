#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the complete static CDL Marketing site. No network access or deployment."""
from pathlib import Path
import re, json, html, xml.etree.ElementTree as ET
from datetime import date
from buyer_content import comparison_body, agency_guide_body
from privacy_policy import privacy_content
from switch_readiness import READINESS_PATH, readiness_body
from retailer_resources import CHECKLIST_PATH, REVIEW_PATH, checklist_body, first_review_body, resource_links
from website_offer import PLAN_NOTICE, PRICE, PRICE_HTML, SUMMARY, EXIT_SUMMARY, SEPARATE, PRICE_DESCRIPTION, PLAN_FAQ, PLAN_FAQS, pricing_content
from transition_offer import MARKETING_HEADLINE, MARKETING_SUMMARY, MARKETING_FAQ, REQUEST_NOTICE, marketing_scope_note, transition_preview, switching_contact_note, switch_page_body
from proof_content import WORK_PATH, WORK_TITLE, WORK_DESCRIPTION, work_samples_body, work_preview
from service_examples import SERVICE_EXAMPLES

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / 'source/legacy'
DOMAIN = 'https://cdlmanagement.com'
PAGES = []
LASTMOD = {}
BUILD_DATE = date.today().isoformat()
ESC = html.escape
SERVICES = [
 ('websites','Showroom websites','A useful first visit.','Fast, clear websites that help homeowners understand your showroom and ask for help.','web'),
 ('local-seo','Local SEO','Be found nearby.','Accurate listings, useful local pages and a Google Business Profile that reflects your store.','pin'),
 ('paid-ads','Paid ads','Reach people planning a floor.','Google and Meta campaigns connected to the right offer, page and next step.','cursor'),
 ('ai-search','AI search visibility','Make your facts easy to find.','Helpful answers and clear business information for search engines and AI-powered discovery.','layers'),
]
PATHS = {'pin':'<path d="M12 22s8-7 8-13a8 8 0 1 0-16 0c0 6 8 13 8 13Z"/><circle cx="12" cy="9" r="2.5"/>','cursor':'<path d="m8 6 3 15 3-6 6-3-12-6Z M3 3l2 2 M10 1v3 M1 10h3 M16 3l-2 2"/>','layers':'<path d="m12 2 10 6-10 6L2 8 12 2Zm-10 11 10 6 10-6M2 18l10 6 10-6"/>','web':'<rect x="2" y="3" width="20" height="18" rx="2"/><path d="M2 8h20M6 5.5h1M9 5.5h1M7 12h10M7 16h6"/>'}

def icon(name):
 return '<span class="service-icon"><svg viewBox="0 0 24 26" aria-hidden="true">'+PATHS[name]+'</svg></span>'

def link(path,label,cls='text-link'):
 return f'<a class="{cls}" href="{path}">{label} <span aria-hidden="true">→</span></a>'

def header():
 nav=''.join(f'<a href="/services/{s[0]}/">{s[1]}</a>' for s in SERVICES)+'<a href="/switch/">Switching providers</a>'
 return f'''<a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="/"><b>CDL</b>Marketing<small>Marketing for flooring showrooms</small></a><nav class="desktop-nav" aria-label="Main navigation"><details class="nav-services"><summary>Services</summary><div class="nav-popover">{nav}</div></details><a href="/about/">Why CDL</a><a href="/pricing/">Pricing</a><a href="/work-samples/">Work samples</a><a href="/contact/" class="btn">Free audit <span aria-hidden="true">↗</span></a></nav></div><details class="mobile-disclosure"><summary class="menu-toggle" aria-controls="mobile-menu">Menu <span aria-hidden="true">☰</span></summary><nav id="mobile-menu" class="mobile-nav" aria-label="Mobile navigation"><a href="/services/">All services</a>{nav}<a href="/about/">Why CDL</a><a href="/pricing/">Pricing</a><a href="/work-samples/">Work samples</a><a href="/guides/choosing-a-flooring-marketing-agency/">Buyer guides</a><a href="/blog/">Showroom insights</a><a href="/contact/">Free audit</a></nav></details></header>'''

def footer():
 return '''<footer class="site-footer"><div class="wrap"><div class="footer-top"><div><a class="brand" href="/"><b>CDL</b>Marketing</a><p>Marketing for flooring showrooms.<br>From people who run showrooms, too.</p><a href="tel:+12172171705">(217) 217-1705</a><br><a href="mailto:caleb@cdl1.net">caleb@cdl1.net</a></div><nav class="footer-links" aria-label="Service links"><b>What we do</b><a href="/services/websites/">Showroom websites</a><a href="/services/local-seo/">Local SEO</a><a href="/services/paid-ads/">Google &amp; Meta ads</a><a href="/services/ai-search/">AI search visibility</a></nav><nav class="footer-links" aria-label="Company links"><b>Get to know us</b><a href="/work-samples/">Work samples</a><a href="/about/">Why CDL</a><a href="/pricing/">Pricing &amp; scope</a><a href="/switch/">Switching providers</a><a href="/guides/choosing-a-flooring-marketing-agency/">Choosing an agency</a><a href="/guides/flooring-marketing-checklist/">Marketing checklist</a><a href="/guides/your-first-marketing-review/">Your first review</a><a href="/compare/broadlume/">CDL &amp; Broadlume</a><a href="/blog/">Showroom insights</a><a href="/free-mockup/">Free homepage design</a><a href="/contact/">Contact us</a><a href="/privacy/">Privacy policy</a></nav></div><details id="privacy-choices" class="privacy-choices"><summary>Privacy choices</summary><p data-privacy-status role="status" aria-live="polite">Advertising measurement is off unless you allow it. Forms work either way.</p><div class="privacy-actions"><button type="button" class="privacy-choice" data-privacy-choice="allow" disabled>Allow advertising measurement</button><button type="button" class="privacy-choice" data-privacy-choice="decline" disabled>Decline advertising measurement</button><button type="button" class="privacy-choice" data-privacy-reload hidden>Reload to apply fully</button></div></details><div class="footer-bottom"><span>© 2026 CDL Management · CDL Marketing · Kirksville, Missouri</span><span>Showroom experience. Clear answers.</span></div></div></footer>'''

ORG = {'@type':'Organization','@id':DOMAIN+'/#organization','name':'CDL Marketing','alternateName':['CDL Management'],'url':DOMAIN+'/','logo':DOMAIN+'/assets/favicon.svg','image':DOMAIN+'/assets/og-marketing-20261105.jpg','telephone':'+1-217-217-1705','email':'caleb@cdl1.net','address':{'@type':'PostalAddress','addressLocality':'Kirksville','addressRegion':'MO','postalCode':'63501','addressCountry':'US'},'areaServed':'US','founder':{'@id':DOMAIN+'/about/#caleb-foglesong'},'knowsAbout':['Flooring store marketing','Local SEO for flooring stores','Flooring website design','Google Ads for flooring stores','AI search visibility for flooring stores'],'description':'CDL Marketing is a marketing agency for independent flooring stores in the United States: websites, local SEO, Google and Facebook advertising and AI search visibility.','disambiguatingDescription':"A flooring store marketing agency in Kirksville, Missouri. Not connected with commercial driver's license (CDL) training, trucking or driver recruitment companies.",'contactPoint':{'@type':'ContactPoint','contactType':'sales','telephone':'+1-217-217-1705','email':'caleb@cdl1.net','areaServed':'US','availableLanguage':'English'}}
OG_IMAGE = DOMAIN+'/assets/og-marketing-20261105.jpg'
PAGE_META = {}

def crumb_parent(path):
 # Second breadcrumb level for article and service detail pages; None for every other page.
 if path.startswith('/blog/') and path!='/blog/':return ('Insights','/blog/')
 if path.startswith('/services/') and path!='/services/':return ('Services','/services/')
 return None

def plain(text):
 return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',text))).strip()

def faq_schema(items):
 return {'@type':'FAQPage','mainEntity':[{'@type':'Question','name':plain(q),'acceptedAnswer':{'@type':'Answer','text':plain(a)}} for q,a in items]}

def write(path,title,description,body,schema=None,extra_scripts=()):
 url=DOMAIN+path
 data=[ORG,{'@type':'WebSite','@id':DOMAIN+'/#website','name':'CDL Marketing','url':DOMAIN+'/'}, {'@type':'WebPage','@id':url+'#page','url':url,'name':title,'description':description,'isPartOf':{'@id':DOMAIN+'/#website'},'about':{'@id':DOMAIN+'/#organization'}}]
 if schema: data.extend(schema)
 if path != '/':
  name=re.sub('<[^>]+>','',title.split(' | ')[0])
  crumbs=[('Home',DOMAIN+'/')]
  parent=crumb_parent(path)
  if parent:crumbs.append((parent[0],DOMAIN+parent[1]))
  crumbs.append((name,url))
  data.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i,'name':n,'item':u} for i,(n,u) in enumerate(crumbs,1)]})
 schema_json=json.dumps({'@context':'https://schema.org','@graph':data},ensure_ascii=False).replace('</','<\\/')
 out=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{ESC(title)}</title><meta name="description" content="{ESC(description,quote=True)}"><link rel="canonical" href="{url}"><meta name="theme-color" content="#f7f3ec"><meta property="og:type" content="website"><meta property="og:site_name" content="CDL Marketing"><meta property="og:title" content="{ESC(title,quote=True)}"><meta property="og:description" content="{ESC(description,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{OG_IMAGE}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{ESC(title,quote=True)}"><meta name="twitter:description" content="{ESC(description,quote=True)}"><meta name="twitter:image" content="{OG_IMAGE}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css"><script type="application/ld+json">{schema_json}</script><script src="/assets/site.js" defer></script><script src="/assets/track.js" defer></script></head><body>{header()}<main id="main" tabindex="-1">{body}</main>{footer()}</body></html>'''
 if extra_scripts:
  out=out.replace('</head>',''.join(f'<script src="{ESC(src,quote=True)}" defer></script>' for src in extra_scripts)+'</head>')
 article_schema=next((item for item in data if item.get('@type')=='Article'),None)
 if article_schema and article_schema.get('dateModified'):LASTMOD[path]=str(article_schema['dateModified'])[:10]
 if article_schema:
  out=out.replace('property="og:type" content="website"','property="og:type" content="article"')
  dates=''.join(f'<meta property="article:{prop}_time" content="{ESC(str(article_schema[key]),quote=True)}">' for key,prop in [('datePublished','published'),('dateModified','modified')] if article_schema.get(key))
  out=out.replace('</head>',dates+'</head>')
 out=out.replace('—',', ').replace(' – ',' to ')
 out='\n'.join(line.rstrip() for line in out.splitlines())+'\n'
 dest=ROOT/path.strip('/')/'index.html' if path!='/' else ROOT/'index.html'
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(out)
 PAGES.append(path)
 PAGE_META[path]=(title,description)

def subhero(label,title,description,path,crumb=None):
 parent=crumb_parent(path)
 trail=f'<a href="{parent[1]}">{parent[0]}</a><span aria-hidden="true">/</span>' if parent else ''
 return f'<section class="sub-hero"><div class="wrap"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span>{trail}<span>{crumb or label}</span></nav><span class="eyebrow">{label}</span><h1>{title}</h1><p>{description}</p></div></section>'

def cta():
 return '<section class="cta-band"><div class="wrap"><div><h2>Let’s look at your showroom.</h2><p>Start with a free growth audit. No pressure. No obligation.</p></div>'+link('/contact/','Get my growth audit','btn')+'</div></section>'

def faqs(items):
 return '<div class="faq-list">'+''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in items)+'</div>'

FAQ=[
 ('What does a flooring marketing agency do?','A flooring marketing agency helps flooring stores and flooring companies get found and get more estimate requests: SEO, your Google Business Profile, your website, Google and Facebook ads and, now, AI search. All of these need to line up, and they have to be tuned all the time. CDL Marketing does that work for flooring stores, and we run our own flooring showrooms too.'),
 ('Who is CDL Marketing a good fit for?','Independent flooring showroom owners who want practical help with their website, local visibility or advertising. We first check your goals, market, current tools and access before recommending a scope.'),
 ('What do you offer?','Showroom websites, local SEO, Google and Meta advertising, and AI search visibility. We agree on the work you need rather than assuming every store needs every service. <a href="/services/">Explore the services.</a>'),
 ('How is CDL different from a general agency?','Our flooring-industry experience includes product questions, estimates and the work behind a sold job. <a href="/about/">See our operating background.</a>'),
 ('How long does flooring marketing take?','Timing depends on your market, starting point, access and agreed work. Ads can reach buyers while a campaign runs; organic visibility needs sustained work. The first 90 days are a planning and review period, not a promised sales result.'),
 ('Do I need a new website?','No. A new CDL website is not required. We can do SEO or advertising around your existing site when access and inquiry paths support the work. We assess those first, and we will point out free fixes on your current site whether or not you hire us.'),
 MARKETING_FAQ,
 PLAN_FAQ,
 ('How do flooring stores show up in ChatGPT and AI search?','AI tools pull from your website, your Google Business Profile, your reviews and other sites that mention you. Clear, consistent store facts and direct answers to real buyer questions make you easier to find and quote. <a href="/services/ai-search/">See our AI search work.</a>'),
 ('Can you guarantee rankings, AI mentions or leads?','No. We do not promise a search position, AI recommendation, lead count or sales result. We agree on deliverables and review the evidence, including gaps in tracking.'),
 ('What will I receive in the free audit?','A review of your website and local online presence, with three priority opportunities to discuss. It is a practical starting point, with no obligation to hire us.'),
]

def form(kind='audit'):
 audit=kind=='audit'
 extra='''<div class="fields-row"><div class="field"><label for="revenue">Approximate monthly revenue (optional)</label><select id="revenue" name="revenue"><option value="">Choose a range</option><option>Under $50k / mo</option><option>$50k to $100k / mo</option><option>$100k to $250k / mo</option><option>$250k+ / mo</option></select></div><div class="field"><label for="goal">Biggest goal (optional)</label><select id="goal" name="goal"><option value="">Choose a goal</option><option>More local customers / leads</option><option>Rank higher on Google</option><option>A clearer website and inquiry path</option><option>Run better ads</option><option>All of the above</option><option>Switch providers: website only</option><option>Switch providers: SEO and advertising</option></select></div></div>''' if audit else '''<div class="field"><label for="vertical">Business type</label><select id="vertical" name="vertical" required><option value="">Choose one</option><option value="Flooring">Flooring store</option><option value="Restoration">Restoration company</option><option value="Assisted Living">Assisted living</option><option value="Fitness">Fitness center / gym</option><option value="Massage">Massage therapy</option><option>Other</option></select></div>'''
 city='<div class="field"><label for="city">City and state</label><input id="city" name="city" autocomplete="address-level2" required maxlength="160"></div>' if audit else ''
 request_note='<p class="form-fine">'+REQUEST_NOTICE+'</p>' if audit else ''
 return f'''<form class="lead-form" method="post" id="{'applyForm' if audit else 'leadForm'}" data-lead-form="{kind}"><fieldset class="form-fields" aria-labelledby="form-heading"><h3 id="form-heading">{'Tell us about your showroom' if audit else 'Request your free homepage concept'}</h3><p class="muted">{'Required: your name, showroom, city and state, and email.' if audit else 'Required: business name, your name, email and business type.'}</p><div class="field"><label for="name">Your name</label><input id="name" name="name" autocomplete="name" required maxlength="160"></div><div class="field"><label for="showroom">{'Showroom' if audit else 'Business'} name</label><input id="showroom" name="showroom" autocomplete="organization" required maxlength="200"></div>{city}<div class="fields-row"><div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required maxlength="254"></div><div class="field"><label for="phone">Phone (optional)</label><input id="phone" name="phone" type="tel" autocomplete="tel" maxlength="40"></div></div><div class="field"><label for="website">Current website (optional)</label><input id="website" name="website" inputmode="url" autocomplete="url" maxlength="500" placeholder="yourshowroom.com"></div>{extra}<div class="hp" aria-hidden="true"><label for="company_website_hp">Leave this field blank</label><input id="company_website_hp" name="company_website_hp" tabindex="-1" autocomplete="off"></div><button class="btn" type="submit" disabled>{'Request my free growth audit' if audit else 'Request my free concept'} <span aria-hidden="true">→</span></button><p class="form-fine">By sending, you ask us to contact you about your request. <a href="/privacy/">Privacy policy</a>.</p>{request_note}<p class="form-fine form-fallback">If this form is unavailable, <a href="tel:+12172171705">call (217) 217-1705</a> or <a href="mailto:caleb@cdl1.net">email caleb@cdl1.net</a>.</p></fieldset><div class="form-message" role="status" aria-live="polite" aria-atomic="true"></div></form>'''

def portrait():
 return '<img class="portrait showroom-portrait" src="/assets/caleb-showroom.webp" srcset="/assets/caleb-showroom-400.webp 400w, /assets/caleb-showroom.webp 800w" sizes="(max-width: 600px) calc(100vw - 82px), (max-width: 820px) 340px, 460px" width="800" height="1000" fetchpriority="high" alt="Caleb Foglesong standing in a flooring showroom, illustrative portrait"><div class="portrait-caption"><b>Caleb Foglesong</b>CDL Marketing</div>'

def service_choices():
 return f'''<div class="cards buying-choices">
 <article class="service-card"><span class="article-type">01 · Make the first visit count</span><h3>A better showroom website.</h3><p>Help shoppers see what you sell, where you work and how to request an estimate.</p><p class="choice-price"><b>{PRICE}</b><br>Proposed website-only plan. Hosting and care included; campaigns quoted separately.</p>{link('/services/websites/','See the website scope')}</article>
 <article class="service-card"><span class="article-type">02 · Get found in your market</span><h3>Local search that reflects your store.</h3><p>Accurate business listings and useful product, installation and service-area pages based on what you actually offer.</p><p class="choice-price"><b>Local SEO: custom scope and quote.</b><br>We can assess your current website first.</p>{link('/services/local-seo/','Explore local SEO')}</article>
 <article class="service-card"><span class="article-type">03 · Reach shoppers with a plan</span><h3>Ads with a useful next step.</h3><p>Google and Meta campaigns connected to the right flooring offer, page and inquiry path.</p><p class="choice-price"><b>Ad management: custom scope and quote.</b><br>Advertising spend is paid separately.</p>{link('/services/paid-ads/','Explore paid advertising')}</article>
 </div><p class="inline-note search-note"><b>Thinking about AI search?</b> Clear store facts and helpful answers support search discovery. <a href="/services/ai-search/">Explore our separately scoped AI search work</a>.</p>'''

def home():
 body=f'''<section class="hero" id="top"><div class="wrap hero-grid"><div class="hero-copy"><span class="eyebrow">{MARKETING_HEADLINE}</span><h1>Marketing for flooring stores.<br><span>Built for the next sale.</span></h1><p class="intro">CDL Marketing is a flooring marketing agency run by people who own flooring showrooms. Flooring SEO, websites, Google and Facebook ads and AI search that help homeowners find your store and ask for an estimate. Month-to-month.</p><div class="hero-actions">{link('/contact/','Get my free growth audit','btn')}{link(WORK_PATH,'See how we work')}</div><p class="hero-note">Your website + local presence. Three priorities to discuss.<br>Free, with no obligation.</p><p class="hero-note">Spoken with our team? <a href="/contact/#after-call">Pick up the conversation.</a></p></div><div class="hero-art">{portrait()}</div></div></section><div class="trust-strip"><div class="wrap trust-inner"><span>Built on flooring-industry experience</span><span>Websites</span><span>Local search</span><span>Advertising</span></div></div>
 <section class="section" id="services"><div class="wrap"><div class="section-heading"><span class="eyebrow">Choose the work your store needs</span><h2>One clear starting point.<br>Room to grow from there.</h2><p>CDL Marketing helps independent flooring showrooms with websites, local search, advertising and AI search visibility. Start with a specific problem. Each service has its own scope and costs.</p></div>{service_choices()}<p class="inline-note">You can keep a useful existing website. We check access, compatibility and inquiry paths before recommending a rebuild.</p></div></section>
 {work_preview()}
 <section class="section light" id="approach"><div class="wrap split"><div><span class="eyebrow">Our approach is different</span><h2>No long contract.<br>Just the work.</h2><p>For too long, flooring stores have signed marketing contracts that promised a lot and never delivered. Our approach is different. If we don’t do what we say, you can let us go and move on. No waiting for a contract to end. We fight every day to keep our clients.</p><p>We’ve seen stores pay for a 12-month SEO contract and get 12 edits in 12 months. That isn’t SEO. Search, your Google listing, your website and your ads all need to line up, and they have to be tuned all the time.</p></div><div class="quote-panel"><span class="eyebrow">Think about your best installer</span><h3>The little things.<br>Every time.</h3><p>A good installer does the floor prep, patches, uses the right adhesive, vacuums and talks to the customer. That’s how they get five-star reviews. Marketing works the same way. Google changes every couple of weeks, so we check the work a few days later, not a year later, and adjust.</p><p>Your installer is the last thing a customer sees. We take care of the first: Google, Maps and what ChatGPT recommends. Nothing magical. We’re just doing the work.</p></div></div></section>
 <section class="section" id="edge"><div class="wrap split"><div id="own-stores"><span class="eyebrow">We’re in the flooring business, too</span><h2>From a product question<br>to a measure appointment.</h2><p class="muted">A flooring inquiry is the start of a real project. The shopper may need help comparing materials, understanding installation or arranging a measure. Our team operates flooring showrooms and handles marketing for our own businesses, so those decisions shape the pages and campaigns we plan.</p>{link('/about/','Meet the team behind CDL')}</div><div class="quote-panel"><span class="eyebrow">Why choose CDL?</span><h3>Flooring context.<br>A clear scope.<br>Work you can review.</h3><ul class="reason-list"><li><b>Start where the problem is.</b> Discuss a website, search or advertising scope that fits your store.</li><li><b>Keep the costs clear.</b> Separate website service, marketing fees and ad spend.</li><li><b>Stay flexible.</b> Month-to-month marketing, with scope, fees and notice in writing.</li><li><b>Ask for the evidence.</b> Review actual work, relevant inquiries and the limits of the data.</li></ul>{link('/compare/broadlume/','Compare CDL and Broadlume')}</div></div></section>
 <section class="section light"><div class="wrap"><div class="section-heading"><span class="eyebrow">From first conversation to ongoing work</span><h2>Know the next step.<br>Know what you are buying.</h2><p>We agree the scope, access and milestones before paid work begins. The first 90 days give the work a review plan.</p></div><div class="process"><article><span class="step-number">01</span><h3>Find the priority.</h3><p>Start with a free review of your website and public local presence. Discuss three priorities and what needs a closer look.</p></article><article><span class="step-number">02</span><h3>Agree the work.</h3><p>Review a written scope with deliverables, separate costs, access needs and responsibilities. Approve the plan before it starts.</p></article><article><span class="step-number">03</span><h3>See what changed.</h3><p>Review completed work and inquiry quality where records are available. Choose the next improvement from the evidence.</p></article></div><p class="inline-note">{link('/guides/your-first-marketing-review/','What to expect from your first review')}</p></div></section>
 <section class="section dark-section" id="pricing"><div class="wrap price-teaser"><div><span class="eyebrow">Proposed standalone website plan</span><h2>Your website.<br>One defined scope.</h2><div class="price-amount">{PRICE_HTML}</div><p class="scope-note">{SUMMARY}</p><p class="scope-note">Proposed terms: month-to-month after launch, 30 days’ notice and a portable website handover after setup is paid. Your domain and accounts stay yours. Confirm the final terms in writing.</p>{link('/pricing/','See the full website scope and terms')}</div><div class="price-summary" id="guarantee"><span class="eyebrow">Marketing is a separate choice</span><h3>Local SEO. Paid ads.<br>AI search visibility.</h3><p>Agree the services you need and their fees. Media spend is separate from ad management.</p><p>Review the work and the results that can be verified. Search positions, AI mentions, inquiry counts and sales are not guaranteed.</p>{link('/services/','Compare the services')}</div></div></section>
 <section class="section light"><div class="wrap split"><div><span class="eyebrow">Already with another provider?</span><h2>A careful move.<br>A clear agreement.</h2><p>We review your current agreement, useful pages, accounts and inquiry paths before planning a change. Bring the facts about your own provider.</p>{link('/guides/switching-flooring-website-providers/','Use the switching checklist')}</div><div class="callout"><h3>Explore proposed switching support</h3><p>We are reviewing monthly website-service credits for eligible transitions. Eligibility, paid marketing, setup treatment, credit limits and timing need written approval. An inquiry does not activate a credit or cancel your existing agreement.</p>{link('/switch/','Compare the proposed switching paths')}</div></div></section>
 <section class="section"><div class="wrap faq-layout"><div class="section-heading"><span class="eyebrow">Straight answers</span><h2>Before you<br>choose an agency.</h2><p>How we work, what it costs and what to expect.</p>{link('/contact/','Ask us something else')}</div>{faqs(FAQ)}</div></section>
 <section class="section light"><div class="wrap"><div class="section-heading"><span class="eyebrow">Notes from the showroom</span><h2>Useful answers.<br>No marketing lecture.</h2></div>{articles_cards()}<p class="inline-note">{link('/blog/','Read all showroom insights')}</p></div></section>
 <section class="section" id="apply"><div class="wrap contact-grid"><div class="contact-intro"><span class="eyebrow">Your free growth audit</span><h2>Three priorities.<br>A useful starting point.</h2><p>We review your website and local online presence, then identify three priority opportunities to discuss. The audit is free, with no obligation to hire us.</p><p>{link(WORK_PATH+'#audit','See an example of the review')}</p><div class="contact-links"><a href="tel:+12172171705">(217) 217-1705</a><a href="mailto:caleb@cdl1.net">caleb@cdl1.net</a></div><p class="inline-note">Prefer to start with a design? <a href="/free-mockup/">Request a free homepage mockup.</a></p></div>{form()}</div></section>'''
 write('/','Marketing for Flooring Stores | Flooring Marketing Agency | CDL','Marketing for flooring stores from a team that runs flooring showrooms: websites, local SEO, Google and Facebook ads and AI search. Month to month.',body,[faq_schema(FAQ)])

ARTICLE_INFO=[('flooring-store-website-speed-study','Original research','We tested 831 flooring store websites on a phone','Only 1 in 10 scored in Google\'s good range. What the numbers show and what to fix first.'),('marketing-for-flooring-stores','Showroom growth','Flooring store marketing: a practical guide','What to fix first, what to spend on and how to judge it by sold jobs.'),('broadlume-alternatives','Buyer guide','Broadlume alternatives for independent flooring stores','The real options, how each provider describes itself and what to check before you switch.'),('local-seo-for-flooring-stores','Local search','Local SEO for flooring stores: a practical checklist','Start with your Business Profile, consistent information and useful local pages.'),('flooring-store-chatgpt-ai-search','AI search','How flooring stores can show up in AI search','Clear business details and helpful answers give search services usable information.'),('google-business-profile-for-flooring-stores','Google Business Profile','A practical Business Profile checklist','Give homeowners accurate hours, a useful description and the right next step.')]

ARTICLE_INFO += [('flooring-store-call-tracking','Call tracking','How a flooring store should track phone calls','Connect inquiries to their source and understand the limits of your call reports.'),('flooring-store-website-checklist','Website checklist','What a flooring store website should have','Check the pages, contact paths and business details shoppers need.'),('google-ads-for-flooring-stores','Google Ads','Google Ads for flooring stores','Count real leads, block searches that never buy and judge campaigns by sold jobs.')]

# Article to service page links shown at the end of each article body.
ARTICLE_SERVICE={
 'local-seo-for-flooring-stores':('/services/local-seo/','flooring store SEO service'),
 'google-business-profile-for-flooring-stores':('/services/local-seo/','flooring store SEO service'),
 'google-ads-for-flooring-stores':('/services/paid-ads/','Google Ads management for flooring stores'),
 'flooring-store-call-tracking':('/services/paid-ads/','Google Ads management for flooring stores'),
 'flooring-store-website-checklist':('/services/websites/','flooring website design service'),
 'flooring-store-website-speed-study':('/services/websites/','flooring website design service'),
 'flooring-store-chatgpt-ai-search':('/services/ai-search/','AI search work for flooring stores'),
 'marketing-for-flooring-stores':('/','marketing for flooring stores'),
 'broadlume-alternatives':('/switch/','switching plan for flooring stores'),
}
# Specific link text for article cards; other cards keep the generic label.
CARD_LINK_TEXT={'marketing-for-flooring-stores':'Flooring store marketing guide','flooring-store-website-speed-study':'Our test of 831 flooring store websites'}

_ARTICLE_SOURCES={}
def article_source(slug):
 # Parsed article source, or None when no complete source exists. A corrected file in source/articles/
 # wins; a missing or half-written one falls back to the legacy snapshot, then to None.
 if slug in _ARTICLE_SOURCES:return _ARTICLE_SOURCES[slug]
 found=None
 for f in [ROOT/'source/articles'/slug/'index.html',LEGACY/'blog'/slug/'index.html']:
  if not f.exists():continue
  try:
   old=f.read_text()
   parts=[re.search(r'<title>(.*?)</title>',old,re.S),re.search(r'<meta name="description" content="(.*?)"',old),re.search(r'<h1>(.*?)</h1>',old,re.S),re.search(r'<article>(.*?)</article>',old,re.S)]
   if not all(parts):raise ValueError('missing title, description, h1 or article')
   scripts=[json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',old,re.S)]
  except (ValueError,OSError,UnicodeDecodeError) as exc:
   print(f'Skipping incomplete article source {f.relative_to(ROOT)}: {exc}');continue
  found={'title':parts[0][1],'desc':parts[1][1],'h1':parts[2][1],'article':parts[3][1],'scripts':scripts}
  break
 _ARTICLE_SOURCES[slug]=found
 return found

def available_articles():
 return [x for x in ARTICLE_INFO if article_source(x[0])]

def article_title(slug):
 return next(x[2] for x in ARTICLE_INFO if x[0]==slug)

def articles_cards(all_posts=False):
 items=available_articles()
 return '<div class="article-grid">'+''.join(f'<article class="article-card"><p class="article-type">{tag}</p><h3><a href="/blog/{slug}/">{title}</a></h3><p>{desc}</p>{link("/blog/"+slug+"/",CARD_LINK_TEXT.get(slug,"Read the guide"))}</article>' for slug,tag,title,desc in (items if all_posts else items[:3]))+'</div>'

DETAIL={
 'websites': {
 'h1':'Flooring website design that helps shoppers take the next step.',
 'intro':f'Proposed standalone website plan for review: {PRICE}. A useful website for one showroom, with hosting, care and monthly updates.',
 'answer':'A flooring showroom website should quickly answer three questions: does this store have what I need, does it serve my area and how do I get help? We organize the agreed pages around those decisions.',
 'work':PLAN_NOTICE+' '+SUMMARY+' Proposed setup includes one brand direction, up to 5,000 words, 20 supplied images, two consolidated revision rounds and up to two pages formatting your supplied legal text. One standard inquiry form, search foundations, measurement setup and up to 20 agreed redirects are included. <a href="/pricing/#included">See the full build scope.</a>',
 'provide':'Your store details, product and installation facts, approved photography, brand requirements, website access and a person who can review the content. We assess co-op and provider restrictions first.',
 'review':'Under the proposed website plan, you review the design/content draft and the final version before launch. We check mobile/desktop pages, keyboard use, links, redirects and real inquiry delivery to the agreed destination, with your authorization. Monthly care includes availability monitoring, link/form checks, versioned backups, restoration and a short care summary.',
 'separate':f'Proposed standalone website plan: {PRICE}. '+SEPARATE+' New pages, redesigns, integrations and bulk imports need a separate scope. Extra work is $125/hour or a written fixed quote, approved before work begins. '+EXIT_SUMMARY,
 'related':['local-seo-for-flooring-stores','marketing-for-flooring-stores','flooring-store-website-checklist','flooring-store-website-speed-study']},
 'local-seo': {
 'h1':'Flooring store SEO that gets your showroom found nearby.',
 'intro':'Accurate business information and useful local pages for homeowners looking for flooring in your area.',
 'answer':'Flooring store SEO is the work that gets your showroom found when someone nearby searches for carpet, vinyl plank, hardwood, tile or installation. It connects an accurate Google Business Profile, a useful showroom website and consistent business information. We find the gaps in the area you really serve and agree on the work to close them.',
 'extra':[('What flooring store SEO includes','<ul><li><strong>Google Business Profile.</strong> The right category, the products and services you really sell, current photos, correct hours and replies to reviews.</li><li><strong>A page for each main product and service.</strong> Carpet, luxury vinyl plank, hardwood, tile and installation, written around the questions your salespeople hear.</li><li><strong>Your towns.</strong> The places you serve, named on the pages where it is true.</li><li><strong>Matching business details.</strong> The same name, address and phone number on your website, profile, Facebook and directories.</li><li><strong>Reviews.</strong> A simple, honest way to ask every customer, with no reward attached.</li><li><strong>The technical basics.</strong> A site that loads fast on a phone, clear page titles and store facts that search engines can read.</li></ul>'),('What we look at first','<p>We start with three checks before proposing any work.</p><ol><li><strong>Where you show up.</strong> We search for your main products from several points around your showroom, because your position on the map changes from one side of town to the other.</li><li><strong>Which products you are found for.</strong> Many stores show up for the words in their name and are far down for the products they most want to sell.</li><li><strong>How fast the site is on a phone.</strong> When <a href="/blog/flooring-store-website-speed-study/">we tested 831 independent flooring store websites</a>, only one in ten scored in the range Google calls good.</li></ol><p>You get those findings in plain words whether or not you hire us.</p>'),('How long flooring store SEO takes','<p>Some fixes show quickly, such as a corrected Business Profile. Others build over months. Google\'s own <a href="https://developers.google.com/search/docs/fundamentals/seo-starter-guide" rel="noopener">starter guide</a> says some changes take effect in a few hours and others can take several months. We do not promise a ranking. We agree the work, do it, and review it with you against calls, forms and sold jobs where those can be traced.</p>')],
 'work':'Review your Business Profile, categories, services, contact information and key listings. Plan useful service and location content around actual buyer questions, with technical checks and internal links.',
 'provide':'Access to the correct profiles and website, accurate hours and service areas, real product and installation details, approved images and content approval. We do not add services you do not offer.',
 'review':'Review completed changes and search visibility alongside relevant calls and forms where tracking is available. A ranking observation is not a sold job; incomplete attribution stays visible.',
 'separate':'Local SEO is custom quoted. Website changes beyond the agreed scope, paid advertising, media and optional third-party tools are identified separately in the proposal.',
 'related':['local-seo-for-flooring-stores','google-business-profile-for-flooring-stores']},
 'paid-ads': {
 'h1':'Google and Facebook ads for flooring stores, with a clear next step.',
 'intro':'Google and Meta campaigns connected to your products, your market and the right landing page.',
 'answer':'Google Ads for flooring stores work when the ad reaches someone nearby who is shopping for a floor now, sends them to a page about that product, and makes it easy to call or visit. Facebook and Instagram ads do a different job: they keep your store in front of local homeowners before they search. We plan targeting, copy, creative and review around the scope your showroom needs.',
 'extra':[('How Google Ads for flooring stores should be set up','<ul><li><strong>Campaigns by product.</strong> Carpet, vinyl plank, hardwood and installation are different searches and deserve their own ads and pages.</li><li><strong>Searches blocked on purpose.</strong> Jobs, do-it-yourself questions, free samples and brands you do not carry are kept out so the budget goes to buyers.</li><li><strong>A page that matches the ad.</strong> Someone who searched for hardwood lands on hardwood, not the home page.</li><li><strong>A phone number for the ads alone.</strong> So you can see which calls the ads caused.</li><li><strong>A plain definition of a lead.</strong> A real person asking about a real project. Wrong numbers and vendors do not count.</li></ul><p>What we check in our own accounts is in <a href="/blog/google-ads-for-flooring-stores/">Google Ads for flooring stores</a>, and the phone setup is in <a href="/blog/flooring-store-call-tracking/">how a flooring store should track phone calls</a>.</p>'),('Google Ads or Facebook ads: which does what','<div class="tbl fit"><table><tr><th></th><th>Google search ads</th><th>Facebook and Instagram ads</th></tr><tr><td>Who sees them</td><td>People searching for flooring now</td><td>Local homeowners before they search, and people who visited your site</td></tr><tr><td>Best for</td><td>Calls and visits this month</td><td>Staying known, and bringing visitors back</td></tr><tr><td>Judge by</td><td>Leads and sold jobs per dollar</td><td>Calls, visits and requests over a few months</td></tr></table></div>'),('What flooring advertising costs','<p>There are two separate costs. The advertising budget is paid by you directly to Google or Meta. Our management fee is quoted for your scope before you commit, and it is month to month.</p><p>We will not quote you a cost per lead before we have seen your market, because it depends on your town, your products and your competition. What we can give you is the way to judge it: decide what you can afford to spend to win one sold job, then compare each campaign to that figure every month. The method is in our <a href="/blog/marketing-for-flooring-stores/">flooring store marketing guide</a>.</p>')],
 'work':'Plan agreed Google or Meta campaigns, match offers to landing pages, review search terms or audience settings and adjust creative and targeting around the available lead-quality evidence.',
 'provide':'Ad-account access, an agreed media budget, accurate offers and availability, approved claims and imagery, landing-page access and staff input on inquiry quality. Your team handles customer conversations.',
 'review':'Review spend, inquiry quality and landing-page behavior. When source and sold-job data can be linked, include them with the reporting period and coverage; do not treat platform conversions as verified sales.',
 'separate':'Ad management is custom quoted. Media is paid separately to the platforms. Campaign scope, creative production, landing-page work and optional tools are defined before commitment.',
 'related':['marketing-for-flooring-stores','google-ads-for-flooring-stores','flooring-store-call-tracking']},
 'ai-search': {
 'h1':'AI search for flooring stores, built on useful showroom facts.',
 'intro':'Clear, reliable information for the questions homeowners ask search engines and AI tools.',
 'answer':'AI search visibility helps search tools find and understand accurate information about your showroom. Generative engine optimization (GEO) and answer engine optimization (AEO) overlap with SEO: useful answers about products, installation, estimates and service areas, supported by clear business facts. No agency controls whether a tool recommends your store.',
 'work':'Review buyer questions, strengthen direct answers on relevant pages, align public business details and use structured data that matches visible facts. Check a documented sample of questions and record the answers and sources.',
 'provide':'Verified store facts, product and service details, permission to edit relevant pages and listings, real photos and an approver. Claims need evidence before they appear in content.',
 'review':'Compare dated observations for the same questions and tools, recognizing that answers vary. Separate mentions, referrals, inquiries and sold jobs. A small sample is not market-wide visibility or proof that a change caused a result.',
 'separate':'AI search work is custom quoted. Website production, local SEO campaigns, paid media and optional monitoring tools are specified separately. Google says existing SEO best practices apply to its AI features; there is no special schema requirement.',
 'related':['flooring-store-chatgpt-ai-search','local-seo-for-flooring-stores']}
}

SERVICE_META = {
 'websites': ('Flooring Website Design for Flooring Stores | CDL Marketing','Flooring showroom website design with clear product pages, installation information and inquiry paths. Review the proposed build, monthly care and pricing.'),
 'local-seo': ('Flooring Store SEO | Local SEO for Flooring Stores | CDL','Flooring store SEO for independent showrooms: Google Business Profile, product and town pages, reviews and listings, reviewed against calls and sold jobs.'),
 'paid-ads': ('Google Ads for Flooring Stores & Facebook Ads | CDL','Google Ads for flooring stores, plus Facebook and Instagram, with matching landing pages and tracked calls. Management fee quoted, ad budget paid direct.'),
 'ai-search': ('AI Search & GEO for Flooring Stores: ChatGPT, Google AI | CDL','Practical SEO, AEO and GEO work for flooring showrooms: accurate store facts, useful answers and documented AI-search observations. See the process and scope.')
}

SERVICE_FAQ = {
 'websites': [
  ('What should a flooring store website have?','Clear product categories, your service area, real photos, installation information and an easy way to ask for an estimate or measure. It needs to load fast on a phone, because that is where most shoppers start.'),
  ('Can you fix my current website instead of building a new one?','Yes. A new CDL website is not required. We will point out free fixes on your current site whether or not you hire us. Most of them are pretty easy fixes for us.'),
  ('Do I own my website and domain?','Your domain and accounts stay yours. Under the proposed website plan, a portable website handover is included after setup is paid.')],
 'local-seo': [
  ('What is flooring SEO?','Flooring SEO is the work that helps homeowners find your store when they search for flooring, carpet, LVP, hardwood or installation near them. It covers your Google Business Profile, your website pages, your listings and your reviews. All of these need to line up, and they need to be tuned all the time.'),
  ('How long does SEO take for a flooring store?','Some fixes show up in weeks, like a corrected Business Profile or a page Google can finally read. Ranking for competitive searches takes steady monthly work. We check changes a few days after we make them, not a year later, and adjust.'),
  ('How is flooring store SEO different from general SEO?','It is local and it is about a showroom. The goal is to show up on the map and in nearby searches for the products you sell, and to make a visit or a call the easy next step. National rankings and blog traffic from other states do not sell floors.'),
  ('How much does flooring store SEO cost?','It is quoted for your store after we look at your website and local presence, and you get the scope and the price in writing before you commit. It is month to month.'),
  ('Do you do SEO for commercial flooring companies?','Our focus is primarily residential, but it is also commercial. Done right, local SEO brings in commercial jobs you have not even thought about.')],
 'paid-ads': [
  ('Should a flooring store run Google Ads or Facebook ads?','Usually Google for people already searching for flooring, and Facebook and Instagram to reach homeowners before they search. The right mix depends on your market, your budget and what you sell most.'),
  ('How much should a flooring store spend on Google Ads?','Enough to learn which searches produce real leads in your market, and no more than your numbers support. Decide what you can afford to spend to win one sold job, then grow the campaigns that stay under that figure and cut the ones that do not.'),
  ('Is ad spend included in the management fee?','No. Ad spend is paid directly to Google or Meta. Our management fee is separate and quoted for your scope.'),
  ('How do you know if flooring ads are working?','We track calls and form inquiries back to the campaign where we can, and review lead quality with your team. A platform conversion count is not the same as a sold job, and our reporting says so.')],
 'ai-search': [
  ('Can my flooring store show up in ChatGPT?','It can. ChatGPT, Google AI answers and similar tools pull from your website, your Google Business Profile, your reviews and other sites that mention you. We make those facts clear, consistent and easy to quote. No one controls whether a tool recommends a specific store.'),
  ('What is GEO?','Generative engine optimization (GEO) is SEO for AI answers. It overlaps with regular SEO: clear answers to real buyer questions, accurate business details and structured data that matches what is on the page.'),
  ('Is AI search separate from SEO?','Mostly no. Good SEO and AI search work use the same foundation. We add checks of the actual AI answers for your market, so you can see what is being said about your store.')],
}

# Services hub: link text and a two-sentence plain description per service.
HUB_TEXT={
 'websites':('Flooring website design','A showroom website lays out what you sell, where you install and how a shopper asks for an estimate. It suits stores whose current site is slow on a phone, hard to update or unclear about the next step.'),
 'local-seo':('Flooring store SEO','Local SEO is ongoing work on your Google Business Profile, listings, reviews and local pages so nearby shoppers find accurate facts about your store. It suits stores that serve a defined area and want to be easier to find when people search close to home.'),
 'paid-ads':('Google and Facebook ads for flooring stores','We plan and manage Google and Facebook campaigns that send shoppers to a page with a clear offer and an easy way to reach you. It suits stores that want to reach buyers while a campaign runs and can set a separate advertising budget.'),
 'ai-search':('AI search visibility for flooring stores','AI search work makes your store facts, product details and answers to common buyer questions clear and consistent in the places tools like ChatGPT and Google AI read. It suits stores that already have a working website and listings and want those facts easy to find and quote.'),
}

def services():
 for slug,label,headline,desc,_ in SERVICES:
  d=DETAIL[slug]
  items=[('What we work on',d['work']),('What your team provides',d['provide']),('How we review the work',d['review']),('What is quoted separately',d['separate'])]
  extra=''.join(f'<section id="more-{i}"><h2>{h}</h2>{body_html}</section>' for i,(h,body_html) in enumerate(d.get('extra',[]),1))
  sections=SERVICE_EXAMPLES[slug]+extra+''.join(f'<section id="part-{i}"><h2>{h}</h2><p>{p}</p></section>' for i,(h,p) in enumerate(items,1))
  related=''.join(f'<li><a href="/blog/{key}/">{article_title(key)}</a></li>' for key in d['related'] if article_source(key))
  source='<p>Source: <a href="https://developers.google.com/search/docs/appearance/ai-features">Google Search Central: AI features and your website</a>. Inclusion and presentation remain Google’s decisions.</p>' if slug=='ai-search' else ''
  body=subhero(label,d['h1'],d['intro'],'/services/'+slug+'/')+f'<section class="section"><div class="wrap article-layout"><p class="answer">{d["answer"]}</p><nav class="toc" aria-label="On this page"><b>On this page</b><a href="#service-example">A flooring example</a>'+''.join(f'<a href="#part-{i}">{h}</a>' for i,(h,p) in enumerate(items,1))+f'</nav>{sections}{source}<aside><b>Agree on the scope first</b><p>Proposed standalone website plan for review: {PRICE}. {SUMMARY} Marketing services and advertising spend are separate.</p><a href="/pricing/">See pricing and proposal details</a></aside><h2>See how the work is reviewed</h2><p><a href="/work-samples/#audit">Read a sample audit</a> and <a href="/work-samples/#report">see the monthly report format</a>. The examples help you compare the approach before agreeing a paid scope.</p><h2>Keep reading</h2><ul>{related}<li><a href="/guides/choosing-a-flooring-marketing-agency/">How to choose a flooring marketing agency</a></li></ul><p><a href="/services/">Explore all marketing services</a></p></div></section>'+cta()
  if slug == 'websites': body=body.removesuffix(cta())+'<section class="section light"><div class="wrap">'+transition_preview()+'</div></section>'+cta()
  else:
   website_aside=f'<aside><b>Agree on the scope first</b><p>Proposed standalone website plan for review: {PRICE}. {SUMMARY} Marketing services and advertising spend are separate.</p><a href="/pricing/">See pricing and proposal details</a></aside>'
   service_aside='<aside><b>Start with the service you need</b><p>A new CDL website is not required. We can use your existing site when its access, compatibility and inquiry paths support the agreed work. Any necessary changes are scoped first. This service has its own fee; advertising spend is separate.</p><a href="/pricing/">See pricing and scope</a></aside>'
   assert website_aside in body
   body=body.replace(website_aside,service_aside)
  faq_html='<section class="section light" id="questions"><div class="wrap faq-layout"><div class="section-heading"><span class="eyebrow">Common questions</span><h2>'+label+'<br>questions.</h2></div>'+faqs(SERVICE_FAQ[slug])+'</div></section>'
  assert body.endswith(cta())
  body=body.removesuffix(cta())+faq_html+cta()
  title,description = SERVICE_META[slug]
  write('/services/'+slug+'/',title,description,body,[{'@type':'Service','name':label+' for flooring stores','serviceType':label,'provider':{'@id':DOMAIN+'/#organization'},'areaServed':{'@type':'Country','name':'United States'},'audience':{'@type':'BusinessAudience','name':'Flooring stores and flooring companies'},'url':DOMAIN+'/services/'+slug+'/','description':description},faq_schema(SERVICE_FAQ[slug])])
 cards=''.join(f'<article class="service-card">{icon(s[4])}<h2>{s[1]}</h2><p>{s[3]}</p><p>{HUB_TEXT[s[0]][1]}</p>{link("/services/"+s[0]+"/",HUB_TEXT[s[0]][0])}</article>' for s in SERVICES)
 fit='<section class="section light"><div class="wrap narrow"><span class="eyebrow">Choosing where to start</span><h2>How the services fit together</h2><p>If your website is the bottleneck, start there. When shoppers cannot see what you sell or how to reach you, every other service has less to work with. Local SEO helps people nearby find your store when they search. Ads reach people who are planning a floor right now. AI search work uses the same store facts and answers, made clear enough for AI tools to read and repeat.</p><p>Most stores do not need all four at once. We look at your current website and local presence first, then agree which service comes first and what it includes.</p></div></section>'
 write('/services/','Flooring Marketing Services | CDL Marketing','Websites, local SEO, Google and Meta ads, and AI search visibility for independent flooring showrooms. Agree on the work your store needs.',subhero('Services','The right work.<br>For your showroom.','Start with the gaps that matter to your store. Each service has a defined scope, responsibilities and a way to review the work.','/services/')+'<section class="section"><div class="wrap cards two-cards">'+cards+'</div></section>'+fit+cta())


def pricing():
 body=subhero('Pricing','Month-to-month marketing.<br>A clear website option.','No long-term marketing contract. Agree the work, fees and cancellation notice in writing.','/pricing/')+'<section class="section"><div class="wrap article-layout">'+marketing_scope_note()+pricing_content()+'<h2>Proposed website terms: questions and answers</h2><p>'+PLAN_NOTICE+'</p>'+faqs(PLAN_FAQS)+'''<section id="guarantee"><h2>Clear work. Honest expectations.</h2><p>No search position, AI recommendation, inquiry count or sales result is promised. Local SEO, AI search visibility and advertising need their own agreed deliverables and budget.</p></section><h2>Let’s discuss your website</h2><p>Bring your current site and the problem you want solved. We can confirm whether this plan fits, check access and important pages, and agree the schedule before you commit.</p><p><a class="btn" href="/contact/">Discuss my website <span aria-hidden="true">→</span></a></p><p>Still comparing options? <a href="/guides/choosing-a-flooring-marketing-agency/">Use our agency buying checklist</a> or <a href="/compare/broadlume/">compare CDL and Broadlume / Cyncly</a>.</p>'''+'</div></section><section class="section light"><div class="wrap">'+transition_preview()+'</div></section>'+cta()
 write('/pricing/','Flooring Website & Marketing Pricing | CDL Marketing',PRICE_DESCRIPTION,body)


def about():
 body=subhero('About CDL','We know what it is like<br>to run a showroom.','CDL Marketing is part of CDL Management, based in Kirksville, Missouri. Caleb Foglesong and our team operate local businesses and do the marketing for them, too.','/about/')+'''<section class="section"><div class="wrap split"><div><span class="eyebrow">Our perspective</span><h2>Start with the work<br>behind the sale.</h2><p>Marketing is only part of the job. Someone has to answer the inquiry, help the homeowner, arrange the estimate and follow up on the quote. That is the world we work in.</p><p>Our background includes flooring retail, wholesale showrooms and other local service businesses.</p><p>We bring that practical perspective to websites, local search, advertising and AI search visibility for independent flooring showrooms.</p></div><div class="quote-panel"><span class="eyebrow" id="caleb-foglesong">Caleb Foglesong</span><h3>Showroom experience.<br>Plain answers.</h3><p class="bio-intro">CDL Marketing</p><p class="bio-copy">Our showroom background shapes the questions we ask. The next step is to show you how we approach your website, local presence and marketing priorities.</p><a class="text-link" href="/work-samples/">Review our illustrative work samples →</a></div></div></section><section class="section light"><div class="wrap narrow"><span class="eyebrow">How we judge the work</span><h2>Inquiries matter.<br>What happens next matters, too.</h2><p>We work toward more qualified conversations and sold jobs, rather than treating impressions or website visits as the finish line. When tracking is incomplete, we say so. A useful report should help you decide what to do next.</p><p>Compare the actual scope, separate costs and responsibilities before choosing an agency. Our operating background is not a substitute for a defined proposal.</p>'''+link('/pricing/','See pricing and scope')+'<p><a href="/guides/choosing-a-flooring-marketing-agency/">Read our agency buyer’s guide</a> · <a href="/compare/broadlume/">Compare CDL and Broadlume</a></p>'+'<h2>Can you work with what I already have?</h2><p>A new website is not required to discuss SEO or advertising. We first review access, compatibility and the inquiry path. Keep useful pages and tools where they support the agreed work.</p><h2>Who will I work with?</h2><p>Caleb is your first contact at CDL Marketing. Before paid work starts, agree on your day-to-day contact, approval responsibilities and how progress will be reviewed. We do not treat an inquiry as a signed engagement.</p></div></section>'+'<section class="section" id="who-we-are"><div class="wrap narrow"><span class="eyebrow">CDL Marketing</span><h2>Who CDL Marketing is</h2><p>CDL Marketing is the flooring marketing arm of CDL Management, a family company in Kirksville, Missouri. Caleb Foglesong, a third-generation flooring professional, leads the work. We market independent flooring stores across the United States, and we run flooring showrooms ourselves.</p><p>One note on the name: we are a flooring store marketing agency. We are not connected with commercial driver’s license (CDL) training, trucking or driver recruitment companies that use similar names.</p><p><a href="tel:+12172171705">Call (217) 217-1705</a> or <a href="/contact/">request a free growth audit</a>.</p></div></section>'+cta()
 write('/about/','About Caleb Foglesong & CDL Marketing','Meet CDL Marketing, part of CDL Management in Kirksville, Missouri. Marketing for flooring showrooms, from a team that operates flooring showrooms.',body,[{'@type':'Person','@id':DOMAIN+'/about/#caleb-foglesong','name':'Caleb Foglesong','url':DOMAIN+'/about/','worksFor':{'@id':DOMAIN+'/#organization'},'description':'Third-generation flooring professional who leads CDL Marketing.','knowsAbout':['Flooring retail','Flooring store marketing','Local search']}])

def contact():
 body=subhero('Contact','Let’s talk about<br>your showroom.','A free review of your website and local online presence, with three priority opportunities to discuss.','/contact/')+'<section class="section" id="apply"><div class="wrap contact-grid"><div class="contact-intro"><h2>A useful conversation.<br>No pressure.</h2><p>Tell us your showroom, location and website. We look at how your store appears online, where a shopper may struggle and which three opportunities deserve attention first. There is no obligation to hire us.</p><section class="callout" id="after-call"><h3>Already spoken with our team?</h3><p><a href="mailto:caleb@cdl1.net">Email Caleb</a> with your showroom name and the next step you discussed. You can ask a question or review your options before deciding to change anything.</p><p><a href="/about/">Check our background</a> · <a href="/pricing/">Review services and proposed costs</a></p><p><a href="/guides/flooring-marketing-checklist/">Note your own observations</a> or <a href="/guides/your-first-marketing-review/">prepare for the first review</a>. The checklist sends no answers.</p></section><p><a href="/work-samples/#audit">See a sample three-priority audit</a> before you request yours.</p><h3>What happens next?</h3><p>We review your website and public local presence, then discuss three priorities and any access limits. If you want to go further, the next step is a written scope with separate fees and responsibilities. No service or credit starts just because you ask.</p><p>Your name, showroom, city and email are enough to start. Your website helps us review it; phone and revenue are optional. Please do not send passwords, customer records or account credentials through this form.</p><div class="contact-links"><a href="tel:+12172171705">(217) 217-1705</a><a href="mailto:caleb@cdl1.net">caleb@cdl1.net</a></div><p class="inline-note">CDL Management · Kirksville, Missouri</p><div class="callout"><h3>Want to start with a design?</h3><p>Our free homepage mockup gives you something concrete to look at before deciding.</p>'+link('/free-mockup/','Request a free homepage design')+'</div>'+switching_contact_note()+'</div>'+form()+'</div></section>'
 write('/contact/','Free Flooring Marketing Audit | Contact CDL Marketing','Request a free growth audit for your flooring showroom. Contact CDL Marketing at (217) 217-1705 or caleb@cdl1.net. No obligation.',body)

def related_service(slug):
 if slug not in ARTICLE_SERVICE:return ''
 href,anchor=ARTICLE_SERVICE[slug]
 if href=='/':return f'<p class="related-service">CDL Marketing does <a href="{href}">{anchor}</a> month to month.</p>'
 return f'<p class="related-service">Want this handled for you? See our <a href="{href}">{anchor}</a>.</p>'

def legacy_pages():
 # Keep existing article bodies, publication dates and addresses. Refresh only shared presentation.
 slugs=sorted({f.parent.name for f in [*(LEGACY/'blog').glob('*/index.html'), *(ROOT/'source/articles').glob('*/index.html')]})
 for slug in sorted(set(slugs)|{x[0] for x in ARTICLE_INFO}):
  src=article_source(slug)
  if not src:
   # A listed article without a complete source is not built; drop an earlier generated copy so it is not published stale.
   stale=ROOT/'blog'/slug/'index.html'
   if stale.exists():stale.unlink();print(f'Removed stale generated page blog/{slug}/index.html')
   continue
  url=DOMAIN+'/blog/'+slug+'/'
  title,desc,h1,article=src['title'],src['desc'],src['h1'],src['article']
  article=re.sub(r'<p class="article-updated">.*?</p>','',article,count=1,flags=re.S)
  # Old article wrappers carried their own .wrap class. Keep prose, not old layout.
  article=article.replace('class="tbl"','class="tbl" role="region" aria-label="Article comparison table" tabindex="0"')
  article=article.replace('class="wrap prose"','class="prose"').replace('class="wrap article-body"','class="prose"')
  article=re.sub(r'<div class="wrap[^\"]*">','<div>',article)
  schemas=[]
  for obj in src['scripts']:
   if isinstance(obj,dict) and obj.get('@type') in ['Article','FAQPage','Dataset']:
    obj=dict(obj);obj.pop('@context',None);schemas.append(obj)
  article_schema=next((x for x in schemas if x.get('@type')=='Article'),{})
  author=article_schema.get('author',{})
  if isinstance(author,dict) and author.get('name')=='Caleb Foglesong':
   author.update({'@id':DOMAIN+'/about/#caleb-foglesong','url':DOMAIN+'/about/'})
  if schemas and article_schema:
   article_schema['publisher']={'@id':ORG['@id']}
   article_schema['mainEntityOfPage']={'@id':url+'#page'}
   if not article_schema.get('image'):article_schema['image']=OG_IMAGE
  def display_date(value):
   return date.fromisoformat(value[:10]).strftime('%B %-d, %Y') if value else ''
  published=article_schema.get('datePublished','')
  modified=article_schema.get('dateModified','')
  meta='By Caleb Foglesong'
  if published: meta+=' · Published '+display_date(published)
  if modified and modified!=published: meta+=' · Updated '+display_date(modified)
  body=subhero('Showroom insights',h1,'Practical guidance from the CDL Marketing team.','/blog/'+slug+'/',crumb=ESC(plain(html.unescape(title).split(' | ')[0])))+'<section class="section"><div class="wrap article-layout"><p class="article-meta">'+ESC(meta).replace('Caleb Foglesong','<a href="/about/#caleb-foglesong">Caleb Foglesong</a>')+'</p>'+article+related_service(slug)+'<aside><b>About the author</b><p>Caleb Foglesong is a third-generation flooring professional. His family company operates flooring showrooms and runs CDL Marketing.</p><a href="/about/">Learn about CDL Marketing</a></aside><p><a href="/blog/">← All flooring marketing insights</a></p></div></section>'+cta()
  write('/blog/'+slug+'/',html.unescape(title),html.unescape(desc),body,schemas)
 write('/blog/','Flooring Marketing Insights | CDL Marketing','Practical guides to flooring store marketing, local SEO, Google Business Profile and AI search from a team that operates showrooms.',subhero('Insights','Notes from<br>the showroom.','Practical answers to the questions flooring store owners ask about search, websites, advertising and follow-up.','/blog/')+'<section class="section"><div class="wrap">'+articles_cards(True)+'</div></section>'+cta())
 legal=privacy_content()
 write('/privacy/','Privacy Policy | CDL Marketing','How CDL Marketing collects, uses and protects the information you send through cdlmanagement.com.',subhero('Privacy','Privacy policy','What we collect through this website, why, and what we do with it.','/privacy/')+'<section class="section"><div class="wrap article-layout">'+legal+'</div></section>')
 write('/free-mockup/','Free Flooring Showroom Homepage Concept | CDL Marketing','Request a free homepage concept for your flooring showroom, with no obligation. A live website, hosting and ongoing services are scoped separately.',subhero('Free homepage concept','See what your<br>website could be.','A free visual homepage concept to discuss before deciding. A working website, hosting and ongoing marketing are separate services.','/free-mockup/')+'<section class="section"><div class="wrap contact-grid"><div><h2>Something concrete.<br>Before you decide.</h2><p>Tell us your business name and current website. We review the basics and follow up by email to agree the next step for a homepage concept.</p><ol><li>Share your business and the problem you want the homepage to solve.</li><li>Review a visual direction for your services and market.</li><li>Decide whether to discuss a separately scoped website build. There is no obligation to hire us.</li></ol><p>Before preparing the concept, we confirm the format, timing and how you may use it. A working website and ongoing service need a separate agreed scope.</p><p>Our main focus is independent flooring showrooms. If yours is another local business, select its type so we can confirm fit.</p><p>Want a review of your existing site first? <a href="/contact/">Request a free growth audit</a>. Questions? <a href="tel:+12172171705">Call (217) 217-1705</a>.</p></div>'+form('mockup')+'</div></section>')


def buyer_pages():
 write('/compare/broadlume/','CDL Marketing vs Broadlume | Flooring Agency Comparison','Compare CDL Marketing with Broadlume and Cyncly: services, published evidence, scope and questions to ask before choosing a flooring marketing provider.',subhero('Agency comparison','CDL and Broadlume.<br>Compare what fits.','Look at the work, evidence and terms behind each proposal.','/compare/broadlume/')+comparison_body()+cta())
 write('/guides/choosing-a-flooring-marketing-agency/','How to Choose a Flooring Marketing Agency | CDL Marketing','A practical checklist for flooring showroom owners comparing marketing agencies: scope, pricing, websites, data, proof and questions to ask.',subhero('Buyer’s guide','Choose an agency<br>with clear answers.','A practical checklist for independent flooring showroom owners.','/guides/choosing-a-flooring-marketing-agency/')+'<section class="section"><div class="wrap article-layout">'+resource_links()+'</div></section>'+agency_guide_body()+cta())

def switching():
 write('/switch/','Switch Website Providers | Proposed CDL Transition Credits','Review proposed CDL website-service credits when switching from Broadlume or another provider. Eligibility, setup, paid marketing and credit terms need written approval.',subhero('Switching providers','Switch providers<br>with a clear plan.','Month-to-month marketing and proposed monthly website-service credits. Review both paths, then confirm your eligibility and terms in writing.','/switch/')+switch_page_body())

def retailer_pages():
 write(READINESS_PATH,'Flooring Website Switch Checklist | CDL Marketing','Check contract dates, account control, content rights, analytics and inquiry routes before planning a flooring website move, cutover or rollback.',subhero('Switch readiness','Know what can move.<br>Protect what must work.','A practical checklist for changing website providers around your actual agreement, accounts and customer paths.',READINESS_PATH)+readiness_body())
 write(CHECKLIST_PATH,'Flooring Marketing Checklist | CDL Marketing','Check your flooring website, local information and advertising. Organize observations for a useful first review, with no score or contact details required.',subhero('For showroom owners','A practical flooring<br>marketing checklist.','Six checks to help you see what works, what needs attention and what you still need to find out.',CHECKLIST_PATH)+checklist_body(),extra_scripts=('/assets/diagnostic.js',))
 write(REVIEW_PATH,'Your First Flooring Marketing Review | CDL Marketing','Prepare for a flooring marketing review: what to bring, how to assess your current website, and how SEO, advertising and a careful transition fit together.',subhero('Your first review','Start with your showroom.<br>Agree a useful next step.','A guide to the first assessment, the work you might need and a careful transition if you choose to change providers.',REVIEW_PATH)+first_review_body())

def work_samples():
 write(WORK_PATH,WORK_TITLE,WORK_DESCRIPTION,subhero('Work samples','See the thinking.<br>See the next step.','A sample audit, showroom page concept and monthly report to help you judge the approach before discussing a paid scope.',WORK_PATH)+work_samples_body()+cta())

LLMS_HEADER='''# CDL Marketing

> CDL Marketing is a flooring marketing agency, part of CDL Management in Kirksville, Missouri. We own and run flooring showrooms ourselves, and we do marketing for flooring stores and flooring companies across the United States: flooring SEO, local SEO and Google Business Profiles, flooring website design, Google and Facebook ads, and AI search visibility (GEO). Marketing is month-to-month: if we don't do what we say, clients can let us go.

Contact: (217) 217-1705, caleb@cdl1.net. Founder: Caleb Foglesong.
'''
LLMS_FIRST=['/','/blog/marketing-for-flooring-stores/','/blog/flooring-store-website-speed-study/']

def llms_txt():
 # Generated from the same pages as sitemap.xml so it never goes stale.
 groups={'Services':[],'Guides and research':[],'Company':[]}
 for path in sorted(PAGES,key=lambda x:(LLMS_FIRST.index(x) if x in LLMS_FIRST else len(LLMS_FIRST))):
  group='Services' if path=='/' or path.startswith('/services/') or path=='/pricing/' else 'Guides and research' if path.startswith(('/blog/','/guides/','/compare/')) else 'Company'
  title,description=PAGE_META[path]
  clean=lambda text:re.sub(r'\s+',' ',text.replace('—',', ').replace(' – ',' to ').replace('–',' to ')).strip()
  groups[group].append(f'- [{clean(title)}]({DOMAIN+path}): {clean(description)}')
 return LLMS_HEADER+''.join(f'\n## {name}\n'+'\n'.join(lines)+'\n' for name,lines in groups.items() if lines)

def main():
 home();services();pricing();about();contact();legacy_pages();buyer_pages();switching();retailer_pages();work_samples()
 not_found='<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found | CDL Marketing</title><link rel="stylesheet" href="/assets/site.css"><script src="/assets/site.js" defer></script><script src="/assets/track.js" defer></script></head><body>'+header()+'<main id="main" tabindex="-1"><section class="section"><div class="wrap narrow"><span class="eyebrow">Page not found</span><h1>Let’s get you back<br>to the showroom.</h1><p>That page is not available. You can explore our services or contact the team.</p><p><a class="btn" href="/">Go to the homepage</a></p><p><a href="/contact/">Contact CDL Marketing</a></p></div></section></main>'+footer()+'</body></html>'
 (ROOT/'404.html').write_text(not_found)
 ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns)
 root=ET.Element('{'+ns+'}urlset')
 for path in PAGES:
  item=ET.SubElement(root,'{'+ns+'}url');ET.SubElement(item,'{'+ns+'}loc').text=DOMAIN+path;ET.SubElement(item,'{'+ns+'}lastmod').text=LASTMOD.get(path,BUILD_DATE)
 ET.ElementTree(root).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
 (ROOT/'llms.txt').write_text(llms_txt())
 print(f'Built {len(PAGES)} public pages. No deployment performed.')

if __name__=='__main__':main()
