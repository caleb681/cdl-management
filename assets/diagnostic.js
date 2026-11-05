// This worksheet reads fixed choices only. It has no storage, tracking or network calls.
(() => {
  const root = document.querySelector('[data-diagnostic]');
  if (!root) return;
  const checks = [...root.querySelectorAll('[data-diagnostic-check]')];
  const summary = root.querySelector('[data-diagnostic-summary]');
  const title = root.querySelector('#discussion-title');
  const list = root.querySelector('[data-summary-list]');
  const intro = root.querySelector('[data-summary-intro]');
  const unknown = root.querySelector('[data-summary-unknown]');
  const show = () => {
    const flagged = checks.filter(check => check.querySelector('select').value === 'review');
    const unchecked = checks.filter(check => check.querySelector('select').value === 'unknown');
    list.replaceChildren();
    for (const check of flagged) {
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = check.querySelector('[data-check-link]').getAttribute('href');
      link.textContent = check.querySelector('select').dataset.checkTitle;
      item.append(link, document.createTextNode(': ' + check.querySelector('[data-check-action]').textContent));
      list.append(item);
    }
    intro.textContent = flagged.length
      ? 'You marked these items for a closer look. They appear in checklist order, not a measured ranking of importance.'
      : 'You have not marked any item for a closer look. This does not establish that your marketing is working; review what you have checked and any unknowns.';
    list.hidden = flagged.length === 0;
    unknown.textContent = unchecked.length
      ? 'Still to check: ' + unchecked.map(check => check.querySelector('select').dataset.checkTitle).join('; ') + '.'
      : 'No items are marked “Not checked / not sure.” Bring the evidence behind your observations to the conversation.';
    summary.hidden = false;
    title.focus();
  };
  root.querySelector('[data-build-review]').addEventListener('click', show);
  root.querySelector('[data-clear-review]').addEventListener('click', () => {
    for (const check of checks) check.querySelector('select').value = 'unknown';
    summary.hidden = true;
    list.replaceChildren();
    checks[0].querySelector('select').focus();
  });
  // Hide an old summary whenever a selection changes; no stale result is shown.
  for (const check of checks) check.querySelector('select').addEventListener('change', () => { summary.hidden = true; });
  root.querySelector('[data-print-review]').addEventListener('click', () => window.print());
  root.querySelector('[data-diagnostic-tools]').hidden = false;
})();
