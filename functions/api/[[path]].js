/**
 * CDL Command Center — Backend API
 * Cloudflare Pages Functions catch-all: /api/*
 *
 * Runtime: Cloudflare Workers (Web APIs only — no Node built-ins).
 *
 * Bindings expected on context.env:
 *   DB                  D1 database ("cdl-command")
 *   SESSION_SECRET      HMAC secret for session cookies + OTP hashing
 *   RESEND_API_KEY      Resend transactional email key (optional)
 *   BREAK_GLASS_PASSWORD  Shared emergency password (optional)
 *   WEBHOOK_SECRET      Shared secret for /webhooks/* and /digest
 *   ALERT_EMAIL         Where hot-lead alerts go (default caleb@cdl1.net)
 *   FROM_EMAIL          Resend "from" (default CDL Command <command@cdlmanagement.com>)
 */

/* ------------------------------------------------------------------ *
 * Constants
 * ------------------------------------------------------------------ */

const DEFAULT_ALERT_EMAIL = 'caleb@cdl1.net';
const DEFAULT_FROM_EMAIL = 'CDL Command <command@cdlmanagement.com>';
const SESSION_COOKIE = 'cdl_session';
const SESSION_DAYS = 30;
const OTP_TTL_MS = 10 * 60 * 1000;
const OTP_MAX_ATTEMPTS = 5;
const DEFAULT_GOAL_CLOSES = 20;

const NO_DB_MESSAGE =
  "Database not connected. Bind D1 database 'cdl-command' as DB in Cloudflare Pages settings.";

const TIER_ORDER_SQL = `CASE l.tier
  WHEN 'Hot' THEN 0
  WHEN 'Engaged' THEN 1
  WHEN 'Call Booked' THEN 2
  WHEN 'Cold' THEN 3
  ELSE 4 END`;

const LEAD_WRITE_FIELDS = [
  'business_name', 'vertical', 'contact_name', 'address', 'city', 'state', 'zip',
  'phone', 'email', 'website', 'tier', 'owner_id', 'source', 'dnc',
  'mockup_status', 'brief_status', 'strike_owner_id', 'smartlead_id',
];

const LEAD_PATCH_FIELDS = [
  'contact_name', 'address', 'city', 'state', 'zip', 'phone', 'email', 'website',
  'tier', 'owner_id', 'mockup_status', 'brief_status', 'strike_owner_id', 'dnc',
  'vertical', 'business_name',
];

const IMPORT_FIELDS = [
  'business_name', 'vertical', 'contact_name', 'address', 'city', 'state', 'zip',
  'phone', 'email', 'website', 'source',
];

const ONBOARDING_TEMPLATE = [
  ['Kickoff call + collect access (GBP, site, ad accounts)', 2, 1],
  ['Confirm qualified-lead definition in writing', 2, 2],
  ['Spin up CRM from snapshot + connect tracking', 5, 3],
  ['Google Business Profile audit + optimization', 5, 4],
  ['Launch ads (3 Meta + 1 Google)', 10, 5],
  ['Publish on-page SEO/GEO fixes', 10, 6],
  ['Turn on lead automations + missed-call text-back', 10, 7],
  ['Verify leads flowing + send first report + set monthly cadence', 14, 8],
];

/* ------------------------------------------------------------------ *
 * Tiny helpers
 * ------------------------------------------------------------------ */

function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store',
      ...extraHeaders,
    },
  });
}

function nowIso() {
  return new Date().toISOString();
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function currentMonth() {
  return new Date().toISOString().slice(0, 7); // YYYY-MM
}

function addDaysIso(days) {
  return new Date(Date.now() + days * 86400000).toISOString();
}

async function readJson(request) {
  try {
    const text = await request.text();
    if (!text) return {};
    return JSON.parse(text);
  } catch {
    return {};
  }
}

function str(v) {
  return v === undefined || v === null ? '' : String(v).trim();
}

function digitsOnly(v) {
  return str(v).replace(/\D+/g, '');
}

function escapeHtml(v) {
  return str(v)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function intOr(v, fallback) {
  const n = parseInt(v, 10);
  return Number.isFinite(n) ? n : fallback;
}

function numOr(v, fallback) {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
}

/* ------------------------------------------------------------------ *
 * Crypto helpers (Web Crypto only)
 * ------------------------------------------------------------------ */

const enc = new TextEncoder();
const dec = new TextDecoder();

function bytesToB64url(bytes) {
  let bin = '';
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function b64urlToBytes(s) {
  let t = String(s).replace(/-/g, '+').replace(/_/g, '/');
  while (t.length % 4 !== 0) t += '=';
  const bin = atob(t);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function b64urlEncode(text) {
  return bytesToB64url(enc.encode(text));
}

function b64urlDecode(text) {
  return dec.decode(b64urlToBytes(text));
}

function bytesToHex(buffer) {
  const bytes = new Uint8Array(buffer);
  let hex = '';
  for (let i = 0; i < bytes.length; i++) hex += bytes[i].toString(16).padStart(2, '0');
  return hex;
}

async function sha256hex(text) {
  const digest = await crypto.subtle.digest('SHA-256', enc.encode(text));
  return bytesToHex(digest);
}

async function hmacKey(secret) {
  return crypto.subtle.importKey(
    'raw',
    enc.encode(String(secret || '')),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign', 'verify'],
  );
}

async function hmacSign(payloadB64, secret) {
  const key = await hmacKey(secret);
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(payloadB64));
  return bytesToB64url(new Uint8Array(sig));
}

async function hmacVerify(payloadB64, signatureB64, secret) {
  try {
    const key = await hmacKey(secret);
    return await crypto.subtle.verify(
      'HMAC',
      key,
      b64urlToBytes(signatureB64),
      enc.encode(payloadB64),
    );
  } catch {
    return false;
  }
}

/** Constant-time-ish string compare. */
function safeEqual(a, b) {
  const x = String(a || '');
  const y = String(b || '');
  if (x.length !== y.length) return false;
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x.charCodeAt(i) ^ y.charCodeAt(i);
  return diff === 0;
}

function randomCode6() {
  const buf = new Uint32Array(1);
  crypto.getRandomValues(buf);
  return String(buf[0] % 1000000).padStart(6, '0');
}

/* ------------------------------------------------------------------ *
 * Session / auth
 * ------------------------------------------------------------------ */

function parseCookies(request) {
  const header = request.headers.get('Cookie') || '';
  const out = {};
  for (const part of header.split(';')) {
    const idx = part.indexOf('=');
    if (idx === -1) continue;
    const k = part.slice(0, idx).trim();
    const v = part.slice(idx + 1).trim();
    if (k) out[k] = v;
  }
  return out;
}

async function makeSessionToken(userId, secret) {
  const exp = Date.now() + SESSION_DAYS * 86400000;
  const payload = b64urlEncode(JSON.stringify({ uid: userId, exp }));
  const sig = await hmacSign(payload, secret);
  return `${payload}.${sig}`;
}

function sessionCookieHeader(token) {
  const maxAge = SESSION_DAYS * 86400;
  return `${SESSION_COOKIE}=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${maxAge}`;
}

function clearCookieHeader() {
  return `${SESSION_COOKIE}=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0`;
}

function publicUser(u) {
  if (!u) return null;
  return { id: u.id, name: u.name, email: u.email, role: u.role };
}

/** Parse + verify the session cookie and load the active user. Null if invalid. */
async function getUser(context) {
  const { request, env } = context;
  if (!env || !env.DB) return null;
  const token = parseCookies(request)[SESSION_COOKIE];
  if (!token || token.indexOf('.') === -1) return null;

  const dot = token.lastIndexOf('.');
  const payloadB64 = token.slice(0, dot);
  const sigB64 = token.slice(dot + 1);
  if (!payloadB64 || !sigB64) return null;

  const ok = await hmacVerify(payloadB64, sigB64, env.SESSION_SECRET);
  if (!ok) return null;

  let payload;
  try {
    payload = JSON.parse(b64urlDecode(payloadB64));
  } catch {
    return null;
  }
  if (!payload || !payload.uid) return null;
  if (!payload.exp || Date.now() > Number(payload.exp)) return null;

  const user = await env.DB.prepare(
    'SELECT * FROM users WHERE id = ? AND active = 1',
  ).bind(payload.uid).first();

  return user || null;
}

async function loginResponse(env, user) {
  const token = await makeSessionToken(user.id, env.SESSION_SECRET);
  return json({ user: publicUser(user) }, 200, { 'Set-Cookie': sessionCookieHeader(token) });
}

/* ------------------------------------------------------------------ *
 * Email
 * ------------------------------------------------------------------ */

function fromEmail(env) {
  return env.FROM_EMAIL || DEFAULT_FROM_EMAIL;
}

function alertEmail(env) {
  return env.ALERT_EMAIL || DEFAULT_ALERT_EMAIL;
}

/** Send through Resend. Never throws — returns {sent, error?}. */
async function sendEmail(env, { to, subject, html }) {
  if (!env.RESEND_API_KEY) return { sent: false, error: 'no-api-key' };
  const recipients = (Array.isArray(to) ? to : [to]).filter(Boolean);
  if (!recipients.length) return { sent: false, error: 'no-recipients' };

  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ from: fromEmail(env), to: recipients, subject, html }),
    });
    if (!res.ok) {
      const body = await res.text().catch(() => '');
      return { sent: false, error: `resend ${res.status}: ${body.slice(0, 300)}` };
    }
    return { sent: true };
  } catch (e) {
    return { sent: false, error: String(e && e.message ? e.message : e) };
  }
}

function emailShell(inner) {
  return `<!doctype html><html><body style="margin:0;padding:24px;background:#0e1116;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <div style="max-width:560px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;">
    <div style="background:#0e1116;padding:18px 24px;">
      <span style="color:#f5b731;font-weight:700;letter-spacing:.14em;font-size:12px;">CDL COMMAND CENTER</span>
    </div>
    <div style="padding:24px;color:#1c2430;font-size:15px;line-height:1.6;">${inner}</div>
    <div style="padding:14px 24px;background:#f4f6f9;color:#7a8595;font-size:11px;">
      CDL Management &middot; automated message
    </div>
  </div></body></html>`;
}

function otpEmailHtml(code) {
  return emailShell(`
    <p style="margin:0 0 14px;">Here is your one-time login code:</p>
    <div style="font-size:34px;font-weight:700;letter-spacing:10px;padding:16px 8px;text-align:center;background:#0e1116;color:#f5b731;border-radius:10px;">${escapeHtml(code)}</div>
    <p style="margin:16px 0 0;color:#66707e;font-size:13px;">It expires in 10 minutes. If you did not request it, ignore this email.</p>`);
}

function hotLeadEmailHtml(lead, extraLines = []) {
  const rows = [
    ['Business', lead.business_name],
    ['Contact', lead.contact_name],
    ['Email', lead.email],
    ['Phone', lead.phone],
    ['Website', lead.website],
    ['Vertical', lead.vertical],
    ['Location', [lead.city, lead.state].filter(Boolean).join(', ')],
    ...extraLines,
  ]
    .filter(([, v]) => str(v) !== '')
    .map(
      ([k, v]) =>
        `<tr><td style="padding:5px 12px 5px 0;color:#7a8595;font-size:13px;">${escapeHtml(k)}</td><td style="padding:5px 0;font-weight:600;">${escapeHtml(v)}</td></tr>`,
    )
    .join('');
  return emailShell(`
    <p style="margin:0 0 10px;font-size:18px;font-weight:700;">🔥 Hot lead</p>
    <table style="border-collapse:collapse;width:100%;">${rows}</table>
    <p style="margin:18px 0 0;color:#66707e;font-size:13px;">Strike window: 48 hours. Get the mockup + brief moving.</p>`);
}

/* ------------------------------------------------------------------ *
 * DB helpers
 * ------------------------------------------------------------------ */

async function getSetting(db, key, fallback = null) {
  const row = await db.prepare('SELECT value FROM settings WHERE key = ?').bind(key).first();
  return row && row.value !== undefined && row.value !== null ? row.value : fallback;
}

async function logActivity(db, leadId, type, body, actor) {
  if (!leadId) return null;
  const res = await db
    .prepare(
      'INSERT INTO activities (lead_id, type, body, actor, created_at) VALUES (?, ?, ?, ?, ?)',
    )
    .bind(leadId, type, str(body), str(actor) || 'System', nowIso())
    .run();
  const id = res && res.meta ? res.meta.last_row_id : null;
  if (!id) return null;
  return db.prepare('SELECT * FROM activities WHERE id = ?').bind(id).first();
}

async function getLeadById(db, id) {
  return db
    .prepare(
      `SELECT l.*, o.name AS owner_name, s.name AS strike_owner_name
         FROM leads l
         LEFT JOIN users o ON o.id = l.owner_id
         LEFT JOIN users s ON s.id = l.strike_owner_id
        WHERE l.id = ?`,
    )
    .bind(id)
    .first();
}

async function findLeadByEmail(db, email) {
  const e = str(email);
  if (!e) return null;
  return db
    .prepare("SELECT * FROM leads WHERE email IS NOT NULL AND email <> '' AND lower(email) = lower(?) LIMIT 1")
    .bind(e)
    .first();
}

async function findLeadByBusinessName(db, name) {
  const n = str(name);
  if (!n) return null;
  return db
    .prepare('SELECT * FROM leads WHERE lower(business_name) = lower(?) LIMIT 1')
    .bind(n)
    .first();
}

/* ------------------------------------------------------------------ *
 * KPI computation (shared by /api/kpis and /api/digest)
 * ------------------------------------------------------------------ */

async function computeKpis(env) {
  const db = env.DB;
  const month = currentMonth();

  const [addsRow, tierRows, closesRow, clientRow, callsRow, goalRaw, snapRows] = await Promise.all([
    db.prepare('SELECT COUNT(*) AS c FROM leads WHERE substr(created_at, 1, 7) = ?').bind(month).first(),
    db.prepare('SELECT tier, COUNT(*) AS c FROM leads GROUP BY tier').all(),
    db.prepare('SELECT COUNT(*) AS c FROM clients WHERE substr(created_at, 1, 7) = ?').bind(month).first(),
    db.prepare(
      "SELECT COUNT(*) AS c, COALESCE(SUM(mrr), 0) AS mrr FROM clients WHERE status <> 'churned'",
    ).first(),
    db.prepare(
      "SELECT COUNT(*) AS c FROM activities WHERE type = 'call' AND substr(created_at, 1, 7) = ?",
    ).bind(month).first(),
    getSetting(db, 'goal_monthly_closes', null),
    db.prepare(
      'SELECT * FROM (SELECT * FROM kpi_snapshots ORDER BY snap_date DESC LIMIT 30) ORDER BY snap_date ASC',
    ).all(),
  ]);

  const tier_counts = { Cold: 0, Engaged: 0, Hot: 0, 'Call Booked': 0 };
  for (const r of (tierRows && tierRows.results) || []) {
    if (Object.prototype.hasOwnProperty.call(tier_counts, r.tier)) {
      tier_counts[r.tier] = Number(r.c) || 0;
    }
  }

  return {
    month_adds: Number(addsRow && addsRow.c) || 0,
    tier_counts,
    month_closes: Number(closesRow && closesRow.c) || 0,
    active_clients: Number(clientRow && clientRow.c) || 0,
    mrr: Number(clientRow && clientRow.mrr) || 0,
    month_calls: Number(callsRow && callsRow.c) || 0,
    goal: intOr(goalRaw, DEFAULT_GOAL_CLOSES),
    snapshots: (snapRows && snapRows.results) || [],
  };
}

/* ------------------------------------------------------------------ *
 * Entry point
 * ------------------------------------------------------------------ */

export async function onRequest(context) {
  const { request, env } = context;

  try {
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: { Allow: 'GET, POST, PATCH, DELETE, OPTIONS' },
      });
    }

    if (!env || !env.DB) {
      return json({ error: NO_DB_MESSAGE }, 503);
    }

    const url = new URL(request.url);
    const rest = url.pathname.replace(/^\/+api\/?/, '').replace(/\/+$/, '');
    const seg = rest ? rest.split('/').map(decodeURIComponent) : [];
    const method = request.method.toUpperCase();

    return await route(context, { url, seg, method });
  } catch (err) {
    return json({ error: String(err && err.message ? err.message : err) }, 500);
  }
}

/* ------------------------------------------------------------------ *
 * Router
 * ------------------------------------------------------------------ */

async function route(context, ctx) {
  const { env } = context;
  const { seg, method } = ctx;
  const head = seg[0] || '';

  /* ---------- public routes ---------- */
  if (head === 'auth') return handleAuth(context, ctx);
  if (head === 'intake' && method === 'POST') return handleIntake(context, ctx);
  if (head === 'webhooks') return handleWebhooks(context, ctx);
  if (head === 'digest' && method === 'GET') return handleDigest(context, ctx);
  if (head === 'brief-email' && method === 'POST') {
    const secret = ctx.url.searchParams.get('secret') || '';
    if (!env.WEBHOOK_SECRET || secret !== env.WEBHOOK_SECRET) {
      return json({ error: 'Unauthorized' }, 401);
    }
    return json(await emailTodaysBrief(env));
  }
  if (head === 'health' && method === 'GET') return json({ ok: true, db: true });

  /* ---------- everything below needs a session ---------- */
  const user = await getUser(context);

  if (head === 'me' && method === 'GET') {
    if (!user) return json({ error: 'Unauthorized' }, 401);
    return json({ user: publicUser(user) });
  }

  if (!user) return json({ error: 'Unauthorized' }, 401);

  if (head === 'leads') return handleLeads(context, ctx, user);
  if (head === 'clients') return handleClients(context, ctx, user);
  if (head === 'tasks') return handleTasks(context, ctx, user);
  if (head === 'brief') return handleBrief(context, ctx, user);
  if (head === 'kpis' && method === 'GET') return json(await computeKpis(env));
  if (head === 'users') return handleUsers(context, ctx, user);

  return json({ error: 'Not found' }, 404);
}

/* ------------------------------------------------------------------ *
 * /api/brief  — the daily brief written by the agent org
 *
 * GET /api/brief            today's brief, rendered HTML
 * GET /api/brief?date=YYYY-MM-DD   a specific day
 * GET /api/brief/list       the last 30 dates, JSON
 *
 * Session required. The org writes rows into the `brief` table; nothing here
 * generates content, it only serves what the org already produced.
 * ------------------------------------------------------------------ */

async function handleBrief(context, ctx, user) {
  const { env } = context;
  const { url, seg, method } = ctx;
  if (method !== 'GET') return json({ error: 'Method not allowed' }, 405);

  if (seg[1] === 'list') {
    const r = await env.DB.prepare(
      'SELECT run_date, created_at, LENGTH(html) AS bytes FROM brief ORDER BY run_date DESC LIMIT 30'
    ).all();
    return json({ briefs: r.results || [] });
  }

  const date = url.searchParams.get('date');
  const row = date
    ? await env.DB.prepare('SELECT run_date, html FROM brief WHERE run_date = ?').bind(date).first()
    : await env.DB.prepare('SELECT run_date, html FROM brief ORDER BY run_date DESC LIMIT 1').first();

  if (!row || !row.html) {
    return new Response(briefMissingPage(date), {
      status: 404,
      headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' },
    });
  }

  return new Response(row.html, {
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'private, no-store',
      'X-Brief-Date': row.run_date,
    },
  });
}

/** Shown when a brief is asked for and none exists. Says why, rather than 404ing blankly. */
function briefMissingPage(date) {
  const what = date ? `for ${escapeHtml(date)}` : 'yet today';
  return `<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>No brief ${escapeHtml(date || '')}</title>
<style>body{margin:0;background:#f3f2ee;color:#0b0b0b;font:16px/1.6 system-ui,sans-serif;
display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px}
div{background:#fcfcfb;border:1px solid rgba(11,11,11,.1);border-radius:12px;padding:28px 32px;max-width:520px}
h1{margin:0 0 10px;font-size:20px}p{margin:0 0 8px;color:#52514e;font-size:14.5px}
code{background:#f3f2ee;padding:2px 6px;border-radius:4px;font-size:13px}</style></head>
<body><div><h1>No brief ${what}</h1>
<p>The agent organisation has not written one. It runs weekdays at 5:30am Central.</p>
<p>If it is past 6am on a weekday, the run failed. Check the scheduled task, or look
in D1 <code>cdl-command</code>, table <code>brief</code>.</p>
<p style="margin-top:14px"><a href="/api/brief/list">See which dates exist</a></p>
</div></body></html>`;
}

/** Email today's brief. Called by the cdl-brief-mailer Worker on a cron.
 *  Auth: WEBHOOK_SECRET, same as the other machine-to-machine routes. */
async function emailTodaysBrief(env) {
  const row = await env.DB.prepare(
    'SELECT run_date, html FROM brief ORDER BY run_date DESC LIMIT 1'
  ).first();
  if (!row || !row.html) return { sent: false, error: 'no-brief' };

  const r = await sendEmail(env, {
    to: alertEmail(env),
    subject: `CDL Brief, ${row.run_date}`,
    html: row.html,
  });
  return { ...r, run_date: row.run_date };
}

/* ------------------------------------------------------------------ *
 * /api/auth/*
 * ------------------------------------------------------------------ */

async function handleAuth(context, ctx) {
  const { request, env } = context;
  const { seg, method } = ctx;
  const action = seg[1] || '';
  const db = env.DB;

  if (method !== 'POST') return json({ error: 'Method not allowed' }, 405);

  /* --- request-code --- */
  if (action === 'request-code') {
    const body = await readJson(request);
    const email = str(body.email);
    if (!email) return json({ error: 'Email is required' }, 400);

    const user = await db
      .prepare('SELECT * FROM users WHERE lower(email) = lower(?) AND active = 1')
      .bind(email)
      .first();
    if (!user) return json({ error: 'No account for that email' }, 404);

    if (!env.RESEND_API_KEY) {
      return json({ error: 'Email sending not configured yet. Use password login.' }, 503);
    }

    const code = randomCode6();
    const codeHash = await sha256hex(code + String(env.SESSION_SECRET || ''));
    const expiresAt = new Date(Date.now() + OTP_TTL_MS).toISOString();

    await db.prepare('DELETE FROM otp_codes WHERE lower(email) = lower(?)').bind(user.email).run();
    await db
      .prepare(
        'INSERT INTO otp_codes (email, code_hash, expires_at, attempts, created_at) VALUES (?, ?, ?, 0, ?)',
      )
      .bind(user.email, codeHash, expiresAt, nowIso())
      .run();

    const sent = await sendEmail(env, {
      to: user.email,
      subject: 'Your CDL Command login code',
      html: otpEmailHtml(code),
    });
    if (!sent.sent) {
      return json({ error: 'Could not send the login code. Try password login.' }, 502);
    }
    return json({ ok: true });
  }

  /* --- verify --- */
  if (action === 'verify') {
    const body = await readJson(request);
    const email = str(body.email);
    const code = str(body.code);
    if (!email || !code) return json({ error: 'Email and code are required' }, 400);

    const row = await db
      .prepare(
        'SELECT * FROM otp_codes WHERE lower(email) = lower(?) AND expires_at > ? ORDER BY id DESC LIMIT 1',
      )
      .bind(email, nowIso())
      .first();

    if (!row) return json({ error: 'Code expired or not found. Request a new one.' }, 400);

    if (Number(row.attempts || 0) >= OTP_MAX_ATTEMPTS) {
      return json({ error: 'Too many attempts. Request a new code.' }, 429);
    }

    const hash = await sha256hex(code + String(env.SESSION_SECRET || ''));
    if (!safeEqual(hash, row.code_hash)) {
      await db
        .prepare('UPDATE otp_codes SET attempts = attempts + 1 WHERE id = ?')
        .bind(row.id)
        .run();
      const left = Math.max(0, OTP_MAX_ATTEMPTS - (Number(row.attempts || 0) + 1));
      return json({ error: `Invalid code. ${left} attempt${left === 1 ? '' : 's'} left.` }, 401);
    }

    const user = await db
      .prepare('SELECT * FROM users WHERE lower(email) = lower(?) AND active = 1')
      .bind(email)
      .first();
    if (!user) return json({ error: 'No account for that email' }, 404);

    await db.prepare('DELETE FROM otp_codes WHERE lower(email) = lower(?)').bind(email).run();
    return loginResponse(env, user);
  }

  /* --- password (break glass) --- */
  if (action === 'password') {
    const body = await readJson(request);
    const email = str(body.email);
    const password = str(body.password);

    if (!env.BREAK_GLASS_PASSWORD || !password || !safeEqual(password, env.BREAK_GLASS_PASSWORD)) {
      return json({ error: 'Invalid credentials' }, 401);
    }
    const user = await db
      .prepare('SELECT * FROM users WHERE lower(email) = lower(?) AND active = 1')
      .bind(email)
      .first();
    if (!user) return json({ error: 'Invalid credentials' }, 401);

    return loginResponse(env, user);
  }

  /* --- logout --- */
  if (action === 'logout') {
    return json({ ok: true }, 200, { 'Set-Cookie': clearCookieHeader() });
  }

  return json({ error: 'Not found' }, 404);
}

/* ------------------------------------------------------------------ *
 * /api/leads/*
 * ------------------------------------------------------------------ */

async function handleLeads(context, ctx, user) {
  const { request, env } = context;
  const { url, seg, method } = ctx;
  const db = env.DB;

  /* GET /api/leads */
  if (seg.length === 1 && method === 'GET') return listLeads(db, url);

  /* POST /api/leads */
  if (seg.length === 1 && method === 'POST') {
    const body = await readJson(request);
    if (!str(body.business_name)) return json({ error: 'business_name is required' }, 400);

    const cols = [];
    const vals = [];
    for (const f of LEAD_WRITE_FIELDS) {
      if (body[f] !== undefined) {
        cols.push(f);
        vals.push(body[f] === null ? null : body[f]);
      }
    }
    if (!cols.includes('tier')) {
      cols.push('tier');
      vals.push('Cold');
    }
    const ts = nowIso();
    cols.push('created_at', 'updated_at');
    vals.push(ts, ts);

    const placeholders = cols.map(() => '?').join(', ');
    const res = await db
      .prepare(`INSERT INTO leads (${cols.join(', ')}) VALUES (${placeholders})`)
      .bind(...vals)
      .run();
    const id = res.meta.last_row_id;

    await logActivity(db, id, 'system', 'Lead created', user.name);
    return json({ lead: await getLeadById(db, id) }, 201);
  }

  /* POST /api/leads/import */
  if (seg.length === 2 && seg[1] === 'import' && method === 'POST') {
    return importLeads(db, request, user);
  }

  const id = intOr(seg[1], null);
  if (id === null) return json({ error: 'Not found' }, 404);

  /* GET /api/leads/:id */
  if (seg.length === 2 && method === 'GET') {
    const lead = await getLeadById(db, id);
    if (!lead) return json({ error: 'Lead not found' }, 404);
    const acts = await db
      .prepare('SELECT * FROM activities WHERE lead_id = ? ORDER BY created_at DESC, id DESC')
      .bind(id)
      .all();
    return json({ lead, activities: acts.results || [] });
  }

  /* PATCH /api/leads/:id */
  if (seg.length === 2 && method === 'PATCH') {
    const existing = await db.prepare('SELECT * FROM leads WHERE id = ?').bind(id).first();
    if (!existing) return json({ error: 'Lead not found' }, 404);

    const body = await readJson(request);
    const sets = [];
    const vals = [];
    for (const f of LEAD_PATCH_FIELDS) {
      if (body[f] === undefined) continue;
      sets.push(`${f} = ?`);
      vals.push(body[f] === null ? null : body[f]);
    }

    const newTier = body.tier !== undefined ? str(body.tier) : null;
    const tierChanged = newTier !== null && newTier !== existing.tier;

    if (tierChanged && newTier === 'Hot' && !existing.hot_at) {
      sets.push('hot_at = ?');
      vals.push(nowIso());
    }

    if (!sets.length) return json({ lead: await getLeadById(db, id) });

    sets.push('updated_at = ?');
    vals.push(nowIso());
    vals.push(id);

    await db.prepare(`UPDATE leads SET ${sets.join(', ')} WHERE id = ?`).bind(...vals).run();

    if (tierChanged) {
      await logActivity(
        db,
        id,
        'tier_change',
        `${existing.tier || 'None'} → ${newTier}`,
        user.name,
      );
    }
    return json({ lead: await getLeadById(db, id) });
  }

  /* POST /api/leads/:id/notes */
  if (seg.length === 3 && seg[2] === 'notes' && method === 'POST') {
    const lead = await db.prepare('SELECT id FROM leads WHERE id = ?').bind(id).first();
    if (!lead) return json({ error: 'Lead not found' }, 404);

    const body = await readJson(request);
    const text = str(body.body);
    if (!text) return json({ error: 'Note body is required' }, 400);

    const activity = await logActivity(db, id, 'note', text, user.name);
    await db.prepare('UPDATE leads SET updated_at = ? WHERE id = ?').bind(nowIso(), id).run();
    return json({ activity }, 201);
  }

  return json({ error: 'Not found' }, 404);
}

async function listLeads(db, url) {
  const p = url.searchParams;
  const tier = str(p.get('tier'));
  const vertical = str(p.get('vertical'));
  const q = str(p.get('q'));
  const owner = str(p.get('owner'));
  const limit = Math.min(Math.max(intOr(p.get('limit'), 100), 1), 500);
  const offset = Math.max(intOr(p.get('offset'), 0), 0);

  const where = [];
  const args = [];

  if (tier) {
    where.push('l.tier = ?');
    args.push(tier);
  }
  if (vertical) {
    where.push('lower(l.vertical) = lower(?)');
    args.push(vertical);
  }
  if (owner) {
    where.push('l.owner_id = ?');
    args.push(intOr(owner, -1));
  }
  if (q) {
    where.push(
      `(lower(COALESCE(l.business_name,'')) LIKE lower(?)
        OR lower(COALESCE(l.contact_name,'')) LIKE lower(?)
        OR lower(COALESCE(l.city,'')) LIKE lower(?)
        OR lower(COALESCE(l.email,'')) LIKE lower(?))`,
    );
    const like = `%${q}%`;
    args.push(like, like, like, like);
  }

  const whereSql = where.length ? `WHERE ${where.join(' AND ')}` : '';

  const rows = await db
    .prepare(
      `SELECT l.*, o.name AS owner_name, s.name AS strike_owner_name
         FROM leads l
         LEFT JOIN users o ON o.id = l.owner_id
         LEFT JOIN users s ON s.id = l.strike_owner_id
         ${whereSql}
        ORDER BY ${TIER_ORDER_SQL}, l.updated_at DESC, l.id DESC
        LIMIT ? OFFSET ?`,
    )
    .bind(...args, limit, offset)
    .all();

  const countRow = await db
    .prepare(`SELECT COUNT(*) AS c FROM leads l ${whereSql}`)
    .bind(...args)
    .first();

  return json({ leads: rows.results || [], total: Number(countRow && countRow.c) || 0 });
}

async function importLeads(db, request, user) {
  const body = await readJson(request);
  const rows = Array.isArray(body.rows) ? body.rows : [];
  if (!rows.length) return json({ inserted: 0, skipped: 0 });

  const existing = await db
    .prepare(
      `SELECT lower(COALESCE(email,'')) AS e,
              lower(COALESCE(business_name,'')) AS b,
              lower(COALESCE(state,'')) AS s
         FROM leads`,
    )
    .all();

  const emailSet = new Set();
  const nameStateSet = new Set();
  for (const r of existing.results || []) {
    if (r.e) emailSet.add(r.e);
    if (r.b) nameStateSet.add(`${r.b}||${r.s}`);
  }

  let inserted = 0;
  let skipped = 0;
  const ts = nowIso();

  for (const raw of rows) {
    if (!raw || typeof raw !== 'object') {
      skipped++;
      continue;
    }
    const businessName = str(raw.business_name);
    if (!businessName) {
      skipped++;
      continue;
    }
    const email = str(raw.email);
    const emailKey = email.toLowerCase();
    const nameStateKey = `${businessName.toLowerCase()}||${str(raw.state).toLowerCase()}`;

    if ((emailKey && emailSet.has(emailKey)) || nameStateSet.has(nameStateKey)) {
      skipped++;
      continue;
    }

    const cols = [];
    const vals = [];
    for (const f of IMPORT_FIELDS) {
      if (raw[f] === undefined || raw[f] === null) continue;
      cols.push(f);
      vals.push(str(raw[f]));
    }
    if (!cols.includes('business_name')) {
      cols.push('business_name');
      vals.push(businessName);
    }
    cols.push('tier', 'created_at', 'updated_at');
    vals.push('Cold', ts, ts);

    const res = await db
      .prepare(`INSERT INTO leads (${cols.join(', ')}) VALUES (${cols.map(() => '?').join(', ')})`)
      .bind(...vals)
      .run();

    await logActivity(db, res.meta.last_row_id, 'system', 'Lead created (import)', user.name);

    if (emailKey) emailSet.add(emailKey);
    nameStateSet.add(nameStateKey);
    inserted++;
  }

  return json({ inserted, skipped });
}

/* ------------------------------------------------------------------ *
 * /api/clients/* and /api/tasks/*
 * ------------------------------------------------------------------ */

async function handleClients(context, ctx, user) {
  const { request, env } = context;
  const { seg, method } = ctx;
  const db = env.DB;

  /* GET /api/clients */
  if (seg.length === 1 && method === 'GET') {
    const clients = await db
      .prepare('SELECT * FROM clients ORDER BY created_at DESC, id DESC')
      .all();
    const list = clients.results || [];
    if (!list.length) return json({ clients: [] });

    const tasks = await db
      .prepare('SELECT * FROM onboarding_tasks ORDER BY sort ASC, id ASC')
      .all();
    const byClient = new Map();
    for (const t of tasks.results || []) {
      if (!byClient.has(t.client_id)) byClient.set(t.client_id, []);
      byClient.get(t.client_id).push(t);
    }

    return json({
      clients: list.map((c) => {
        const ts = byClient.get(c.id) || [];
        return {
          ...c,
          tasks: ts,
          done_count: ts.filter((t) => Number(t.done) === 1).length,
          total_count: ts.length,
        };
      }),
    });
  }

  /* POST /api/clients */
  if (seg.length === 1 && method === 'POST') {
    const body = await readJson(request);
    let businessName = str(body.business_name);
    let vertical = str(body.vertical);
    const leadId = body.lead_id !== undefined && body.lead_id !== null ? intOr(body.lead_id, null) : null;

    if (leadId !== null) {
      const lead = await db.prepare('SELECT * FROM leads WHERE id = ?').bind(leadId).first();
      if (!lead) return json({ error: 'Lead not found' }, 404);
      businessName = str(lead.business_name) || businessName;
      vertical = str(lead.vertical) || vertical;

      if (lead.tier !== 'Won') {
        await db
          .prepare('UPDATE leads SET tier = ?, updated_at = ? WHERE id = ?')
          .bind('Won', nowIso(), leadId)
          .run();
        await logActivity(db, leadId, 'tier_change', `${lead.tier || 'None'} → Won`, user.name);
      }
    }

    if (!businessName) return json({ error: 'business_name or lead_id is required' }, 400);

    const res = await db
      .prepare(
        `INSERT INTO clients (lead_id, business_name, vertical, mrr, ad_spend, start_date, status, created_at)
         VALUES (?, ?, ?, ?, ?, ?, 'onboarding', ?)`,
      )
      .bind(
        leadId,
        businessName,
        vertical || null,
        numOr(body.mrr, 0),
        numOr(body.ad_spend, 0),
        todayIso(),
        nowIso(),
      )
      .run();

    const clientId = res.meta.last_row_id;

    for (const [title, dueDay, sort] of ONBOARDING_TEMPLATE) {
      await db
        .prepare(
          'INSERT INTO onboarding_tasks (client_id, title, due_day, done, sort) VALUES (?, ?, ?, 0, ?)',
        )
        .bind(clientId, title, dueDay, sort)
        .run();
    }

    return json({ client: await clientWithTasks(db, clientId) }, 201);
  }

  /* PATCH /api/clients/:id */
  const id = intOr(seg[1], null);
  if (seg.length === 2 && method === 'PATCH' && id !== null) {
    const existing = await db.prepare('SELECT * FROM clients WHERE id = ?').bind(id).first();
    if (!existing) return json({ error: 'Client not found' }, 404);

    const body = await readJson(request);
    const sets = [];
    const vals = [];
    for (const f of ['mrr', 'ad_spend', 'status', 'business_name']) {
      if (body[f] === undefined) continue;
      sets.push(`${f} = ?`);
      vals.push(f === 'mrr' || f === 'ad_spend' ? numOr(body[f], 0) : body[f]);
    }
    if (!sets.length) return json({ client: await clientWithTasks(db, id) });

    vals.push(id);
    await db.prepare(`UPDATE clients SET ${sets.join(', ')} WHERE id = ?`).bind(...vals).run();
    return json({ client: await clientWithTasks(db, id) });
  }

  return json({ error: 'Not found' }, 404);
}

async function clientWithTasks(db, clientId) {
  const client = await db.prepare('SELECT * FROM clients WHERE id = ?').bind(clientId).first();
  if (!client) return null;
  const tasks = await db
    .prepare('SELECT * FROM onboarding_tasks WHERE client_id = ? ORDER BY sort ASC, id ASC')
    .bind(clientId)
    .all();
  const list = tasks.results || [];
  return {
    ...client,
    tasks: list,
    done_count: list.filter((t) => Number(t.done) === 1).length,
    total_count: list.length,
  };
}

async function handleTasks(context, ctx) {
  const { request, env } = context;
  const { seg, method } = ctx;
  const db = env.DB;
  const id = intOr(seg[1], null);

  /* PATCH /api/tasks/:id */
  if (seg.length === 2 && method === 'PATCH' && id !== null) {
    const task = await db.prepare('SELECT * FROM onboarding_tasks WHERE id = ?').bind(id).first();
    if (!task) return json({ error: 'Task not found' }, 404);

    const body = await readJson(request);
    const done = body.done === true || body.done === 1 || body.done === '1' ? 1 : 0;

    await db
      .prepare('UPDATE onboarding_tasks SET done = ?, done_at = ? WHERE id = ?')
      .bind(done, done ? nowIso() : null, id)
      .run();

    return json({ task: await db.prepare('SELECT * FROM onboarding_tasks WHERE id = ?').bind(id).first() });
  }

  return json({ error: 'Not found' }, 404);
}

/* ------------------------------------------------------------------ *
 * /api/users/*
 * ------------------------------------------------------------------ */

const VALID_ROLES = ['owner', 'sales', 'implementation'];

async function handleUsers(context, ctx, user) {
  const { request, env } = context;
  const { seg, method } = ctx;
  const db = env.DB;

  if (seg.length === 1 && method === 'GET') {
    const rows = await db.prepare('SELECT * FROM users ORDER BY name ASC, id ASC').all();
    return json({ users: rows.results || [] });
  }

  if (user.role !== 'owner') return json({ error: 'Owner role required' }, 403);

  if (seg.length === 1 && method === 'POST') {
    const body = await readJson(request);
    const name = str(body.name);
    const email = str(body.email);
    const role = str(body.role) || 'sales';
    if (!name || !email) return json({ error: 'name and email are required' }, 400);
    if (!VALID_ROLES.includes(role)) return json({ error: 'Invalid role' }, 400);

    const dupe = await db
      .prepare('SELECT id FROM users WHERE lower(email) = lower(?)')
      .bind(email)
      .first();
    if (dupe) return json({ error: 'A user with that email already exists' }, 409);

    const res = await db
      .prepare('INSERT INTO users (name, email, role, active, created_at) VALUES (?, ?, ?, 1, ?)')
      .bind(name, email, role, nowIso())
      .run();

    return json(
      { user: await db.prepare('SELECT * FROM users WHERE id = ?').bind(res.meta.last_row_id).first() },
      201,
    );
  }

  const id = intOr(seg[1], null);
  if (seg.length === 2 && method === 'PATCH' && id !== null) {
    const existing = await db.prepare('SELECT * FROM users WHERE id = ?').bind(id).first();
    if (!existing) return json({ error: 'User not found' }, 404);

    const body = await readJson(request);
    const sets = [];
    const vals = [];

    if (body.name !== undefined) {
      sets.push('name = ?');
      vals.push(str(body.name));
    }
    if (body.email !== undefined) {
      sets.push('email = ?');
      vals.push(str(body.email));
    }
    if (body.role !== undefined) {
      const role = str(body.role);
      if (!VALID_ROLES.includes(role)) return json({ error: 'Invalid role' }, 400);
      sets.push('role = ?');
      vals.push(role);
    }
    if (body.active !== undefined) {
      sets.push('active = ?');
      vals.push(body.active === true || body.active === 1 || body.active === '1' ? 1 : 0);
    }
    if (!sets.length) return json({ user: existing });

    vals.push(id);
    await db.prepare(`UPDATE users SET ${sets.join(', ')} WHERE id = ?`).bind(...vals).run();
    return json({ user: await db.prepare('SELECT * FROM users WHERE id = ?').bind(id).first() });
  }

  return json({ error: 'Not found' }, 404);
}

/* ------------------------------------------------------------------ *
 * /api/intake  (public landing-page form)
 * ------------------------------------------------------------------ */

async function handleIntake(context) {
  const { request, env } = context;
  const db = env.DB;
  const body = await readJson(request);

  // Honeypot — bots fill hidden fields. Look successful, do nothing.
  if (str(body.company_website_hp)) return json({ ok: true });

  const businessName = str(body.business_name);
  const name = str(body.name);
  const email = str(body.email);
  const phone = str(body.phone);
  const website = str(body.website);
  const vertical = str(body.vertical);

  if (!businessName && !email) {
    return json({ error: 'business_name or email is required' }, 400);
  }

  const ts = nowIso();
  let lead = (await findLeadByEmail(db, email)) || (await findLeadByBusinessName(db, businessName));

  if (lead) {
    await db
      .prepare(
        `UPDATE leads SET
            tier = 'Hot',
            hot_at = ?,
            contact_name = COALESCE(NULLIF(contact_name, ''), ?),
            email        = COALESCE(NULLIF(email, ''), ?),
            phone        = COALESCE(NULLIF(phone, ''), ?),
            website      = COALESCE(NULLIF(website, ''), ?),
            vertical     = COALESCE(NULLIF(vertical, ''), ?),
            updated_at   = ?
          WHERE id = ?`,
      )
      .bind(ts, name || null, email || null, phone || null, website || null, vertical || null, ts, lead.id)
      .run();
  } else {
    const res = await db
      .prepare(
        `INSERT INTO leads (business_name, vertical, contact_name, phone, email, website, tier, source, hot_at, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?, 'Hot', 'mockup-page', ?, ?, ?)`,
      )
      .bind(
        businessName || name || email,
        vertical || null,
        name || null,
        phone || null,
        email || null,
        website || null,
        ts,
        ts,
        ts,
      )
      .run();
    lead = await db.prepare('SELECT * FROM leads WHERE id = ?').bind(res.meta.last_row_id).first();
  }

  await logActivity(
    db,
    lead.id,
    'system',
    'Requested free homepage mockup via landing page',
    'Website',
  );

  if (env.RESEND_API_KEY) {
    await sendEmail(env, {
      to: alertEmail(env),
      subject: `HOT LEAD: ${lead.business_name || businessName}`,
      html: hotLeadEmailHtml(
        {
          business_name: lead.business_name || businessName,
          contact_name: name || lead.contact_name,
          email: email || lead.email,
          phone: phone || lead.phone,
          website: website || lead.website,
          vertical: vertical || lead.vertical,
          city: lead.city,
          state: lead.state,
        },
        [['Source', 'Free homepage mockup landing page']],
      ),
    });
  }

  return json({ ok: true });
}

/* ------------------------------------------------------------------ *
 * /api/webhooks/*
 * ------------------------------------------------------------------ */

function checkSecret(url, env) {
  const provided = url.searchParams.get('secret') || '';
  if (!env.WEBHOOK_SECRET || !safeEqual(provided, env.WEBHOOK_SECRET)) return false;
  return true;
}

async function handleWebhooks(context, ctx) {
  const { url, seg, method } = ctx;
  const which = seg[1] || '';

  if (method !== 'POST') return json({ error: 'Method not allowed' }, 405);
  if (!checkSecret(url, context.env)) return json({ error: 'Unauthorized' }, 401);

  if (which === 'smartlead') return handleSmartlead(context);
  if (which === 'dialpad') return handleDialpad(context);

  return json({ error: 'Not found' }, 404);
}

async function handleSmartlead(context) {
  const { request, env } = context;
  const db = env.DB;
  const body = await readJson(request);

  const eventRaw = body.event_type || body.eventType || body.event || '';
  const event = String(eventRaw).toUpperCase();

  const email = str(
    body.to_email || body.lead_email || body.email || (body.lead && body.lead.email) || '',
  );

  const lead = await findLeadByEmail(db, email);
  if (!lead) return json({ ok: true, unmatched: true });

  const ts = nowIso();
  const touch = async () =>
    db.prepare('UPDATE leads SET updated_at = ? WHERE id = ?').bind(ts, lead.id).run();

  if (event.includes('SENT')) {
    await logActivity(db, lead.id, 'email_sent', 'Smartlead: email sent', 'Smartlead');
    await touch();
  } else if (event.includes('OPEN')) {
    await logActivity(db, lead.id, 'email_open', 'Smartlead: email opened', 'Smartlead');
    await touch();
  } else if (event.includes('CLICK')) {
    await logActivity(db, lead.id, 'email_click', 'Smartlead: link clicked', 'Smartlead');
    if (lead.tier === 'Cold') {
      await db
        .prepare('UPDATE leads SET tier = ?, updated_at = ? WHERE id = ?')
        .bind('Engaged', ts, lead.id)
        .run();
      await logActivity(db, lead.id, 'tier_change', 'Cold → Engaged', 'Smartlead');
    } else {
      await touch();
    }
  } else if (event.includes('REPLY') || event.includes('REPLIED')) {
    await logActivity(db, lead.id, 'email_reply', str(body.reply_body || ''), 'Smartlead');

    if (lead.tier === 'Cold' || lead.tier === 'Engaged') {
      await db
        .prepare('UPDATE leads SET tier = ?, hot_at = ?, updated_at = ? WHERE id = ?')
        .bind('Hot', ts, ts, lead.id)
        .run();
      await logActivity(db, lead.id, 'tier_change', `${lead.tier} → Hot`, 'Smartlead');
    } else {
      await touch();
    }

    if (env.RESEND_API_KEY) {
      await sendEmail(env, {
        to: alertEmail(env),
        subject: `HOT LEAD: ${lead.business_name}`,
        html: hotLeadEmailHtml(lead, [
          ['Source', 'Smartlead reply'],
          ['Reply', str(body.reply_body || '').slice(0, 600)],
        ]),
      });
    }
  } else if (event.includes('BOUNCE') || event.includes('UNSUB')) {
    await db
      .prepare('UPDATE leads SET dnc = 1, updated_at = ? WHERE id = ?')
      .bind(ts, lead.id)
      .run();
    await logActivity(
      db,
      lead.id,
      'system',
      `Smartlead: ${event.includes('BOUNCE') ? 'bounced' : 'unsubscribed'} — marked DNC`,
      'Smartlead',
    );
  } else {
    await logActivity(db, lead.id, 'system', `Smartlead event: ${event || 'unknown'}`, 'Smartlead');
  }

  return json({ ok: true });
}

async function handleDialpad(context) {
  const { request, env } = context;
  const db = env.DB;
  const body = await readJson(request);

  const rawPhone =
    (body.contact && body.contact.phone) ||
    body.external_number ||
    body.from_number ||
    body.to_number ||
    '';

  const digits = digitsOnly(rawPhone);
  if (digits.length < 10) return json({ ok: true, unmatched: true });
  const last10 = digits.slice(-10);

  const candidates = await db
    .prepare("SELECT id, phone FROM leads WHERE phone IS NOT NULL AND phone <> ''")
    .all();

  let matchId = null;
  for (const row of candidates.results || []) {
    const d = digitsOnly(row.phone);
    if (d.length >= 10 && d.slice(-10) === last10) {
      matchId = row.id;
      break;
    }
  }

  if (matchId === null) return json({ ok: true, unmatched: true });

  await logActivity(
    db,
    matchId,
    'call',
    `Dialpad: ${str(body.state) || str(body.event) || 'call event'}`,
    'Dialpad',
  );
  await db.prepare('UPDATE leads SET updated_at = ? WHERE id = ?').bind(nowIso(), matchId).run();

  return json({ ok: true, lead_id: matchId });
}

/* ------------------------------------------------------------------ *
 * /api/digest  (daily snapshot + owner email)
 * ------------------------------------------------------------------ */

async function handleDigest(context, ctx) {
  const { env } = context;
  const db = env.DB;

  if (!checkSecret(ctx.url, env)) return json({ error: 'Unauthorized' }, 401);

  const kpis = await computeKpis(env);

  await db
    .prepare(
      `INSERT OR REPLACE INTO kpi_snapshots (snap_date, adds, engaged, hot, calls, closes, mrr)
       VALUES (date('now'), ?, ?, ?, ?, ?, ?)`,
    )
    .bind(
      kpis.month_adds,
      kpis.tier_counts.Engaged,
      kpis.tier_counts.Hot,
      kpis.month_calls,
      kpis.month_closes,
      kpis.mrr,
    )
    .run();

  const hotLeads = await db
    .prepare(
      `SELECT l.id, l.business_name, l.hot_at, l.mockup_status, l.brief_status, u.name AS strike_owner_name
         FROM leads l
         LEFT JOIN users u ON u.id = l.strike_owner_id
        WHERE l.tier = 'Hot'
        ORDER BY l.hot_at ASC
        LIMIT 50`,
    )
    .all();

  const cutoff = addDaysIso(-2);
  const overdue = (hotLeads.results || []).filter(
    (l) =>
      l.hot_at &&
      String(l.hot_at) < cutoff &&
      (l.mockup_status !== 'delivered' || l.brief_status !== 'delivered'),
  );

  if (env.RESEND_API_KEY) {
    const owners = await db
      .prepare(
        "SELECT email FROM users WHERE role = 'owner' AND active = 1 AND email IS NOT NULL AND email <> ''",
      )
      .all();
    const recipients = (owners.results || []).map((r) => r.email).filter(Boolean);
    if (recipients.length) {
      await sendEmail(env, {
        to: recipients,
        subject: `CDL daily digest — ${todayIso()}`,
        html: digestHtml(kpis, hotLeads.results || [], overdue),
      });
    }
  }

  return json({ ok: true, kpis });
}

function digestHtml(kpis, hotLeads, overdue) {
  const stat = (label, value) =>
    `<td style="padding:10px 14px;background:#f4f6f9;border-radius:10px;">
       <div style="font-size:11px;letter-spacing:.08em;color:#7a8595;text-transform:uppercase;">${escapeHtml(label)}</div>
       <div style="font-size:22px;font-weight:700;color:#0e1116;">${escapeHtml(value)}</div>
     </td>`;

  const hotList = hotLeads.length
    ? `<ul style="margin:6px 0 0;padding-left:18px;">${hotLeads
        .map(
          (l) =>
            `<li style="margin:3px 0;">${escapeHtml(l.business_name)}${
              l.strike_owner_name ? ` <span style="color:#7a8595;">— ${escapeHtml(l.strike_owner_name)}</span>` : ''
            }</li>`,
        )
        .join('')}</ul>`
    : '<p style="margin:6px 0 0;color:#7a8595;">No hot leads right now.</p>';

  const overdueList = overdue.length
    ? `<ul style="margin:6px 0 0;padding-left:18px;">${overdue
        .map(
          (l) =>
            `<li style="margin:3px 0;color:#b3261e;">${escapeHtml(l.business_name)} — mockup: ${escapeHtml(
              l.mockup_status || 'none',
            )}, brief: ${escapeHtml(l.brief_status || 'none')}</li>`,
        )
        .join('')}</ul>`
    : '<p style="margin:6px 0 0;color:#1e8e3e;">No overdue strikes. 48-hour window clean.</p>';

  return emailShell(`
    <p style="margin:0 0 14px;font-size:18px;font-weight:700;">Daily digest — ${escapeHtml(todayIso())}</p>

    <table style="width:100%;border-collapse:separate;border-spacing:8px 8px;">
      <tr>${stat('Adds (MTD)', kpis.month_adds)}${stat('Calls (MTD)', kpis.month_calls)}</tr>
      <tr>${stat('Hot', kpis.tier_counts.Hot)}${stat('Engaged', kpis.tier_counts.Engaged)}</tr>
      <tr>${stat('Call Booked', kpis.tier_counts['Call Booked'])}${stat('Cold', kpis.tier_counts.Cold)}</tr>
      <tr>${stat('Closes vs goal', `${kpis.month_closes} / ${kpis.goal}`)}${stat('MRR', `$${Math.round(kpis.mrr).toLocaleString('en-US')}`)}</tr>
    </table>

    <h3 style="margin:22px 0 0;font-size:14px;text-transform:uppercase;letter-spacing:.08em;color:#7a8595;">Hot leads (${hotLeads.length})</h3>
    ${hotList}

    <h3 style="margin:22px 0 0;font-size:14px;text-transform:uppercase;letter-spacing:.08em;color:#7a8595;">Strikes overdue (${overdue.length})</h3>
    ${overdueList}

    <p style="margin:22px 0 0;color:#66707e;font-size:13px;">Active clients: ${kpis.active_clients}</p>`);
}
