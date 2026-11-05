#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the complete static CDL Marketing site. No network access or deployment."""
from pathlib import Path
import re, json, html, xml.etree.ElementTree as ET
from datetime import date
from buyer_content import comparison_body, agency_guide_body
from website_offer import PRICE, PRICE_HTML, SUMMARY, EXIT_SUMMARY, SEPARATE, PRICE_DESCRIPTION, PLAN_FAQ, PLAN_FAQS, pricing_content
from transition_offer import MARKETING_HEADLINE, MARKETING_SUMMARY, MARKETING_FAQ, REQUEST_NOTICE, marketing_scope_note, transition_preview, switching_contact_note, switch_page_body

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / 'source/legacy'
DOMAIN = 'https://cdlmanagement.com'
PAGES = []
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
 return f'''<a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="/"><b>CDL</b>Marketing<small>Marketing for flooring showrooms</small></a><nav class="desktop-nav" aria-label="Main navigation"><details class="nav-services"><summary>Services</summary><div class="nav-popover">{nav}</div></details><a href="/about/">Why CDL</a><a href="/pricing/">Pricing</a><a href="/guides/choosing-a-flooring-marketing-agency/">Guides</a><a href="/contact/" class="btn">Free audit <span aria-hidden="true">↗</span></a></nav><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu">Menu <span aria-hidden="true">☰</span></button></div><nav id="mobile-menu" class="mobile-nav" aria-label="Mobile navigation" hidden><a href="/services/">All services</a>{nav}<a href="/about/">Why CDL</a><a href="/pricing/">Pricing</a><a href="/guides/choosing-a-flooring-marketing-agency/">Buyer guides</a><a href="/blog/">Showroom insights</a><a href="/contact/">Free audit</a></nav></header>'''

def footer():
 return '''<footer class="site-footer"><div class="wrap"><div class="footer-top"><div><a class="brand" href="/"><b>CDL</b>Marketing</a><p>Marketing for flooring showrooms.<br>From people who run showrooms, too.</p><a href="tel:+16606653889">(660) 665-3889</a><br><a href="mailto:caleb@cdl1.net">caleb@cdl1.net</a></div><nav class="footer-links" aria-label="Service links"><b>What we do</b><a href="/services/websites/">Showroom websites</a><a href="/services/local-seo/">Local SEO</a><a href="/services/paid-ads/">Google &amp; Meta ads</a><a href="/services/ai-search/">AI search visibility</a></nav><nav class="footer-links" aria-label="Company links"><b>Get to know us</b><a href="/about/">Why CDL</a><a href="/pricing/">Pricing &amp; scope</a><a href="/switch/">Switching providers</a><a href="/guides/choosing-a-flooring-marketing-agency/">Choosing an agency</a><a href="/compare/broadlume/">CDL &amp; Broadlume</a><a href="/blog/">Showroom insights</a><a href="/free-mockup/">Free homepage design</a><a href="/contact/">Contact us</a><a href="/privacy/">Privacy policy</a></nav></div><div class="footer-bottom"><span>© 2026 CDL Management · CDL Marketing · Kirksville, Missouri</span><span>Showroom experience. Clear answers.</span></div></div></footer>'''

ORG = {'@type':'Organization','@id':DOMAIN+'/#organization','name':'CDL Marketing','legalName':'CDL Management','url':DOMAIN+'/','telephone':'+1-660-665-3889','email':'caleb@cdl1.net'}

def write(path,title,description,body,schema=None):
 url=DOMAIN+path
 data=[ORG,{'@type':'WebSite','@id':DOMAIN+'/#website','name':'CDL Marketing','url':DOMAIN+'/'}, {'@type':'WebPage','@id':url+'#page','url':url,'name':title,'description':description,'isPartOf':{'@id':DOMAIN+'/#website'},'about':{'@id':DOMAIN+'/#organization'}}]
 if schema: data.extend(schema)
 if path != '/':
  name=re.sub('<[^>]+>','',title.split(' | ')[0])
  data.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':DOMAIN+'/'},{'@type':'ListItem','position':2,'name':name,'item':url}]})
 schema_json=json.dumps({'@context':'https://schema.org','@graph':data},ensure_ascii=False).replace('</','<\\/')
 out=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{ESC(title)}</title><meta name="description" content="{ESC(description,quote=True)}"><link rel="canonical" href="{url}"><meta name="theme-color" content="#f7f3ec"><meta property="og:type" content="website"><meta property="og:site_name" content="CDL Marketing"><meta property="og:title" content="{ESC(title,quote=True)}"><meta property="og:description" content="{ESC(description,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{DOMAIN}/assets/og-marketing-20261105.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{ESC(title,quote=True)}"><meta name="twitter:description" content="{ESC(description,quote=True)}"><meta name="twitter:image" content="{DOMAIN}/assets/og-marketing-20261105.jpg"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css"><script type="application/ld+json">{schema_json}</script><script src="/assets/site.js" defer></script><script src="/assets/track.js" defer></script></head><body>{header()}<main id="main" tabindex="-1">{body}</main>{footer()}</body></html>'''
 article_schema=next((item for item in data if item.get('@type')=='Article'),None)
 if article_schema:
  out=out.replace('property="og:type" content="website"','property="og:type" content="article"')
  dates=''.join(f'<meta property="article:{prop}_time" content="{ESC(str(article_schema[key]),quote=True)}">' for key,prop in [('datePublished','published'),('dateModified','modified')] if article_schema.get(key))
  out=out.replace('</head>',dates+'</head>')
 out=out.replace('—',', ').replace(' – ',' to ')
 out='\n'.join(line.rstrip() for line in out.splitlines())+'\n'
 dest=ROOT/path.strip('/')/'index.html' if path!='/' else ROOT/'index.html'
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(out)
 PAGES.append(path)

def subhero(label,title,description,path):
 return f'<section class="sub-hero"><div class="wrap"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span>{label}</span></nav><span class="eyebrow">{label}</span><h1>{title}</h1><p>{description}</p></div></section>'

def cta():
 return '<section class="cta-band"><div class="wrap"><div><h2>Let’s look at your showroom.</h2><p>Start with a free growth audit. No pressure. No obligation.</p></div>'+link('/contact/','Get my growth audit','btn')+'</div></section>'

def faqs(items):
 return '<div class="faq-list">'+''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in items)+'</div>'

FAQ=[
 ('Who is CDL Marketing a good fit for?','Independent flooring showroom owners who want practical help with their website, local visibility or advertising. We first check your goals, market, current tools and access before recommending a scope.'),
 ('What do you offer?','Showroom websites, local SEO, Google and Meta advertising, and AI search visibility. We agree on the work you need rather than assuming every store needs every service. <a href="/services/">Explore the services.</a>'),
 ('How is CDL different from a general agency?','We operate Kirksville Carpet One, Springfield Carpet One and Columbia Rug Carpet One in Peoria. That gives us direct experience with product questions, estimates and the work behind a sold job. <a href="/about/">See our operating background.</a>'),
 ('How long does flooring marketing take?','Timing depends on your market, starting point, access and agreed work. Ads can reach buyers while a campaign runs; organic visibility needs sustained work. The first 90 days are a planning and review period, not a promised sales result.'),
 ('Do I need to replace my website or CRM?','We assess your existing website first. CRM integration is planned for later and is not part of our current offer. <a href="/services/flooring-crm/">Read our approach to existing systems.</a>'),
 MARKETING_FAQ,
 PLAN_FAQ,
 ('Can you guarantee rankings, AI mentions or leads?','No. We do not promise a search position, AI recommendation or lead count with the website offer. We agree on deliverables and review the evidence, including gaps in tracking.'),
 ('What will I receive in the free audit?','A review of your website and local online presence, with three priority opportunities to discuss. It is a practical starting point, with no obligation to hire us.'),
]

def form(kind='audit'):
 audit=kind=='audit'
 extra='''<div class="fields-row"><div class="field"><label for="revenue">Approximate monthly revenue (optional)</label><select id="revenue" name="revenue"><option value="">Choose a range</option><option>Under $50k / mo</option><option>$50k to $100k / mo</option><option>$100k to $250k / mo</option><option>$250k+ / mo</option></select></div><div class="field"><label for="goal">Biggest goal (optional)</label><select id="goal" name="goal"><option value="">Choose a goal</option><option>More local customers / leads</option><option>Rank higher on Google</option><option>A system to follow up on leads</option><option>Run better ads</option><option>All of the above</option><option>Switch providers: website only</option><option>Switch providers: SEO and advertising</option></select></div></div>''' if audit else '''<div class="field"><label for="vertical">Business type</label><select id="vertical" name="vertical" required><option value="">Choose one</option><option value="Flooring">Flooring store</option><option value="Restoration">Restoration company</option><option value="Assisted Living">Assisted living</option><option value="Fitness">Fitness center / gym</option><option value="Massage">Massage therapy</option><option>Other</option></select></div>'''
 city='<div class="field"><label for="city">City and state</label><input id="city" name="city" autocomplete="address-level2" required maxlength="160"></div>' if audit else ''
 request_note='<p class="form-fine">'+REQUEST_NOTICE+'</p>' if audit else ''
 return f'''<form class="lead-form" method="post" id="{'applyForm' if audit else 'leadForm'}" data-lead-form="{kind}"><div class="form-fields"><h3>{'Tell us about your showroom' if audit else 'Claim your free homepage design'}</h3><p class="muted">{'Required: your name, showroom, city and state, and email.' if audit else 'Required: business name, your name, email and business type.'}</p><div class="field"><label for="name">Your name</label><input id="name" name="name" autocomplete="name" required maxlength="160"></div><div class="field"><label for="showroom">{'Showroom' if audit else 'Business'} name</label><input id="showroom" name="showroom" autocomplete="organization" required maxlength="200"></div>{city}<div class="fields-row"><div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required maxlength="254"></div><div class="field"><label for="phone">Phone (optional)</label><input id="phone" name="phone" type="tel" autocomplete="tel" maxlength="40"></div></div><div class="field"><label for="website">Current website (optional)</label><input id="website" name="website" inputmode="url" autocomplete="url" maxlength="500" placeholder="yourshowroom.com"></div>{extra}<div class="hp" aria-hidden="true"><label for="company_website_hp">Leave this field blank</label><input id="company_website_hp" name="company_website_hp" tabindex="-1" autocomplete="off"></div><button class="btn" type="submit" disabled>{'Request my free growth audit' if audit else 'Send me my free design'} <span aria-hidden="true">→</span></button><p class="form-fine">By sending, you ask us to contact you about your request. We do not sell your details. <a href="/privacy/">Privacy policy</a>.</p>{request_note}<noscript><p>Please enable JavaScript to send this form, or <a href="mailto:caleb@cdl1.net">email caleb@cdl1.net</a>.</p></noscript></div><div class="form-message" role="status" aria-live="polite" aria-atomic="true"></div></form>'''

def portrait():
 if (ROOT/'assets/caleb-portrait.webp').exists():
  return '<img class="portrait" src="/assets/caleb-portrait.webp" srcset="/assets/caleb-portrait-400.webp 400w, /assets/caleb-portrait.webp 700w" sizes="(max-width: 600px) calc(100vw - 82px), (max-width: 820px) 340px, 460px" width="700" height="1202" fetchpriority="high" alt="Caleb Foglesong, owner of CDL Marketing"><div class="portrait-caption"><b>Caleb Foglesong</b>Owner, CDL Management</div>'
 return '<div class="portrait-placeholder"><span class="placeholder-label">Portrait placement preview</span><span class="initials" aria-hidden="true">CF</span><p>Caleb’s verified photo will go here.<br>This is a photo placeholder.</p></div><div class="portrait-caption"><b>Caleb Foglesong</b>Owner, CDL Management</div>'

def home():
 cards=''.join(f'<article class="service-card">{icon(s[4])}<h3>{s[1]}</h3><p>{s[3]}</p>{link("/services/"+s[0]+"/","Explore "+s[1].lower())}</article>' for s in SERVICES)
 body=f'''<section class="hero" id="top"><div class="wrap hero-grid"><div class="hero-copy"><span class="eyebrow">{MARKETING_HEADLINE}</span><h1>Marketing built for<br><span>flooring showrooms.</span></h1><p class="intro">{MARKETING_SUMMARY} From a team that runs showrooms, too.</p><div class="hero-actions">{link('/contact/','Get my free growth audit','btn')}<a href="/switch/">Switching providers? Explore the proposed support →</a></div><p class="hero-note">{PRICE} · Recommended website plan</p></div><div class="hero-art">{portrait()}</div></div></section><div class="trust-strip"><div class="wrap trust-inner"><span>Built on our own showroom experience</span><span>Kirksville, Missouri</span><span>Springfield, Missouri</span><span>Peoria, Illinois</span></div></div>
 <section class="section" id="services"><div class="wrap"><div class="section-heading"><span class="eyebrow">A clear path from search to showroom</span><h2>Start with what<br>your store needs.</h2><p>A useful website. Accurate local information. Advertising with a clear purpose. We agree on the right work for your showroom.</p></div><div class="cards two-cards">{cards}</div></div></section>
 <section class="section light"><div class="wrap">{transition_preview()}</div></section>
 <section class="section light" id="edge"><div class="wrap split"><div id="own-stores"><span class="eyebrow">We’re in the flooring business, too</span><h2>The stores came first.<br>The marketing followed.</h2><p class="muted">Our team runs flooring showrooms and handles the marketing for our own businesses. We know the product questions, estimate requests and daily decisions behind an inquiry.</p>{link('/about/','See the stores behind CDL')}<ul class="store-list"><li>Kirksville Carpet One <small>Kirksville, MO</small></li><li>Springfield Carpet One <small>Springfield, MO</small></li><li>Columbia Rug Carpet One <small>Peoria, IL</small></li></ul></div><div class="quote-panel"><span class="eyebrow">Choose with clear information</span><h3>Ask better questions.<br>Get a clearer proposal.</h3><p class="muted">Compare scope, costs, systems and evidence before choosing an agency.</p>{link('/guides/choosing-a-flooring-marketing-agency/','Read the buyer’s guide')}<br>{link('/compare/broadlume/','Compare CDL and Broadlume')}</div></div></section>
 <section class="section"><div class="wrap"><div class="section-heading"><span class="eyebrow">Your first 90 days, planned together</span><h2>A plan you can understand.<br>Work you can review.</h2><p>Milestones depend on the scope and access we agree on. This is a working plan, not a promised result.</p></div><div class="process"><article><span class="step-number">01</span><h3>Look at your market.</h3><p>Review your website, local presence and current advertising. Agree on priorities, responsibilities and what can be measured.</p></article><article><span class="step-number">02</span><h3>Put the plan to work.</h3><p>Build or improve the agreed pages, business information or campaigns. You supply accurate store facts and approve offers and creative.</p></article><article><span class="step-number">03</span><h3>Review. Adjust. Repeat.</h3><p>Review completed work, inquiries and lead quality where the data is available. Choose the next changes from the evidence.</p></article></div></div></section>
 <section class="section dark-section" id="pricing"><div class="wrap price-teaser"><div><span class="eyebrow">Recommended standalone website plan</span><h2>A website.<br>A clear next step.</h2><div class="price-amount">{PRICE_HTML}</div><p class="scope-note">{SUMMARY}</p><p class="scope-note">Month-to-month after launch. Cancel with 30 days’ notice. Your domain and accounts stay yours, with a portable website handover after setup is paid.</p>{link('/pricing/','See pricing and scope')}</div><div class="price-summary" id="guarantee"><span class="eyebrow">Add the marketing you need</span><h3>Local SEO. Paid ads.<br>AI search visibility.</h3><p>Each is quoted to fit your store and agreed scope. Advertising spend is always separate. CRM is not included in the current offer.</p><p>The website service carries no promised ranking, AI mention or lead count.</p></div></div></section>
 <section class="section"><div class="wrap faq-layout"><div class="section-heading"><span class="eyebrow">Good questions deserve clear answers</span><h2>Before you<br>hand us the keys.</h2><p>How we work, what it costs and what to expect.</p>{link('/contact/','Ask us something else')}</div>{faqs(FAQ)}</div></section>
 <section class="section light"><div class="wrap"><div class="section-heading"><span class="eyebrow">Notes from the showroom</span><h2>Useful answers.<br>No marketing lecture.</h2></div>{articles_cards()}<p class="inline-note">{link('/blog/','Read all showroom insights')}</p></div></section>
 <section class="section" id="apply"><div class="wrap contact-grid"><div class="contact-intro"><span class="eyebrow">Your free growth audit</span><h2>Three priorities.<br>A useful starting point.</h2><p>We review your website and local online presence, then identify three priority opportunities to discuss. The audit is free, with no obligation to hire us.</p><div class="contact-links"><a href="tel:+16606653889">(660) 665-3889</a><a href="mailto:caleb@cdl1.net">caleb@cdl1.net</a></div><p class="inline-note">Prefer to start with a design? <a href="/free-mockup/">Request a free homepage mockup.</a></p></div>{form()}</div></section>'''
 write('/','Month-to-Month Flooring Marketing | CDL Marketing','Month-to-month SEO and advertising for flooring showrooms. Clear written scope, showroom websites and proposed switching credits subject to review.',body)

ARTICLE_INFO=[('local-seo-for-flooring-stores','Local search','Local SEO for flooring stores: a practical checklist','Start with your Business Profile, consistent information and useful local pages.'),('marketing-for-flooring-stores','Showroom growth','What actually brings in showroom visits','How search, your website and follow-up work together.'),('flooring-store-chatgpt-ai-search','AI search','How flooring stores can show up in AI search','Clear business details and helpful answers give search services usable information.'),('google-business-profile-for-flooring-stores','Google Business Profile','The Business Profile setup we use','Give homeowners accurate hours, a useful description and the right next step.')]

def articles_cards(all_posts=False):
 return '<div class="article-grid">'+''.join(f'<article class="article-card"><p class="article-type">{tag}</p><h3><a href="/blog/{slug}/">{title}</a></h3><p>{desc}</p>{link("/blog/"+slug+"/","Read the guide")}</article>' for slug,tag,title,desc in (ARTICLE_INFO if all_posts else ARTICLE_INFO[:3]))+'</div>'

DETAIL={
 'websites': {
 'h1':'Flooring showroom websites that help people take the next step.',
 'intro':f'Recommended standalone website plan: {PRICE}. A useful website for one showroom, with hosting, care and monthly updates.',
 'answer':'A flooring showroom website should quickly answer three questions: does this store have what I need, does it serve my area and how do I get help? We organize the agreed pages around those decisions.',
 'work':SUMMARY+' Setup includes one brand direction, up to 5,000 words, 20 supplied images, two consolidated revision rounds and up to two pages formatting your supplied legal text. One standard inquiry form, search foundations, measurement setup and up to 20 agreed redirects are included. <a href="/pricing/#included">See the full build scope.</a>',
 'provide':'Your store details, product and installation facts, approved photography, brand requirements, website access and a person who can review the content. We assess co-op and provider restrictions first.',
 'review':'You review the design/content draft and the final version before launch. We check mobile/desktop pages, keyboard use, links, redirects and real inquiry delivery to the agreed destination, with your authorization. Monthly care includes availability monitoring, link/form checks, versioned backups, restoration and a short care summary.',
 'separate':f'{PRICE}. '+SEPARATE+' New pages, redesigns, integrations and bulk imports need a separate scope. Extra work is $125/hour or a written fixed quote, approved before work begins. '+EXIT_SUMMARY,
 'related':['local-seo-for-flooring-stores','marketing-for-flooring-stores']},
 'local-seo': {
 'h1':'Local SEO for flooring stores that need to be found nearby.',
 'intro':'Accurate business information and useful local pages for homeowners looking for flooring in your area.',
 'answer':'Local SEO connects an accurate Google Business Profile, a useful showroom website and consistent business information. We identify gaps in the area you really serve and agree on the work to address them.',
 'work':'Review your Business Profile, categories, services, contact information and key listings. Plan useful service and location content around actual buyer questions, with technical checks and internal links.',
 'provide':'Access to the correct profiles and website, accurate hours and service areas, real product and installation details, approved images and content approval. We do not add services you do not offer.',
 'review':'Review completed changes and search visibility alongside relevant calls and forms where tracking is available. A ranking observation is not a sold job; incomplete attribution stays visible.',
 'separate':'Local SEO is custom quoted. Website changes beyond the agreed scope, paid advertising, media and optional third-party tools are identified separately in the proposal.',
 'related':['local-seo-for-flooring-stores','google-business-profile-for-flooring-stores']},
 'paid-ads': {
 'h1':'Flooring store advertising with a clear next step.',
 'intro':'Google and Meta campaigns connected to your products, your market and the right landing page.',
 'answer':'A flooring ad should connect a relevant homeowner with a useful offer and an easy way to ask for help. We plan targeting, copy, creative and review around the scope your showroom needs.',
 'work':'Plan agreed Google or Meta campaigns, match offers to landing pages, review search terms or audience settings and adjust creative and targeting around the available lead-quality evidence.',
 'provide':'Ad-account access, an agreed media budget, accurate offers and availability, approved claims and imagery, landing-page access and staff input on inquiry quality. Your team handles customer conversations.',
 'review':'Review spend, inquiry quality and landing-page behavior. When source and sold-job data can be linked, include them with the reporting period and coverage; do not treat platform conversions as verified sales.',
 'separate':'Ad management is custom quoted. Media is paid separately to the platforms. Campaign scope, creative production, landing-page work and optional tools are defined before commitment.',
 'related':['marketing-for-flooring-stores']},
 'ai-search': {
 'h1':'AI search visibility built on useful showroom facts.',
 'intro':'Clear, reliable information for the questions homeowners ask search engines and AI tools.',
 'answer':'AI search visibility means making your store information easy to find, understand and verify. It complements SEO. No agency can promise that a search engine or AI tool will recommend your showroom.',
 'work':'Review buyer questions, strengthen direct answers on relevant pages, align public business details and use structured data that matches visible facts. Check a documented sample of questions and record the answers and sources.',
 'provide':'Verified store facts, product and service details, permission to edit relevant pages and listings, real photos and an approver. Claims need evidence before they appear in content.',
 'review':'Compare dated observations for the same questions and tools, recognizing that answers vary. Separate mentions, referrals, inquiries and sold jobs. A small sample is not market-wide visibility or proof that a change caused a result.',
 'separate':'AI search work is custom quoted. Website production, local SEO campaigns, paid media and optional monitoring tools are specified separately. Google says existing SEO best practices apply to its AI features; there is no special schema requirement.',
 'related':['flooring-store-chatgpt-ai-search','local-seo-for-flooring-stores']}
}

def services():
 for slug,label,headline,desc,_ in SERVICES:
  d=DETAIL[slug]
  items=[('What we work on',d['work']),('What your team provides',d['provide']),('How we review the work',d['review']),('What is quoted separately',d['separate'])]
  sections=''.join(f'<section id="part-{i}"><h2>{h}</h2><p>{p}</p></section>' for i,(h,p) in enumerate(items,1))
  related=''.join(f'<li><a href="/blog/{key}/">{next(x[2] for x in ARTICLE_INFO if x[0]==key)}</a></li>' for key in d['related'])
  source='<p>Source: <a href="https://developers.google.com/search/docs/appearance/ai-features">Google Search Central: AI features and your website</a>. Inclusion and presentation remain Google’s decisions.</p>' if slug=='ai-search' else ''
  body=subhero(label,d['h1'],d['intro'],'/services/'+slug+'/')+f'<section class="section"><div class="wrap article-layout"><p class="answer">{d["answer"]}</p><nav class="toc" aria-label="On this page"><b>On this page</b>'+''.join(f'<a href="#part-{i}">{h}</a>' for i,(h,p) in enumerate(items,1))+f'</nav>{sections}{source}<aside><b>Agree on the scope first</b><p>Recommended standalone website plan: {PRICE}. {SUMMARY} Marketing services and advertising spend are separate.</p><a href="/pricing/">See pricing and proposal details</a></aside><h2>Keep reading</h2><ul>{related}<li><a href="/guides/choosing-a-flooring-marketing-agency/">How to choose a flooring marketing agency</a></li></ul><p><a href="/services/">Explore all marketing services</a></p></div></section>'+cta()
  if slug == 'websites': body=body.removesuffix(cta())+'<section class="section light"><div class="wrap">'+transition_preview()+'</div></section>'+cta()
  else:
   website_aside=f'<aside><b>Agree on the scope first</b><p>Recommended standalone website plan: {PRICE}. {SUMMARY} Marketing services and advertising spend are separate.</p><a href="/pricing/">See pricing and proposal details</a></aside>'
   service_aside='<aside><b>Start with the service you need</b><p>We assess your current website before recommending a replacement. This service has its own agreed scope and fee; advertising spend is separate.</p><a href="/pricing/">See pricing and scope</a></aside>'
   assert website_aside in body
   body=body.replace(website_aside,service_aside)
  write('/services/'+slug+'/',label+' for Flooring Showrooms | CDL Marketing',d['intro'],body,[{'@type':'Service','name':label+' for flooring showrooms','serviceType':label,'provider':{'@id':DOMAIN+'/#organization'},'url':DOMAIN+'/services/'+slug+'/','description':d['intro']}])
 cards=''.join(f'<article class="service-card">{icon(s[4])}<h2>{s[1]}</h2><p>{s[3]}</p>{link("/services/"+s[0]+"/","Explore "+s[1].lower())}</article>' for s in SERVICES)
 write('/services/','Flooring Marketing Services | CDL Marketing','Websites, local SEO, Google and Meta ads, and AI search visibility for independent flooring showrooms. Agree on the work your store needs.',subhero('Services','The right work.<br>For your showroom.','Start with the gaps that matter to your store. Each service has a defined scope, responsibilities and a way to review the work.','/services/')+'<section class="section"><div class="wrap cards two-cards">'+cards+'</div></section>'+cta())
 crm=subhero('Existing systems','Your existing CRM.<br>A later conversation.','Our current offer is marketing: websites, local SEO, paid advertising and AI search visibility.','/services/flooring-crm/')+'<section class="section"><div class="wrap article-layout"><h2>CRM integration is planned for later</h2><p>We are not selling a CRM or replacing your estimating, inventory, accounting or showroom software. CRM integration is not included in our current website or marketing offer.</p><p>For future work, we would first assess your existing system, access and supported connections. Any integration would need a separate agreed scope and verification. No connection is promised before that review.</p><h2>Keep the marketing scope clear</h2><p>Your team still owns customer conversations and quote follow-up. We agree on where marketing inquiries should go and review only the data we can actually access.</p><p><a href="/services/">Explore current marketing services</a> or <a href="/pricing/">review pricing and scope</a>.</p></div></section>'+cta()
 write('/services/flooring-crm/','Existing CRM & Future Integrations | CDL Marketing','CRM integration is planned for later. CDL currently offers websites and marketing services, not a CRM product or replacement for showroom business software.',crm)


def pricing():
 body=subhero('Pricing','Month-to-month marketing.<br>A clear website option.','No long-term marketing contract. Agree the work, fees and cancellation notice in writing.','/pricing/')+'<section class="section"><div class="wrap">'+transition_preview()+'</div></section><section class="section"><div class="wrap article-layout">'+marketing_scope_note()+pricing_content()+faqs(PLAN_FAQS)+'''<section id="guarantee"><h2>Clear work. Honest expectations.</h2><p>No search position, AI recommendation, inquiry count or sales result is promised with this website subscription. Local SEO, AI search visibility and advertising need their own agreed deliverables and budget.</p></section><h2>Let’s discuss your website</h2><p>Bring your current site and the problem you want solved. We can confirm whether this plan fits, check access and important pages, and agree the schedule before you commit.</p><p><a class="btn" href="/contact/">Discuss my website <span aria-hidden="true">→</span></a></p><p>Still comparing options? <a href="/guides/choosing-a-flooring-marketing-agency/">Use our agency buying checklist</a> or <a href="/compare/broadlume/">compare CDL and Broadlume / Cyncly</a>.</p>'''+'</div></section>'+cta()
 write('/pricing/','Flooring Website & Marketing Pricing | CDL Marketing',PRICE_DESCRIPTION,body)


def about():
 body=subhero('About CDL','We know what it is like<br>to run a showroom.','CDL Marketing is part of CDL Management, based in Kirksville, Missouri. Caleb Foglesong and our team operate local businesses and do the marketing for them, too.','/about/')+'''<section class="section"><div class="wrap split"><div><span class="eyebrow">Our perspective</span><h2>Start with the work<br>behind the sale.</h2><p>Marketing is only part of the job. Someone has to answer the inquiry, help the homeowner, arrange the estimate and follow up on the quote. That is the world we work in.</p><p>Our flooring experience includes <a href="https://www.kirksvillecarpetone.com/">Kirksville Carpet One in Missouri</a>, <a href="https://www.carpetonespringfield.com/">Springfield Carpet One in Missouri</a> and <a href="https://www.columbiarugcarpetonepeoria.com/">Columbia Rug Carpet One in Peoria, Illinois</a>, along with ProSource wholesale showrooms. Our broader operating experience also includes other local service businesses.</p><p>We bring that practical perspective to websites, local search, advertising and AI search visibility for independent flooring showrooms.</p></div><div class="quote-panel"><span class="eyebrow">Caleb Foglesong</span><h3>Owner, CDL Management</h3><p>Showroom experience.<br>Plain answers.<br>Work you can review.</p><small>We have not published independent client case studies or a verified client-results history. Our operating background is the evidence we can share today.</small></div></div></section><section class="section light"><div class="wrap narrow"><span class="eyebrow">How we judge the work</span><h2>Inquiries matter.<br>What happens next matters, too.</h2><p>We work toward more qualified conversations and sold jobs, rather than treating impressions or website visits as the finish line. When tracking is incomplete, we say so. A useful report should help you decide what to do next.</p><p>Compare the actual scope, separate costs and responsibilities before choosing an agency. Our operating background is not a substitute for a defined proposal.</p>'''+link('/pricing/','See pricing and scope')+'<p><a href="/guides/choosing-a-flooring-marketing-agency/">Read our agency buyer’s guide</a> · <a href="/compare/broadlume/">Compare CDL and Broadlume</a></p>'+'</div></section>'+cta()
 write('/about/','About Caleb Foglesong & CDL Marketing','Meet CDL Marketing, part of CDL Management in Kirksville, Missouri. Marketing for flooring showrooms, from a team that operates flooring showrooms.',body,[{'@type':'Person','name':'Caleb Foglesong','jobTitle':'Owner','worksFor':{'@id':DOMAIN+'/#organization'}}])

def contact():
 body=subhero('Contact','Let’s talk about<br>your showroom.','A free review of your website and local online presence, with three priority opportunities to discuss.','/contact/')+'<section class="section" id="apply"><div class="wrap contact-grid"><div class="contact-intro"><h2>A useful conversation.<br>No pressure.</h2><p>Tell us your showroom, location and website. We look at how your store appears online, where a shopper may struggle and which three opportunities deserve attention first. There is no obligation to hire us.</p><p>Already spoken with our team? <a href="mailto:caleb@cdl1.net">Continue the conversation with Caleb</a> about your next step.</p><div class="contact-links"><a href="tel:+16606653889">(660) 665-3889</a><a href="mailto:caleb@cdl1.net">caleb@cdl1.net</a></div><p class="inline-note">CDL Management · Kirksville, Missouri</p><div class="callout"><h3>Want to start with a design?</h3><p>Our free homepage mockup gives you something concrete to look at before deciding.</p>'+link('/free-mockup/','Request a free homepage design')+'</div>'+switching_contact_note()+'</div>'+form()+'</div></section>'
 write('/contact/','Free Flooring Marketing Audit | Contact CDL Marketing','Request a free growth audit for your flooring showroom. Contact CDL Marketing at (660) 665-3889 or caleb@cdl1.net. No obligation.',body)

def legacy_pages():
 # Keep existing article bodies, publication dates and addresses. Refresh only shared presentation.
 for f in (LEGACY/'blog').glob('*/index.html'):
  slug=f.parent.name
  override=ROOT/'source/articles'/slug/'index.html'
  old=(override if override.exists() else f).read_text()
  title=re.search(r'<title>(.*?)</title>',old,re.S)[1]
  desc=re.search(r'<meta name="description" content="(.*?)"',old)[1]
  h1=re.search(r'<h1>(.*?)</h1>',old,re.S)[1]
  article=re.search(r'<article>(.*?)</article>',old,re.S)[1]
  article=re.sub(r'<p class="article-updated">.*?</p>','',article,count=1,flags=re.S)
  # Old article wrappers carried their own .wrap class. Keep prose, not old layout.
  article=article.replace('class="tbl"','class="tbl" role="region" aria-label="AI search comparison worksheet" tabindex="0"')
  article=article.replace('class="wrap prose"','class="prose"').replace('class="wrap article-body"','class="prose"')
  article=re.sub(r'<div class="wrap[^\"]*">','<div>',article)
  schemas=[]
  for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',old,re.S):
   obj=json.loads(raw)
   if obj.get('@type') in ['Article','FAQPage']:
    obj.pop('@context',None);schemas.append(obj)
  article_schema=next((x for x in schemas if x.get('@type')=='Article'),{})
  def display_date(value):
   return date.fromisoformat(value[:10]).strftime('%B %-d, %Y') if value else ''
  published=article_schema.get('datePublished','')
  modified=article_schema.get('dateModified','')
  meta='By Caleb Foglesong'
  if published: meta+=' · Published '+display_date(published)
  if modified and modified!=published: meta+=' · Updated '+display_date(modified)
  body=subhero('Showroom insights',h1,'Practical guidance from the CDL Marketing team.','/blog/'+slug+'/')+'<section class="section"><div class="wrap article-layout"><p class="article-meta">'+ESC(meta)+'</p>'+article+'<aside><b>About the author</b><p>Caleb Foglesong owns CDL Management. Our team operates flooring showrooms in Missouri and Illinois.</p><a href="/about/">Learn about CDL Marketing</a></aside><p><a href="/blog/">← All flooring marketing insights</a></p></div></section>'+cta()
  write('/blog/'+slug+'/',html.unescape(title),html.unescape(desc),body,schemas)
 write('/blog/','Flooring Marketing Insights | CDL Marketing','Practical guides to flooring store marketing, local SEO, Google Business Profile and AI search from a team that operates showrooms.',subhero('Insights','Notes from<br>the showroom.','Practical answers to the questions flooring store owners ask about search, websites, advertising and follow-up.','/blog/')+'<section class="section"><div class="wrap">'+articles_cards(True)+'</div></section>'+cta())
 old=(LEGACY/'privacy.html').read_text()
 legal=re.search(r'<div class="wrap legal">(.*?)</div>\s*</main>',old,re.S)[1]
 write('/privacy/','Privacy Policy | CDL Marketing','How CDL Marketing collects, uses and protects the information you send through cdlmanagement.com.',subhero('Privacy','Privacy policy','What we collect through this website, why, and what we do with it.','/privacy/')+'<section class="section"><div class="wrap article-layout">'+legal+'</div></section>')
 write('/free-mockup/','Free Homepage Design for Your Business | CDL Marketing','Get a free homepage mockup for your local business. No meeting required. Yours to keep, with no obligation. Request a design from CDL Marketing.',subhero('Free homepage design','See what your<br>website could be.','A free homepage mockup for your local business. No meeting required. Yours to keep whether we work together or not. We agree on the next step after reviewing your request.','/free-mockup/')+'<section class="section"><div class="wrap contact-grid"><div><h2>Something concrete.<br>Before you decide.</h2><p>Tell us your business name and website. We will review the basics, design a homepage mockup and follow up by email.</p><ol><li>Tell us about your business.</li><li>We prepare a homepage concept around your services and market.</li><li>You receive the design by email.</li></ol><p>We work with flooring stores, restoration companies, assisted living communities and other local businesses.</p><p>Questions? <a href="tel:+16606653889">Call (660) 665-3889</a>.</p></div>'+form('mockup')+'</div></section>')

def buyer_pages():
 write('/compare/broadlume/','CDL Marketing vs Broadlume | Flooring Agency Comparison','Compare CDL Marketing with Broadlume and Cyncly: services, published evidence, scope and questions to ask before choosing a flooring marketing provider.',subhero('Agency comparison','CDL and Broadlume.<br>Compare what fits.','Look at the work, evidence and terms behind each proposal.','/compare/broadlume/')+comparison_body()+cta())
 write('/guides/choosing-a-flooring-marketing-agency/','How to Choose a Flooring Marketing Agency | CDL Marketing','A practical checklist for flooring showroom owners comparing marketing agencies: scope, pricing, websites, data, proof and questions to ask.',subhero('Buyer’s guide','Choose an agency<br>with clear answers.','A practical checklist for independent flooring showroom owners.','/guides/choosing-a-flooring-marketing-agency/')+agency_guide_body()+cta())

def switching():
 write('/switch/','Switch Website Providers | Proposed CDL Transition Credits','Review proposed CDL website-service credits when switching from Broadlume or another provider. Eligibility, setup, paid marketing and credit terms need written approval.',subhero('Switching providers','Switch providers<br>with a clear plan.','Month-to-month marketing and proposed monthly website-service credits. Review both paths, then confirm your eligibility and terms in writing.','/switch/')+switch_page_body())

def main():
 home();services();pricing();about();contact();legacy_pages();buyer_pages();switching()
 not_found='<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found | CDL Marketing</title><link rel="stylesheet" href="/assets/site.css"><script src="/assets/site.js" defer></script></head><body>'+header()+'<main id="main" tabindex="-1"><section class="section"><div class="wrap narrow"><span class="eyebrow">Page not found</span><h1>Let’s get you back<br>to the showroom.</h1><p>That page is not available. You can explore our services or contact the team.</p><p><a class="btn" href="/">Go to the homepage</a></p><p><a href="/contact/">Contact CDL Marketing</a></p></div></section></main>'+footer()+'</body></html>'
 (ROOT/'404.html').write_text(not_found)
 ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns)
 root=ET.Element('{'+ns+'}urlset')
 for path in PAGES:
  item=ET.SubElement(root,'{'+ns+'}url');ET.SubElement(item,'{'+ns+'}loc').text=DOMAIN+path
 ET.ElementTree(root).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
 print(f'Built {len(PAGES)} public pages. No deployment performed.')

if __name__=='__main__':main()
