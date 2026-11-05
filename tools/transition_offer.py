"""Proposed switching support, centralized for the unpublished owner review.

These are website-service credits, not cash or payment of another provider.
Eligibility, fees, limits and written approval remain necessary before use.
"""

MARKETING_HEADLINE = 'No long-term marketing contract'
MARKETING_SUMMARY = ('Month-to-month SEO and advertising for independent flooring '
                     'showrooms across the United States. We agree the work, fees and cancellation notice '
                     'in writing before starting.')
CREDIT_NOTICE = ('Proposed monthly website-service credits; setup and marketing/ad spend '
                 'quoted separately.')
APPROVAL_NOTICE = ('No credit is automatically granted. Eligibility, dates and '
                   'limits need review and written approval before work begins.')
REQUEST_NOTICE = ('Proposed transition credit requests are reviewed separately; '
                  'submitting does not activate or approve an offer.')
PROVIDER_NOTICE = ('Credits apply to monthly CDL website-service fees only. They are not '
                   'cash, a refund or payment of another provider’s charges. You '
                   'remain responsible for your existing agreement and any '
                   'cancellation or early-exit fees.')

TRANSITION_PATHS = [
    {
        'title': 'SEO + advertising with CDL',
        'headline': 'No monthly CDL website fee during your approved credit period.',
        'detail': ('When you purchase both paid CDL SEO and advertising management, '
                   'we propose monthly website-service credits through the end of your '
                   'reviewed existing website contract. The maximum free period, '
                   'start date, setup treatment and credit cap are not finalized.'),
    },
    {
        'title': 'Website only',
        'headline': 'Up to 3 months with no monthly website-service fee.',
        'detail': ('A proposed transition credit toward monthly CDL website-service fees '
                   'when you move your website. The approved period may be shorter '
                   'than three months. Eligibility, start date, setup treatment '
                   'and the credit cap still need to be agreed.'),
    },
]

OPEN_TERMS = [
    ('Eligibility and current agreement',
     'Which existing providers and agreements qualify, what evidence is needed, '
     'and the actual end date, renewal and cancellation requirements. Broadlume '
     'and other providers can be reviewed; no provider’s customers automatically qualify.'),
    ('Paid marketing and advertising budget',
     'The SEO scope and fee, advertising-management scope and fee, and media budget '
     'as separate items. Buying ad spend alone does not establish eligibility for '
     'the SEO + advertising path.'),
    ('Maximum combined-service free period',
     'The maximum website-credit period when buying SEO + advertising, even if the '
     'existing website agreement runs longer. No unlimited free period is approved.'),
    ('Start date',
     'When credits begin, when the website and marketing start, and how those '
     'dates relate to the existing contract end date.'),
    ('Setup fee',
     'Whether setup is payable, reduced or credited. The recommended standalone '
     'website plan’s setup fee is not automatically waived by either proposal.'),
    ('Credit cap and application',
     'The maximum total credit and the CDL website-service invoices it can cover. '
     'No cash value, automatic reimbursement or payment to the old provider is offered.'),
    ('Cancellation and credits',
     'The written notice required for month-to-month marketing and the effect of '
     'ending SEO, ad management or website service during a credit period. No '
     'transition-specific cancellation charge or repayment rule is approved here.'),
    ('Combining offers',
     'Whether a transition credit can be combined with another discount or offer. '
     'Combining offers is not automatic.'),
]

MARKETING_FAQ = (
    'What does no long-term marketing contract mean?',
    f'{MARKETING_SUMMARY} Month-to-month does not remove the need for an agreement '
    'or cancel your current provider’s contract. Website-only plan terms and any '
    'approved switching credits are recorded separately. '
    '<a href="/switch/">Review the proposed switching support.</a>'
)


def marketing_scope_note():
    return (f'<div class="callout"><span class="eyebrow">Month-to-month marketing</span>'
            f'<h2>{MARKETING_HEADLINE}.</h2><p>{MARKETING_SUMMARY}</p>'
            '<p>SEO and advertising-management fees are quoted for your scope. '
            'Advertising spend is separate and paid to the platforms. '
            'CRM integration is planned for later.</p></div>')


def transition_cards(contact=False):
    target = '/contact/#switching' if contact else '/switch/'
    label = 'Discuss this path' if contact else 'Review eligibility and open terms'
    cards = ''.join(
        f'<article class="service-card"><span class="eyebrow">Proposed transition offer</span>'
        f'<h3>{path["title"]}</h3><p><strong>{path["headline"]}</strong></p>'
        f'<p>{path["detail"]}</p><a class="text-link" href="{target}">{label} '
        '<span aria-hidden="true">→</span></a></article>'
        for path in TRANSITION_PATHS
    )
    return f'<div class="cards two-cards">{cards}</div>'


def transition_preview(contact=False):
    """A complete, visibly proposed summary usable on the main buying pages."""
    terms_target = '#open-terms' if contact else '/switch/'
    return (f'<div class="section-heading"><span class="eyebrow">Proposed switching support</span>'
            '<h2>Already paying for a website?</h2><p>Let’s review a move from '
            'Broadlume or another provider around your actual agreement.</p>'
            f'<p><strong>{CREDIT_NOTICE}</strong></p></div>{transition_cards(contact=contact)}'
            f'<p class="inline-note">{APPROVAL_NOTICE} {PROVIDER_NOTICE} '
            f'<a href="{terms_target}">See the switching steps and terms still to agree.</a></p>')


def switching_contact_note():
    return (f'<section class="callout" id="switching"><h3>Thinking about switching providers?</h3>'
            '<p>Use this inquiry form to start a conversation. Tell us your current '
            'provider and expected contract end date when we follow up. Choose the '
            'matching switching option under Biggest goal. No contract '
            'upload is needed here; do not send passwords or account credentials.</p>'
            f'<p><strong>{CREDIT_NOTICE}</strong> {REQUEST_NOTICE}</p>'
            '<p>Sending a request does not cancel an agreement or authorize a transfer. '
            '<a href="/switch/">Review both proposed paths first.</a></p></section>')


def switch_page_body():
    terms = ''.join(f'<li><strong>{title}:</strong> {detail}</li>' for title, detail in OPEN_TERMS)
    return (f'<section class="section"><div class="wrap">{transition_preview(contact=True)}'
            f'{marketing_scope_note()}'
            '</div></section>'
            '<section class="section light" id="review"><div class="wrap article-layout">'
            '<span class="eyebrow">Start with the actual agreement</span>'
            '<h2>A clear move starts with a review.</h2>'
            '<p>The review can cover Broadlume or another website provider. We need '
            'to understand what you have, what you can move and what you still owe. '
            'We do not assume every provider uses the same contract or that every '
            'website, catalog or tool can be transferred.</p>'
            '<ul><li>Your current provider, services and known contract end date.</li>'
            '<li>The applicable agreement, renewal and cancellation requirements, '
            'with private information redacted if documents are later requested.</li>'
            '<li>Who controls your domain, hosting, content and accounts, and which '
            'tools or licenses need replacing.</li><li>The important URLs, inquiry '
            'destinations and tracking that must survive the move.</li></ul>'
            '<p>No file upload is required to ask about switching. Start with a '
            '<a href="/contact/#switching">conversation about your current website</a>. '
            'Review is not approval of a credit or a legal interpretation of your agreement.</p>'
            '</div></section>'
            '<section class="section"><div class="wrap article-layout">'
            '<span class="eyebrow">A controlled handover</span><h2>Four steps to switching.</h2>'
            '<ol><li><h3>Review the existing agreement.</h3><p>Confirm the provider, '
            'end date, notice, access and transfer rights before proposing a date. '
            'Keep the current website and inquiry paths working.</p></li>'
            '<li><h3>Approve the scope and credits.</h3><p>Agree the website, any '
            'paid marketing, separate media budget and exact eligibility, credit '
            'period, setup fee and cancellation terms in writing. No credit is '
            'granted just by making an inquiry.</p></li>'
            '<li><h3>Build and verify.</h3><p>Prepare the new site, inventory '
            'important URLs, review redirects and test pages, inquiry delivery '
            'and agreed tracking. Get approval of the exact build.</p></li>'
            '<li><h3>Control the cutover.</h3><p>Agree who changes what and when, '
            'verify the new site and contact paths, and retain a rollback plan. '
            'You handle existing-provider cancellation under your agreement. '
            'We do not cancel accounts or move domains without authorization.</p></li></ol>'
            '</div></section>'
            '<section class="section light" id="open-terms"><div class="wrap article-layout">'
            '<span class="eyebrow">Proposed, with terms still open</span>'
            '<h2>What we must agree before offering a credit.</h2>'
            f'<p><strong>{CREDIT_NOTICE}</strong> {APPROVAL_NOTICE}</p>'
            f'<ul>{terms}</ul><p>{PROVIDER_NOTICE}</p>'
            '<p>Our <a href="/pricing/">recommended standalone website plan</a> '
            'remains a separate proposal. Transition credits do not silently '
            'replace its setup, payment, scope or handover terms. No ranking, '
            'AI recommendation, lead count or sales result is promised.</p>'
            '<p><a class="btn" href="/contact/#switching">Discuss my switch '
            '<span aria-hidden="true">→</span></a></p></div></section>')
