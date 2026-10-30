/* CDL Marketing site tracking, loaded on every public page.
   Meta Pixel: "Correct - CDL Marketing" (dataset 1792164632076086, CDL Management business).
   GA4: add the gtag snippet here once the property exists, so every page picks it up.
   Forms call window.cdlTrackLead(name) after a successful submit. */
(function () {
  var PIXEL_ID = '1792164632076086';
  !function (f, b, e, v, n, t, s) {
    if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
    if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = [];
    t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
  }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
  window.fbq('init', PIXEL_ID);
  window.fbq('track', 'PageView');

  window.cdlTrackLead = function (formName) {
    try { window.fbq('track', 'Lead', { content_name: formName }); } catch (e) {}
  };
})();
