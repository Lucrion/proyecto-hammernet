// Configuración base de API
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_URL = isDevelopment 
  ? (window.__ENV__?.PUBLIC_API_URL || 'http://localhost:8000/api')
  : (window.__ENV__?.PUBLIC_API_URL_PRODUCTION || 'https://hammernet-backend.onrender.com/api');

const API_TIMEOUT = parseInt(window.__ENV__?.PUBLIC_API_TIMEOUT || '10000');

function showStatus(message, type = 'info') {
  const el = document.getElementById('statusMessage');
  el.textContent = message;
  el.className = 'mt-2 text-sm text-center';
  el.classList.remove('hidden');
  el.classList.add(type === 'error' ? 'text-red-600' : type === 'success' ? 'text-green-600' : 'text-gray-600');
}

function showLoading(isLoading) {
  const btn = document.getElementById('registerButton');
  const spinner = document.getElementById('loadingSpinner');
  if (isLoading) {
    spinner.classList.remove('hidden');
    btn.disabled = true;
    btn.classList.add('opacity-75');
  } else {
    spinner.classList.add('hidden');
    btn.disabled = false;
    btn.classList.remove('opacity-75');
  }
}

function showGoogleLoading(isLoading) {
  const btn = document.getElementById('googleButton');
  const spinner = document.getElementById('googleLoadingSpinner');
  if (isLoading) {
    spinner.classList.remove('hidden');
    btn.disabled = true;
    btn.classList.add('opacity-75');
  } else {
    spinner.classList.add('hidden');
    btn.disabled = false;
    btn.classList.remove('opacity-75');
  }
}

function normalizeRut(value) {
  if (!value) return '';
  const cleaned = value.replace(/[^0-9kK]/g, '').toUpperCase();
  return cleaned;
}

function formatRut(value) {
  const cleaned = normalizeRut(value);
  if (cleaned.length <= 1) return cleaned;
  const dv = cleaned.slice(-1);
  let body = cleaned.slice(0, -1);
  // Insertar puntos cada 3 desde el final
  let result = '';
  while (body.length > 3) {
    result = '.' + body.slice(-3) + result;
    body = body.slice(0, -3);
  }
  result = body + result + '-' + dv;
  return result;
}

async function handleRegister(e) {
  e.preventDefault();
  const nombre = document.getElementById('nombre').value.trim();
  const apellido = document.getElementById('apellido').value.trim();
  const rutInput = document.getElementById('rut').value.trim();
  const email = document.getElementById('email').value.trim();
  const telefono = document.getElementById('telefono').value.trim();
  const password = document.getElementById('password').value;
  const confirm_password = document.getElementById('confirm_password').value;

  const rutNorm = normalizeRut(rutInput);

  if (!nombre || !apellido || !rutNorm || !email || !telefono || !password || !confirm_password) {
    showStatus('Completa todos los campos requeridos', 'error');
    return;
  }
  if (password !== confirm_password) {
    showStatus('Las contraseñas no coinciden', 'error');
    return;
  }

  showLoading(true);
  showStatus('Creando tu cuenta...', 'info');

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const payload = {
      nombre,
      apellido,
      username: rutNorm, // compatibilidad OAuth2 (login por RUT)
      rut: rutNorm,
      email,
      telefono,
      password,
      confirm_password,
      role: 'cliente'
    };

    const response = await fetch(`${API_URL}/auth/register-and-login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const text = await response.text();
      let msg = `Error al registrar (${response.status})`;
      try {
        const data = JSON.parse(text);
        if (data.detail) msg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      } catch {}
      showStatus(msg, 'error');
      showLoading(false);
      return;
    }

    const data = await response.json();
    // Guardar token y usuario para autologin
    localStorage.setItem('token', data.access_token);
    const user = {
      id_usuario: data.id_usuario,
      nombre: data.nombre,
      username: data.username,
      rol: data.role
    };
    localStorage.setItem('user', JSON.stringify(user));

    showStatus(`Cuenta creada: ${formatRut(rutNorm)}. Iniciando sesión...`, 'success');
    setTimeout(() => { 
      if (user.rol === 'admin') {
        window.location.href = '/admin';
      } else {
        window.location.href = '/';
      }
    }, 1000);
  } catch (error) {
    const isTimeout = error.name === 'AbortError';
    showStatus(isTimeout ? 'Tiempo de espera agotado' : `Error: ${error.message}`, 'error');
  } finally {
    showLoading(false);
  }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registerForm');
  const googleButton = document.getElementById('googleButton');
  const rutEl = document.getElementById('rut');

  form?.addEventListener('submit', handleRegister);
  googleButton?.addEventListener('click', handleGoogleAuth);

  // Formatear RUT al escribir
  if (rutEl) {
    rutEl.addEventListener('input', (e) => {
      const pos = e.target.selectionStart;
      const formatted = formatRut(e.target.value);
      e.target.value = formatted;
      // Ajuste simple del cursor: mover al final
      e.target.selectionStart = e.target.selectionEnd = formatted.length;
    });
  }

  // Verificar callback de Google
  checkGoogleCallback();
});

async function handleGoogleAuth() {
  showGoogleLoading(true);
  showStatus('Redirigiendo a Google...', 'info');

  try {
    // El backend ahora realiza redirección directa
    window.location.href = `${API_URL}/auth/google`;
  } catch (error) {
    showStatus(`Error al conectar con Google: ${error.message}`, 'error');
    showGoogleLoading(false);
  }
}

// Verificar si hay parámetros de retorno de Google
function checkGoogleCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');
  const success = urlParams.get('success');
  const error = urlParams.get('error');

  if (success && token) {
    // Guardar token y redirigir
    localStorage.setItem('token', token);
    showStatus('¡Registro exitoso con Google! Redirigiendo...', 'success');
    setTimeout(() => {
      window.location.href = '/admin/dashboard';
    }, 1500);
  } else if (error) {
    showStatus(`Error en registro con Google: ${decodeURIComponent(error)}`, 'error');
    // Limpiar URL
    window.history.replaceState({}, document.title, window.location.pathname);
  }
}