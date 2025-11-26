import type { APIContext } from 'astro';

const env = import.meta.env.PUBLIC_ENVIRONMENT;
const devApiDefault = 'http://localhost:8000/api';
const apiBase = env === 'development'
  ? (String(import.meta.env.PUBLIC_API_URL || '').startsWith('http') ? import.meta.env.PUBLIC_API_URL : devApiDefault)
  : import.meta.env.PUBLIC_API_URL_PRODUCTION;
let didHealthPing = false;
async function pingHealthOnce() {
  if (didHealthPing) return;
  didHealthPing = true;
  try {
    const url = String(apiBase || devApiDefault).replace(/\/$/, '') + '/health';
    console.log(`[frontend] Ping de health al backend: ${url}`);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => { try { controller.abort(); } catch {} }, 5000);
    const res = await fetch(url, { method: 'GET', signal: controller.signal }).catch((err) => {
      console.log(`[frontend] Backend health FAILED: ${String(err && err.message || err)}`);
      throw err;
    });
    clearTimeout(timeoutId);
    if (res && res.ok) {
      console.log(`[frontend] Backend health OK: ${res.status}`);
    } else {
      console.log(`[frontend] Backend health NOT OK: ${res ? res.status : 'no response'}`);
    }
  } catch {}
}

pingHealthOnce();

export async function onRequest(context: APIContext, next: Function) {
  const url = new URL(context.request.url);
  const path = url.pathname;
  pingHealthOnce();

  // Acceso a /admin sin restricciones de rol; validaciones se manejan en el cliente o páginas.

  const res = await next();

  try {
    const headers = new Headers(res.headers);
    const isStatic = /\.(css|js|mjs|png|jpg|jpeg|webp|svg|gif|ico|woff2?|ttf)$/i.test(path);
    const isImage = /\.(png|jpg|jpeg|webp|svg|gif|ico)$/i.test(path);

    if (isStatic) {
      headers.set('Cache-Control', 'public, max-age=31536000, immutable');
    } else {
      headers.set('Cache-Control', 'no-cache');
    }

    if (isImage) {
      headers.set('Accept-Ranges', 'bytes');
    }

    return new Response(res.body, { status: res.status, headers });
  } catch {
    return res;
  }
}
