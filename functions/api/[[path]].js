/**
 * MOVED 2026-08-22.
 *
 * This was a Cloudflare Pages Function. cdlmanagement.com is a static-assets
 * Worker, not a Pages project, so Cloudflare never executed this file. Every
 * /api/* route returned 404 for as long as it lived here.
 *
 * The real backend is now the `cdl-api` Worker:
 *     cdl-management/api-worker/src/api.js
 *
 * It serves cdlmanagement.com/api/* via a Worker route. Edit it there.
 * This stub stays so the mistake is not repeated.
 */
export async function onRequest() {
  return new Response(
    JSON.stringify({ error: 'Moved. The API is the cdl-api Worker.' }),
    { status: 410, headers: { 'Content-Type': 'application/json' } }
  );
}
