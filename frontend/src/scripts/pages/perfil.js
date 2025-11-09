import { getData, postData, updateData } from '../utils/api.js';
import { normalizePhoneCL, stripCLPrefix, formatPhoneUI } from '../utils/phone.js';
import { digitsOnly, formatRutUI, formatRutFromDigits } from '../utils/rut.js';

const estado = {
  user: null,
  editablePerfil: false,
  editableDespacho: false,
};

function getAuth() {
  try {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return { token, user };
  } catch {
    return { token: null, user: {} };
  }
}

function setInputsDisabled(formEl, disabled) {
  formEl.querySelectorAll('input, textarea').forEach((el) => {
    el.disabled = disabled;
    if (disabled) {
      el.classList.add('bg-gray-100');
    } else {
      el.classList.remove('bg-gray-100');
    }
  });
}

function loadPerfil() {
  const { token, user } = getAuth();
  estado.user = user;
  const id = user?.id_usuario;
  const status = document.getElementById('perfilStatus');
  // Si no hay id, solo intenta llenar con localStorage
  const fill = (u) => {
    document.getElementById('perfilNombre').value = u?.nombre || '';
    document.getElementById('perfilApellido').value = u?.apellido || '';
    document.getElementById('perfilRut').value = formatRutFromDigits(u?.rut || '');
    document.getElementById('perfilEmail').value = u?.email || '';
    document.getElementById('perfilTelefono').value = stripCLPrefix(u?.telefono || '');
  };
  fill(user || {});
  setInputsDisabled(document.getElementById('perfilForm'), true);

  if (!id) return;
  // Cargar desde backend para ver datos completos
  (async () => {
    try {
      const data = await getData(`/api/usuarios/${id}`);
      // Actualiza localStorage con datos completos
      const merged = { ...(user || {}), ...data };
      localStorage.setItem('user', JSON.stringify(merged));
      estado.user = merged;
      fill(merged);
    } catch (err) {
      console.warn('No se pudo cargar perfil desde backend:', err);
      status.textContent = 'No se pudo cargar datos completos de perfil.';
    }
  })();
}

function storageKeyDespacho(userId) {
  return `perfilDireccion_${userId || 'anon'}`;
}

function loadDespacho() {
  const { token, user } = getAuth();
  // 1) Intentar cargar desde la API
  let data = {};
  const userId = user?.id_usuario;
  const status = document.getElementById('despachoStatus');
  // Limpieza proactiva: eliminar cualquier dirección guardada localmente
  try {
    localStorage.removeItem('checkoutDireccion');
    if (userId) localStorage.removeItem(storageKeyDespacho(userId));
  } catch {}
  const applyDataToForm = (d) => {
    const buscar = document.getElementById('dir-buscar');
    const calle = document.getElementById('dir-calle');
    const numero = document.getElementById('dir-numero');
    const depto = document.getElementById('dir-depto');
    const adicional = document.getElementById('dir-adicional');
    if (buscar) buscar.value = d.buscar || '';
    if (calle) calle.value = d.calle || '';
    if (numero) numero.value = d.numero || '';
    if (depto) depto.value = d.depto || '';
    if (adicional) adicional.value = d.adicional || '';
  };

  const loadFromApi = async () => {
    if (!userId) return null;
    try {
      const list = await getData(`/api/despachos/usuario/${userId}`);
      // Usar el último por fecha (la API ya ordena desc)
      const last = Array.isArray(list) && list.length > 0 ? list[0] : null;
      return last;
    } catch (err) {
      console.warn('No se pudo cargar despacho desde backend:', err);
      return null;
    }
  };

  (async () => {
    const fromApi = await loadFromApi();
    if (fromApi) {
      data = {
        buscar: fromApi.buscar,
        calle: fromApi.calle,
        numero: fromApi.numero,
        depto: fromApi.depto,
        adicional: fromApi.adicional,
      };
      // No almacenar direcciones de despacho en localStorage
    } else {
      // Sin datos del backend, dejar el formulario vacío
      data = {};
    }

    applyDataToForm(data || {});

    const iframe = document.getElementById('map-iframe');
    if (iframe) {
      const q = document.getElementById('dir-buscar')?.value?.trim();
      const base = 'https://www.google.com/maps?q=';
      const ciudad = 'Calama';
      const query = q ? encodeURIComponent(`${q}, ${ciudad}`) : encodeURIComponent(ciudad);
      iframe.src = `${base}${query}&hl=es&gl=cl&output=embed`;
    }

    setInputsDisabled(document.getElementById('despachoForm'), true);
  })();
}

async function guardarPerfil(e) {
  e.preventDefault();
  const status = document.getElementById('perfilStatus');
  const { token, user } = getAuth();
  const id = user?.id_usuario;
  if (!id) {
    status.textContent = 'No se encontró el ID del usuario.';
    return;
  }

  const digitsRut = digitsOnly(document.getElementById('perfilRut').value.trim());
  const payload = {
    nombre: document.getElementById('perfilNombre').value.trim(),
    apellido: document.getElementById('perfilApellido').value.trim(),
    rut: digitsRut ? Number(digitsRut) : undefined,
    email: document.getElementById('perfilEmail').value.trim(),
    telefono: normalizePhoneCL(document.getElementById('perfilTelefono').value.trim()),
  };
  const nuevaPassword = document.getElementById('perfilPassword').value.trim();
  if (nuevaPassword) payload.password = nuevaPassword;

  status.textContent = 'Guardando perfil...';
  try {
    const data = await updateData(`/api/usuarios/${id}`, payload);
    // Actualiza localStorage
    const updatedUser = { ...user, ...payload };
    localStorage.setItem('user', JSON.stringify(updatedUser));
    estado.user = updatedUser;
    setInputsDisabled(document.getElementById('perfilForm'), true);
    estado.editablePerfil = false;
    status.textContent = 'Perfil guardado correctamente.';
    // Limpiar campo de contraseña para evitar retenerla en UI
    document.getElementById('perfilPassword').value = '';
  } catch (err) {
    console.error(err);
    status.textContent = 'No se pudo guardar el perfil.';
  }
}

async function guardarDespacho(e) {
  e.preventDefault();
  const status = document.getElementById('despachoStatus');
  const { token, user } = getAuth();
  const keyUser = storageKeyDespacho(user?.id_usuario);
  const userId = user?.id_usuario;

  const payload = {
    buscar: document.getElementById('dir-buscar').value.trim(),
    calle: document.getElementById('dir-calle').value.trim(),
    numero: document.getElementById('dir-numero').value.trim(),
    depto: document.getElementById('dir-depto').value.trim(),
    adicional: document.getElementById('dir-adicional').value.trim(),
  };

  if (!payload.buscar || !payload.calle || !payload.numero) {
    status.textContent = 'Calle, número y la dirección buscada son obligatorios.';
    return;
  }

  status.textContent = 'Guardando despacho...';
  // 1) Guardar en backend si hay usuario
  let savedOk = false;
  if (userId) {
    try {
      await postData(`/api/despachos/usuario/${userId}`, payload);
      savedOk = true;
    } catch (err) {
      console.warn('Falla al guardar en backend:', err);
    }
  }

  // No guardar direcciones de despacho en localStorage
  try {
    localStorage.removeItem('checkoutDireccion');
    if (userId) localStorage.removeItem(keyUser);
  } catch {}

  setInputsDisabled(document.getElementById('despachoForm'), true);
  estado.editableDespacho = false;
  status.textContent = 'Guardado.';
}

const buscarEnMapa = () => {
  const q = document.getElementById('dir-buscar')?.value?.trim();
  const iframe = document.getElementById('map-iframe');
  if (!iframe) return;
  const base = 'https://www.google.com/maps?q=';
  const ciudad = 'Calama';
  const query = q ? encodeURIComponent(`${q}, ${ciudad}`) : encodeURIComponent(ciudad);
  iframe.src = `${base}${query}&hl=es&gl=cl&output=embed`;
};

function initEventos() {
  const btnEditarPerfil = document.getElementById('btnEditarPerfil');
  const btnGuardarPerfil = document.getElementById('btnGuardarPerfil');
  const btnEditarDespacho = document.getElementById('btnEditarDespacho');
  const btnGuardarDespacho = document.getElementById('btnGuardarDespacho');

  btnEditarPerfil.addEventListener('click', () => {
    estado.editablePerfil = !estado.editablePerfil;
    setInputsDisabled(document.getElementById('perfilForm'), !estado.editablePerfil);
    document.getElementById('perfilStatus').textContent = estado.editablePerfil ? 'Modo edición activo.' : '';
  });
  btnGuardarPerfil.addEventListener('click', guardarPerfil);

  btnEditarDespacho.addEventListener('click', () => {
    estado.editableDespacho = !estado.editableDespacho;
    setInputsDisabled(document.getElementById('despachoForm'), !estado.editableDespacho);
    document.getElementById('despachoStatus').textContent = estado.editableDespacho ? 'Modo edición activo.' : '';
  });
  btnGuardarDespacho.addEventListener('click', guardarDespacho);
}

document.addEventListener('DOMContentLoaded', () => {
  loadPerfil();
  loadDespacho();
  loadGoogleMaps();
  initEventos();
  // Formatear RUT al escribir (puntos y guion con DV)
  const rutEl = document.getElementById('perfilRut');
  const telEl = document.getElementById('perfilTelefono');
  if (rutEl) {
    rutEl.addEventListener('input', (e) => {
      const formatted = formatRutUI(e.target.value);
      e.target.value = formatted;
    });
  }
  if (telEl) {
    telEl.addEventListener('input', (e) => {
      const formatted = formatPhoneUI(e.target.value);
      e.target.value = formatted;
    });
  }
});

// Integración Google Places Autocomplete (igual a carrito)
let placesAutocomplete;
const initPlacesAutocomplete = () => {
  const input = document.getElementById('dir-buscar');
  if (!input || !window.google || !google.maps.places) return;
  const centerCalama = new google.maps.LatLng(-22.455, -68.929);
  const circle = new google.maps.Circle({ center: centerCalama, radius: 20000 });
  const options = {
    fields: ['address_components','geometry','formatted_address'],
    types: ['address'],
    componentRestrictions: { country: 'cl' },
    bounds: circle.getBounds(),
  };
  placesAutocomplete = new google.maps.places.Autocomplete(input, options);
  placesAutocomplete.addListener('place_changed', () => {
    const place = placesAutocomplete.getPlace();
    if (!place || !place.address_components) return;
    const comps = place.address_components;
    const get = (type) => comps.find(c => c.types.includes(type))?.long_name || '';
    const calle = get('route');
    const numero = get('street_number');
    if (calle) {
      const calleEl = document.getElementById('dir-calle');
      if (calleEl) calleEl.value = calle;
    }
    if (numero) {
      const numEl = document.getElementById('dir-numero');
      if (numEl) numEl.value = numero;
    }
    if (place.geometry?.location) {
      const lat = place.geometry.location.lat();
      const lng = place.geometry.location.lng();
      const iframe = document.getElementById('map-iframe');
      if (iframe) iframe.src = `https://www.google.com/maps?q=${lat},${lng}&z=16&hl=es&gl=cl&output=embed`;
    } else {
      buscarEnMapa();
    }
  });
};

const loadGoogleMaps = () => {
  try {
    if (window.google && google.maps && google.maps.places) { initPlacesAutocomplete(); return; }
  } catch {}
  const key = window.GOOGLE_MAPS_API_KEY || '';
  if (!key) { console.warn('Google Maps API key no disponible en window.GOOGLE_MAPS_API_KEY'); return; }
  const s = document.createElement('script');
  s.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(key)}&libraries=places&language=es&region=CL`;
  s.async = true;
  s.onload = initPlacesAutocomplete;
  document.head.appendChild(s);
};

// Utilidades RUT ahora provienen de ../utils/rut.js

// Exponer funciones necesarias para handlers inline
window.buscarEnMapa = buscarEnMapa;