// Funciones para el manejo del formulario de contacto
import { postData, getData } from '../utils/api.js';
import { API_URL } from '../utils/config.js';

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contactForm');
    const charCount = document.getElementById('charCount');
    const mensajeTextarea = document.getElementById('mensaje');
    const nombreEl = document.getElementById('nombre');
    const apellidoEl = document.getElementById('apellido');
    const emailEl = document.getElementById('email');
    
    const getAuth = () => {
        try {
            const token = localStorage.getItem('token') || localStorage.getItem('access_token') || '';
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            return { token, user };
        } catch { return { token: '', user: {} }; }
    };

    // API base centralizada
    const computeApiUrl = () => API_URL;

    const lockPersonalFieldsIfApplicable = () => {
        const { token, user } = getAuth();
        const hasSession = !!token || !!(user && user.id_usuario);
        if (!hasSession) return;
        // Solo bloquear si hay valor (evita dejar campos vacíos e ineditables)
        [nombreEl, apellidoEl, emailEl].forEach((el) => {
            if (el && el.value && el.value.trim()) {
                el.readOnly = true;
                el.classList.add('bg-gray-100', 'cursor-not-allowed');
                el.setAttribute('title', 'Campo bloqueado por sesión activa');
            }
        });
    };
    // Prefill desde sesión si existe (local)
    try {
        const { user } = getAuth();
        if (user && (user.id_usuario || user.id)) {
            if (nombreEl) nombreEl.value = user.nombre || nombreEl.value || '';
            if (apellidoEl) apellidoEl.value = user.apellido || apellidoEl.value || '';
            if (emailEl) emailEl.value = user.email || emailEl.value || '';
        }
    } catch {}
    // Intentar bloquear edición tras prefill local
    lockPersonalFieldsIfApplicable();

    // Prefill consultando el backend si hay token e id_usuario
    (async () => {
        try {
            const { token, user } = getAuth();
            const id = user && (user.id_usuario || user.id);
            if (!token || !id) return;

            const data = await getData(`/api/usuarios/${id}`);
            if (nombreEl && data?.nombre) nombreEl.value = data.nombre;
            if (apellidoEl && data?.apellido) apellidoEl.value = data.apellido;
            if (emailEl && data?.email) emailEl.value = data.email;
            // Bloquear edición tras prefill desde backend
            lockPersonalFieldsIfApplicable();
        } catch (e) { /* silencioso */ }
    })();
    
    // Actualizar contador de caracteres
    if (mensajeTextarea && charCount) {
        mensajeTextarea.addEventListener('input', function() {
            const currentLength = mensajeTextarea.value.length;
            charCount.textContent = `${currentLength}/500`;
        });
    }
    
    // Manejar envío del formulario
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Mostrar indicador de carga
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Enviando...';
            
            try {
                // Recopilar y validar datos del formulario
                const formData = {
                    nombre: document.getElementById('nombre').value.trim(),
                    apellido: document.getElementById('apellido').value.trim(),
                    email: document.getElementById('email').value.trim(),
                    asunto: document.getElementById('asunto').value.trim(),
                    mensaje: document.getElementById('mensaje').value.trim()
                };
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!formData.nombre || formData.nombre.length < 2) throw new Error('El nombre debe tener al menos 2 caracteres');
                if (!formData.apellido || formData.apellido.length < 2) throw new Error('El apellido debe tener al menos 2 caracteres');
                if (!emailRegex.test(formData.email)) throw new Error('El correo electrónico no es válido');
                if (!formData.asunto || formData.asunto.length < 5) throw new Error('El asunto debe tener al menos 5 caracteres');
                if (!formData.mensaje || formData.mensaje.length < 10) throw new Error('El mensaje debe tener al menos 10 caracteres');
                
                // Enviar datos a la API usando utilidad que normaliza la URL
                const result = await postData('/api/mensajes/', formData);
                
                if (!result) {
                    throw new Error('Error al enviar el mensaje');
                }
                
                // Mostrar mensaje de éxito
                alert('¡Gracias por tu mensaje! Te contactaremos pronto.');
                
                // Resetear formulario
                form.reset();
                if (charCount) charCount.textContent = '0/500';
                
            } catch (error) {
                console.error('Error al enviar mensaje:', error);
                let msg = 'Error en conexión del servidor';
                const text = String(error && error.message ? error.message : '');
                try {
                    const jsonStr = text.replace(/^Error\s+\d+:\s+/, '');
                    const data = JSON.parse(jsonStr);
                    if (data && data.detail) {
                        msg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
                    }
                } catch {
                    if (text) msg = text;
                }
                alert(msg);
            } finally {
                // Restaurar botón
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText;
            }
        });
    }
});
