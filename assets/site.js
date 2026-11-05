/* Navigation is optional; all content and links remain in HTML. */
const toggle = document.querySelector('.menu-toggle');
const mobile = document.querySelector('.mobile-nav');
const disclosure = document.querySelector('.mobile-disclosure');
function closeMobileMenu() {
  if (disclosure) disclosure.open = false;
}
document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  const serviceMenu = document.querySelector('.nav-services[open]');
  if (serviceMenu) { serviceMenu.open = false; serviceMenu.querySelector('summary').focus(); }
  if (disclosure?.open) { closeMobileMenu(); toggle.focus(); }
});
mobile?.addEventListener('click', e => {
  if (e.target.closest('a')) closeMobileMenu();
});
window.matchMedia('(min-width: 821px)').addEventListener('change', e => {
  if (!e.matches) return;
  const moveFocus = disclosure?.contains(document.activeElement);
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
  const fields = form.querySelector('.form-fields');
  const website = form.querySelector('[name=website]');
  let busy = false, complete = false, uncertain = false, offlineWarning = false;
  const requiredInputs = [...form.querySelectorAll('input[required]')];
  for (const input of requiredInputs) input.addEventListener('input', () => input.setCustomValidity(''));
  website?.addEventListener('input', () => website.setCustomValidity(''));
  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (busy || complete || uncertain) return;
    for (const input of requiredInputs) input.setCustomValidity(input.value.trim() ? '' : 'Please enter a value.');
    if (website) website.setCustomValidity(validWebsite(website.value) ? '' : 'Enter a website address such as yourshowroom.com, or leave this optional field blank.');
    if (!form.reportValidity()) return;
    const values = Object.fromEntries([...new FormData(form)].map(([name, value]) => [name, String(value).trim()]));
    if (values.company_website_hp) return;
    // Connectivity hints can be wrong. Warn before making any request, but let
    // the visitor explicitly attempt sending anyway instead of trapping them.
    if (navigator.onLine === false && !offlineWarning) {
      offlineWarning = true;
      showFormStatus(status, 'Your browser reports no connection. We have not sent your request. Reconnect and send, or choose Try sending anyway if your connection is working. Your details remain here.');
      button.textContent = 'Try sending anyway';
      return;
    }
    offlineWarning = false;
    busy = true; button.disabled = true; button.textContent = 'Sending…';
    status.textContent = 'Sending your request. Please wait.';
    status.tabIndex = -1; status.focus();
    fields.disabled = true;
    fields.setAttribute('aria-busy', 'true');
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
        if ([400,401,403,404,405,413,415,422,429].includes(response.status) || (kind === 'mockup' && response.status === 408)) throw new Error('rejected');
        throw new Error('uncertain');
      }
      let result; try { result = await response.json(); } catch { throw new Error('uncertain'); }
      const acknowledged = kind === 'audit' ? result?.success === true || result?.success === 'true' : result?.ok === true;
      if (!acknowledged) throw new Error('uncertain');
      const duplicate = kind === 'mockup' && result.duplicate === true;
      complete = true;
      fields.hidden = true;
      status.classList.add('form-success');
      showFormStatus(status, duplicate ? 'We already received this design request. There is no need to send it again. Contact us below if you need to correct anything.' : kind === 'audit' ? 'Your application was accepted. We’ll review your showroom and contact you about the next step.' : 'Your design request was accepted. We’ll review your business and follow up by email.');
      if (!duplicate) try { window.cdlTrackLead?.(kind === 'audit' ? 'Growth Audit' : 'Free Mockup'); } catch {}
    } catch(error) {
      uncertain = error.message !== 'rejected';
      showFormStatus(status, uncertain ? 'We could not confirm delivery. Your request may have arrived. Please call or email us before sending again. Your details remain here.' : 'Your request was not accepted. Check your details or try again later, or contact us below. Your details remain here.');
      button.disabled = uncertain; button.textContent = uncertain ? 'Delivery unconfirmed' : 'Send request';
    } finally { clearTimeout(timer); busy = false; fields.disabled = false; fields.removeAttribute('aria-busy'); }
  });
  // Enable only after the handler is ready; the initial HTML remains usable if
  // this script is delayed or missing, without submitting details into a URL.
  button.disabled = false;
  form.querySelector('.form-fallback').hidden = true;
}
function showFormStatus(status, message) {
  status.textContent = message;
  const recovery = document.createElement('span');
  recovery.className = 'form-recovery';
  for (const [href, label] of [['tel:+16606653889', 'Call (660) 665-3889'], ['mailto:caleb@cdl1.net', 'Email caleb@cdl1.net']]) {
    const link = document.createElement('a');
    link.href = href; link.textContent = label; recovery.append(link);
  }
  status.append(recovery);
  status.tabIndex = -1; status.focus();
}
function normalizeWebsite(value) {
  const text = String(value || '').trim();
  if (!text) return '';
  return /^https?:\/\//i.test(text) ? text : 'https://' + text.replace(/^\/+/, '');
}
function validWebsite(value) {
  const text = String(value || '').trim();
  if (!text) return true;
  if (/[\u0000-\u0020\u007f]/.test(text)) return false;
  if (/^[a-z][a-z0-9+.-]*:\/\//i.test(text) && !/^https?:\/\//i.test(text)) return false;
  try {
    const url = new URL(normalizeWebsite(text));
    return ['http:', 'https:'].includes(url.protocol) && Boolean(url.hostname) && !url.username && !url.password;
  } catch { return false; }
}
