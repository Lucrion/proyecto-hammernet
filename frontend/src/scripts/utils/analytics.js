export function trackEvent(name, properties = {}) {
  try {
    const env = typeof window !== 'undefined' ? (window.__ENV__ || {}) : {};
    const apiBase = (env.PUBLIC_API_URL || env.PUBLIC_API_URL_PRODUCTION || 'http://localhost:8000/api').replace(/\/$/, '');
    const body = {
      name,
      properties,
      url: typeof window !== 'undefined' ? window.location.href : undefined,
      ts: Date.now(),
    };
    fetch(`${apiBase}/analytics/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      keepalive: true
    }).catch(() => {});
  } catch {}
}

export function trackError(error, context = {}) {
  try {
    const message = (error && (error.message || String(error))) || 'unknown';
    trackEvent('error', { message, ...context });
  } catch {}
}