/* Optional Meta measurement. No GA4 property is configured.
   Form delivery is independent of this browser-only preference. */
(function () {
  'use strict';
  var PIXEL_ID = '1792164632076086';
  var STORAGE_KEY = 'cdl-privacy-choice-v1';
  var MAX_AGE = 180 * 24 * 60 * 60 * 1000;
  var choice = null, failed = false, storageFailed = false;
  var injected = false, ready = false, pageViewSent = false;
  var reloadNeeded = false, revoked = false, offStateSaved = false, trackedForms = Object.create(null);
  var allowButtons = [], declineButtons = [], reloadButtons = [], statuses = [];
  window.cdlTrackLead = function () { return false; };

  function preview() {
    var host = location.hostname;
    return host === 'localhost' || host === '127.0.0.1' || host === '[::1]' ||
      host === '::1' || /\.localhost$/.test(host) ||
      document.documentElement.getAttribute('data-cdl-preview') === 'true';
  }
  function privacySignal() {
    return navigator.globalPrivacyControl === true || String(navigator.doNotTrack) === '1' ||
      String(navigator.msDoNotTrack) === '1' || String(window.doNotTrack) === '1';
  }
  function readChoice() {
    var raw;
    try { raw = window.localStorage.getItem(STORAGE_KEY); }
    catch (_) {
      failed = true; storageFailed = true;
      try { window.localStorage.removeItem(STORAGE_KEY); offStateSaved = true; }
      catch (_) { offStateSaved = false; }
      return null;
    }
    if (!raw) { offStateSaved = true; return null; }
    try {
      var saved = JSON.parse(raw), now = Date.now();
      if (saved.version !== 1 || !['allow', 'decline'].includes(saved.choice) ||
          !Number.isFinite(saved.savedAt) || saved.savedAt > now || now - saved.savedAt >= MAX_AGE) { offStateSaved = true; return null; }
      offStateSaved = saved.choice === 'decline';
      return saved.choice;
    } catch (_) { offStateSaved = true; return null; }
  }
  function remember(value) {
    choice = value;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify({version: 1, choice: value, savedAt: Date.now()}));
      offStateSaved = value === 'decline';
      return true;
    } catch (_) {
      failed = true; storageFailed = true;
      try { window.localStorage.removeItem(STORAGE_KEY); offStateSaved = true; }
      catch (_) { offStateSaved = false; }
      return false;
    }
  }
  function permitted() {
    return !failed && !reloadNeeded && !preview() && !privacySignal() && choice === 'allow';
  }
  function suspend() {
    if (injected) reloadNeeded = true;
    // Defensive only: revoke cannot unload a script or recall prior data.
    if (ready && !revoked && typeof window.fbq === 'function') {
      revoked = true;
      try { window.fbq('consent', 'revoke'); } catch (_) {}
    }
  }
  function render() {
    var signal = privacySignal(), local = preview(), allowed = permitted(), message;
    if (local) message = 'Advertising measurement is off in this preview.';
    else if (signal) message = 'Advertising measurement is off because your browser signals a privacy preference.';
    else if (storageFailed) message = 'Your browser did not let us save your choice. Advertising measurement is off on this page; your forms still work. Check your browser settings before relying on a saved choice on another page.';
    else if (failed) message = 'Advertising measurement could not be enabled and is off on this page. Your forms still work.';
    else if (choice === 'decline') message = 'Advertising measurement is off. You can still use the site and submit a request.';
    else if (allowed && ready) message = 'Advertising measurement is allowed in this browser. You can turn it off here.';
    else if (allowed) message = 'Your choice is saved. Optional advertising measurement is loading; your forms still work.';
    else message = 'Optional advertising measurement is off until you allow it. You can use the site and forms without allowing it.';
    var canReloadOff = offStateSaved || signal || local;
    if (reloadNeeded) {
      message += ' The Meta script was already requested on this page. We have stopped requesting new measurement events, but cannot remove an active script or retract data already sent.';
      message += canReloadOff ? ' Copy or finish any form details before choosing Reload to apply fully.' : ' We could not remember an off choice, so Reload to apply fully is unavailable. Resolve browser storage and save a declined choice before relying on another page to keep measurement off. Your form details remain here.';
    }
    statuses.forEach(function (element) { element.textContent = message; });
    allowButtons.forEach(function (button) { button.disabled = signal || local || failed || reloadNeeded; });
    declineButtons.forEach(function (button) { button.disabled = false; });
    reloadButtons.forEach(function (button) { button.hidden = !reloadNeeded; button.disabled = !canReloadOff; });
  }
  function failClosed() {
    failed = true; suspend(); remember('decline');
    try { render(); } catch (_) {}
  }
  function startPixel() {
    if (injected || !permitted()) return;
    if (typeof window.fbq !== 'function') {
      var fbq = function () {
        if (fbq.callMethod) fbq.callMethod.apply(fbq, arguments);
        else fbq.queue.push(arguments);
      };
      fbq.push = fbq; fbq.loaded = true; fbq.version = '2.0'; fbq.queue = [];
      window.fbq = fbq;
      if (!window._fbq) window._fbq = fbq;
    }
    var script = document.createElement('script');
    script.async = true; script.src = 'https://connect.facebook.net/en_US/fbevents.js';
    script.setAttribute('data-cdl-meta', '');
    script.onload = function () {
      try {
        // Never queue events while loading; recheck a racing withdrawal first.
        choice = readChoice();
        if (!permitted()) { suspend(); render(); return; }
        window.fbq('init', PIXEL_ID); ready = true;
        if (!pageViewSent) { pageViewSent = true; window.fbq('track', 'PageView'); }
        render();
      } catch (_) { failClosed(); }
    };
    script.onerror = failClosed;
    injected = true;
    document.head.appendChild(script);
  }
  function refresh(load) {
    choice = readChoice();
    if (!permitted()) suspend();
    else if (load) startPixel();
    render();
  }
  try {
    var controls = document.querySelector('#privacy-choices');
    if (!controls) return;
    allowButtons = Array.from(controls.querySelectorAll('[data-privacy-choice="allow"]'));
    declineButtons = Array.from(controls.querySelectorAll('[data-privacy-choice="decline"]'));
    reloadButtons = Array.from(controls.querySelectorAll('[data-privacy-reload]'));
    statuses = Array.from(controls.querySelectorAll('[data-privacy-status]'));
    if (!allowButtons.length || !declineButtons.length || !statuses.length) return;
    allowButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        try {
          if (failed || reloadNeeded || privacySignal() || preview()) { render(); return; }
          if (remember('allow')) refresh(true); else failClosed();
        } catch (_) { failClosed(); }
      });
    });
    declineButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        try { choice = 'decline'; suspend(); remember('decline'); render(); }
        catch (_) { failClosed(); }
      });
    });
    reloadButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        // An explicit visitor action only; declining never reloads a form.
        try {
          if (!reloadNeeded) return;
          remember('decline');
          if (offStateSaved || privacySignal() || preview()) location.reload();
          else render();
        } catch (_) { failClosed(); }
      });
    });
    window.cdlTrackLead = function (formName) {
      try {
        refresh(false);
        if (!permitted() || !ready || trackedForms[formName] ||
            !['Growth Audit', 'Free Mockup'].includes(formName)) return false;
        trackedForms[formName] = true;
        window.fbq('track', 'Lead', {content_name: formName});
        return true;
      } catch (_) { failClosed(); return false; }
    };
    window.addEventListener('storage', function (event) {
      if (event.key === STORAGE_KEY || event.key === null) {
        try { refresh(true); } catch (_) { failClosed(); }
      }
    });
    window.addEventListener('pageshow', function () { try { refresh(true); } catch (_) { failClosed(); } });
    window.addEventListener('focus', function () { try { refresh(true); } catch (_) { failClosed(); } });
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden) { try { refresh(true); } catch (_) { failClosed(); } }
    });
    refresh(true);
  } catch (_) { failClosed(); }
})();
