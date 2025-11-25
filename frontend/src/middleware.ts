import type { APIContext } from 'astro';

export async function onRequest(context: APIContext, next: Function) {
  const url = new URL(context.request.url);
  const path = url.pathname;

  if (path.startsWith('/admin')) {
    const raw = context.request.headers.get('cookie') || '';
    const cookies: Record<string, string> = {};
    raw.split(';').forEach(pair => {
      const idx = pair.indexOf('=');
      if (idx > -1) {
        const k = pair.slice(0, idx).trim();
        const v = pair.slice(idx + 1).trim();
        cookies[k] = v;
      }
    });
    const isLogged = cookies['isLoggedIn'] === 'true';
    const role = String(cookies['role'] || '').toLowerCase();
    const allowed = ['administrador','admin','trabajador','vendedor','bodeguero'];
    // Bloquear únicamente si el rol en cookie es explícitamente "cliente".
    if (role === 'cliente') {
      return new Response(null, { status: 302, headers: new Headers({ Location: '/?error=unauthorized_admin' }) });
    }
    // Si no hay cookies, dejar pasar y validar en el layout del admin.
  }

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