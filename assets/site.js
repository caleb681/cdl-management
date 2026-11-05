/* Navigation is optional; all content and links remain in HTML. */
const toggle = document.querySelector('.menu-toggle');
const mobile = document.querySelector('.mobile-nav');
function closeMobileMenu() {
  if (!mobile) return;
  mobile.hidden = true;
  toggle?.setAttribute('aria-expanded', 'false');
}
toggle?.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open)); mobile.hidden = !open;
});
document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  const serviceMenu = document.querySelector('.nav-services[open]');
  if (serviceMenu) { serviceMenu.open = false; serviceMenu.querySelector('summary').focus(); }
  if (mobile && !mobile.hidden) { closeMobileMenu(); toggle.focus(); }
});
mobile?.addEventListener('click', e => {
  if (e.target.closest('a')) closeMobileMenu();
});
window.matchMedia('(min-width: 821px)').addEventListener('change', e => {
  if (!e.matches) return;
  const moveFocus = mobile?.contains(document.activeElement);
  closeMobileMenu();
  if (moveFocus) document.querySelector('.site-header .brand')?.focus();
});
document.addEventListener('click', e => {
  const menu = document.querySelector('.nav-services[open]');
  if (menu && !menu.contains(e.target)) menu.open = false;
});

for (const form of document.querySelectorAll('[data-lead-form]')) {
  const status = form.querySelector('[role=status]');
  const button = form.querySelector('[type=submit]');
  let busy = false, complete = false, uncertain = false;
  const requiredInputs = [...form.querySelectorAll('input[required]')];
  for (const input of requiredInputs) input.addEventListener('input', () => input.setCustomValidity(''));
  // The HTML button starts disabled, so a missing script cannot submit details in a URL.
  button.disabled = false;
  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (busy || complete || uncertain) return;
    for (const input of requiredInputs) input.setCustomValidity(input.value.trim() ? '' : 'Please enter a value.');
    if (!form.reportValidity()) return;
    const values = Object.fromEntries([...new FormData(form)].map(([name, value]) => [name, String(value).trim()]));
    if (values.company_website_hp) return;
    busy = true; button.disabled = true; button.textContent = 'Sending…';
    form.setAttribute('aria-busy', 'true'); status.textContent = '';
    const kind = form.dataset.leadForm;
    const payload = kind === 'audit' ? {
      _subject: 'New CDL application: ' + values.showroom,
      name: values.name, showroom: values.showroom, city: values.city,
      email: values.email, phone: values.phone, website: values.website,
      monthly_revenue: values.revenue, biggest_goal: values.goal
    } : {
      business_name: values.showroom, name: values.name, contact_name: values.name,
      email: values.email, phone: values.phone, website: normalizeWebsite(values.website),
      vertical: values.vertical, source: 'free-mockup', company_website_hp: ''
    };
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 18000);
    try {
      const response = await fetch(kind === 'audit' ? 'https://formsubmit.co/ajax/caleb@cdl1.net' : '/api/intake', {
        method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},
        body:JSON.stringify(payload),signal:controller.signal
      });
      if (!response.ok) {
        // Explicit rejection is recoverable even when a provider returns an HTML error page.
        // A server/network failure may have saved the request, so it remains uncertain.
        if ([400,401,403,404,405,422,429].includes(response.status)) throw new Error('rejected');
        throw new Error('uncertain');
      }
      let result; try { result = await response.json(); } catch { throw new Error('uncertain'); }
      const acknowledged = kind === 'audit' ? result?.success === true || result?.success === 'true' : result?.ok === true;
      if (!acknowledged) throw new Error('uncertain');
      complete = true;
      form.querySelector('.form-fields').hidden = true;
      status.classList.add('form-success');
      status.textContent = kind === 'audit' ? 'Your application was accepted. We’ll review your showroom and contact you about the next step. You can also call (660) 665-3889.' : 'Your design request was accepted. We’ll review your business and follow up by email. You can also call (660) 665-3889.';
      status.tabIndex = -1; status.focus();
      try { window.cdlTrackLead?.(kind === 'audit' ? 'Growth Audit' : 'Free Mockup'); } catch {}
    } catch(error) {
      uncertain = error.message !== 'rejected';
      status.textContent = uncertain ? 'We could not confirm delivery. Your request may have arrived. Please call (660) 665-3889 or email caleb@cdl1.net before sending again. Your details remain here.' : 'Your request was not accepted. Check your details or try again later. You can also call (660) 665-3889 or email caleb@cdl1.net. Your details remain here.';
      button.disabled = uncertain; button.textContent = uncertain ? 'Delivery unconfirmed' : 'Send request';
      status.tabIndex = -1; status.focus();
    } finally { clearTimeout(timer); busy = false; form.removeAttribute('aria-busy'); }
  });
}
function normalizeWebsite(value) {
  const text = String(value || '').trim();
  if (!text) return '';
  return /^https?:\/\//i.test(text) ? text : 'https://' + text.replace(/^\/+/, '');
}
