// Configuración de la API desde variables de entorno
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_URL = isDevelopment 
    ? (window.__ENV__?.PUBLIC_API_URL || 'http://localhost:8000/api')
    : (window.__ENV__?.PUBLIC_API_URL_PRODUCTION || 'https://hammernet.onrender.com/api');

const corsConfig = {
    credentials: window.__ENV__?.PUBLIC_CORS_CREDENTIALS || 'include',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    },
    mode: window.__ENV__?.PUBLIC_CORS_MODE || 'cors'
};

const API_TIMEOUT = parseInt(window.__ENV__?.PUBLIC_API_TIMEOUT || '10000');

// ===== Utilidades RUT (UI y envío) =====
function digitsOnly(value) {
    return String(value || '').replace(/\D/g, '');
}

// Limpiar entrada de RUT permitiendo solo dígitos y K/k, y limitar a 9 (cuerpo+DV)
function cleanRutInput(value) {
    return String(value ?? '')
        .replace(/[^0-9kK]/g, '')
        .toUpperCase()
        .slice(0, 9);
}

function computeRutDV(digits) {
    const body = digitsOnly(digits);
    if (!body) return '';
    let sum = 0;
    let factor = 2;
    for (let i = body.length - 1; i >= 0; i--) {
        sum += Number(body[i]) * factor;
        factor = factor === 7 ? 2 : factor + 1;
    }
    const rest = 11 - (sum % 11);
    if (rest === 11) return '0';
    if (rest === 10) return 'K';
    return String(rest);
}

function formatRutFromDigits(digits) {
    const body = digitsOnly(digits);
    if (!body) return '';
    const dv = computeRutDV(body);
    let result = '';
    let tmp = body;
    while (tmp.length > 3) {
        result = '.' + tmp.slice(-3) + result;
        tmp = tmp.slice(0, -3);
    }
    result = tmp + result + '-' + dv;
    return result;
}

// Función para verificar disponibilidad del servidor
async function checkServerAvailability() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT / 2);
        
        const response = await fetch(`${API_URL}/health`, {
            method: 'GET',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        return {
            available: response.ok,
            message: 'Servidor disponible'
        };
    } catch (error) {
        console.error('Error al verificar disponibilidad del servidor:', error);
        
        return {
            available: false,
            message: error.name === 'AbortError' 
                ? 'Tiempo de espera agotado al conectar con el servidor' 
                : `Error de conexión: ${error.message}`
        };
    }
}

// Función para manejar errores de la API
function handleApiError(error) {
    console.error('Error en la API:', error);
    
    if (error.name === 'AbortError') {
        return {
            type: 'timeout',
            message: 'La solicitud ha excedido el tiempo de espera',
            original: error
        };
    }
    
    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        return {
            type: 'connection',
            message: 'No se pudo conectar con el servidor',
            original: error
        };
    }
    
    return {
        type: 'unknown',
        message: error.message || 'Error desconocido',
        original: error
    };
}

// Función para mostrar mensajes de estado
function showStatus(message, type = 'info') {
    const statusMessage = document.getElementById('statusMessage');
    statusMessage.textContent = message;
    statusMessage.className = 'mt-2 text-sm text-center';
    
    switch(type) {
        case 'error':
            statusMessage.classList.add('text-red-600');
            break;
        case 'success':
            statusMessage.classList.add('text-green-600');
            break;
        case 'warning':
            statusMessage.classList.add('text-yellow-600');
            break;
        default:
            statusMessage.classList.add('text-gray-600');
    }
    
    statusMessage.classList.remove('hidden');
}

// Función para mostrar el indicador de carga
function showLoading(isLoading) {
    const loginButton = document.getElementById('loginButton');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    if (isLoading) {
        loadingSpinner.classList.remove('hidden');
        loginButton.disabled = true;
        loginButton.classList.add('opacity-75');
    } else {
        loadingSpinner.classList.add('hidden');
        loginButton.disabled = false;
        loginButton.classList.remove('opacity-75');
    }
}

function normalizeRut(value) {
    if (!value) return '';
    const cleaned = value.replace(/[^0-9kK]/g, '').toUpperCase();
    // Reconstruir poniendo guion antes del dígito verificador
    if (cleaned.length >= 2) {
        const dv = cleaned.slice(-1);
        const body = cleaned.slice(0, -1);
        return `${body}-${dv}`;
    }
    return cleaned;
}

function formatRut(value) {
    const cleaned = cleanRutInput(value);
    if (!cleaned) return '';
    if (cleaned.length === 1) return cleaned;
    const dv = cleaned.slice(-1);
    let body = cleaned.slice(0, -1);
    // Limitar cuerpo a 8 dígitos para cumplir máximo total 9 (incluye DV)
    body = body.slice(0, 8);
    let result = '';
    while (body.length > 3) {
        result = '.' + body.slice(-3) + result;
        body = body.slice(0, -3);
    }
    result = body + result + '-' + dv;
    return result;
}

// Función principal de autenticación
async function handleLogin(e) {
    e.preventDefault();
    
    // Detectar tipo de acceso (cliente/trabajador)
    const params = new URLSearchParams(window.location.search);
    const tipoSeleccionado = params.get('tipo') || localStorage.getItem('loginTipo');

    // Obtener los valores del formulario
    const usernameInput = document.getElementById('username').value.trim();
    const isTrabajador = (tipoSeleccionado === 'trabajador');
    const cleaned = cleanRutInput(usernameInput);
    if (!cleaned || cleaned.length < 2) { showStatus('RUT inválido', 'error'); return; }
    const body = cleaned.slice(0, -1);
    let username = body;
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showStatus('Por favor, ingrese RUT y contraseña', 'error');
        return;
    }
    
    // Mostrar indicador de carga
    showLoading(true);
    showStatus('Verificando credenciales...', 'info');
    
    // Verificar disponibilidad del servidor antes de intentar autenticar
    const serverAvailable = await checkServerAvailability();
    if (!serverAvailable.available) {
        showStatus('El servidor no está disponible. Por favor, intente más tarde.', 'error');
        showLoading(false);
        return;
    }
    
    try {
        // Crear un controlador de tiempo de espera
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 segundos de timeout

        // Intentar autenticar a través de la API
        console.log('Intentando conectar a:', `${API_URL}/login`);
        showStatus('Conectando con el servidor...', 'info');
        
        // Configurar opciones de fetch para OAuth2 password flow
        // FastAPI OAuth2 espera exactamente 'username' y 'password' como campos de formulario
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('grant_type', 'password'); // Requerido por el estándar OAuth2
        console.log('Datos del formulario:', formData.toString());
        
        const fetchOptions = {
            method: 'POST',
            body: formData,
            signal: controller.signal,
            ...corsConfig
        };
        
        const loginEndpoint = (tipoSeleccionado === 'trabajador') ? 'login-trabajador' : 'login-cliente';
        let response = await fetch(`${API_URL}/auth/${loginEndpoint}`, fetchOptions);
        
        // Limpiar el timeout ya que la solicitud se completó
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            console.error('Error en la respuesta:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Contenido de la respuesta de error:', errorText);
            
            // Mostrar información detallada para depuración
            console.error('Detalles completos del error:');
            console.error('- Status:', response.status);
            console.error('- Status Text:', response.statusText);
            console.error('- URL:', response.url);
            console.error('- Headers:', [...response.headers.entries()]);
            
            // Sin fallback por email: solo RUT permitido

            // Información específica para error 422
            if (response.status === 422) {
                console.error('Error 422 (Unprocessable Content): FastAPI está rechazando los datos enviados');
                console.error('Datos enviados:', formData.toString());
                console.error('Headers enviados:', fetchOptions.headers);
                console.error('URL completa:', `${API_URL}/auth/login`);

                // Intentar obtener más información sobre el error
                console.error('Método HTTP:', fetchOptions.method);
                console.error('Cuerpo de la solicitud:', fetchOptions.body);
            }
            
            let errorMessage = `Error de autenticación (${response.status})`;
            try {
                const errorData = JSON.parse(errorText);
                console.error('Error parseado:', errorData);
                
                // Manejar diferentes formatos de error
                if (errorData.detail) {
                    errorMessage = typeof errorData.detail === 'string' 
                        ? errorData.detail 
                        : JSON.stringify(errorData.detail);
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                } else {
                    errorMessage = JSON.stringify(errorData);
                }
            } catch (e) {
                console.error('No se pudo parsear la respuesta como JSON:', e);
                errorMessage += ` - Respuesta: ${errorText.substring(0, 100)}${errorText.length > 100 ? '...' : ''}`;
            }
            
            // Para error 422, añadir información más específica
            if (response.status === 422) {
                errorMessage = `Error 422: Datos no procesables. ${errorMessage}. Verifique la consola para más detalles.`;
            }
            
            showStatus(`Error: ${errorMessage}`, 'error');
            showLoading(false);
            return; // Detener la ejecución en lugar de lanzar un error
        }
        
        const data = await response.json();
        console.log('Respuesta de autenticación:', JSON.stringify(data));

        // Construir objeto de usuario desde el token devuelto por el backend
        const user = {
            id_usuario: data.id_usuario,
            nombre: data.nombre,
            rut: data.rut ?? digitsOnly(usernameInput),
            rol: data.role || data.rol || 'cliente'
        };
        
        // Guardar estado de autenticación y token usando el nombre real
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('role', user.rol);
        // Preferir el nombre real para mostrar en el header; si no viene, usar lo ingresado
        localStorage.setItem('nombreUsuario', user.nombre || formatRutFromDigits(user.rut));
        console.log('Token guardado:', data.access_token ? 'Token presente' : 'Token ausente');
        console.log('Autenticación exitosa');
        
        // Mostrar mensaje de éxito
        showStatus('Autenticación exitosa. Redirigiendo...', 'success');
        
        // Redirigir según tipo seleccionado (cliente/trabajador)
        const tipoFinal = tipoSeleccionado || (user.rol === 'administrador' ? 'trabajador' : 'cliente');
        const destino = tipoFinal === 'cliente' ? '/' : '/admin';
        setTimeout(() => {
            window.location.href = destino;
        }, 800);
    } catch (error) {
        // Limpiar el timeout si existe
        if (typeof timeoutId !== 'undefined') {
            clearTimeout(timeoutId);
        }
        
        // Ocultar indicador de carga
        showLoading(false);
        
        console.error('Error de autenticación:', error);
        
        // Procesar el error para obtener información detallada
        const errorInfo = handleApiError(error);
        
        // Mostrar mensaje de error específico
        if (error.message && (error.message.includes('credenciales') || error.message.includes('credentials'))) {
            showStatus('Las credenciales son incorrectas. Por favor verifique su usuario y contraseña.', 'error');
        } else {
            showStatus('Error de autenticación: ' + errorInfo.message, 'error');
        }
    }
}

// Función para mostrar/ocultar loading del botón de Google
function showGoogleLoading(isLoading) {
    const googleButton = document.getElementById('googleLoginButton');
    const googleSpinner = document.getElementById('googleLoginLoadingSpinner');
    
    if (googleButton && googleSpinner) {
        if (isLoading) {
            googleButton.disabled = true;
            googleSpinner.classList.remove('hidden');
        } else {
            googleButton.disabled = false;
            googleSpinner.classList.add('hidden');
        }
    }
}

// Función para manejar autenticación con Google
async function handleGoogleAuth() {
    try {
        showGoogleLoading(true);
        showStatus('Redirigiendo a Google...', 'info');
        
        // Redirigir al endpoint de Google OAuth
        window.location.href = `${API_URL}/auth/google`;
    } catch (error) {
        console.error('Error al iniciar autenticación con Google:', error);
        showStatus('Error al conectar con Google. Inténtalo de nuevo.', 'error');
        showGoogleLoading(false);
    }
}

// Función para verificar si venimos del callback de Google
function checkGoogleCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const error = urlParams.get('error');
    
    if (token) {
        // Guardar el token y redirigir
        localStorage.setItem('token', token);
        showStatus('¡Inicio de sesión exitoso con Google!', 'success');
        
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1000);
        
        return true;
    } else if (error) {
        showStatus(`Error de autenticación: ${error}`, 'error');
        // Limpiar la URL
        window.history.replaceState({}, document.title, window.location.pathname);
        return true;
    }
    
    return false;
}

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', async () => {
    const loginForm = document.getElementById('loginForm');
    const googleLoginButton = document.getElementById('googleLoginButton');
    const usernameEl = document.getElementById('username');
    const usernameLabel = document.getElementById('usernameLabel');
    const createAccountContainer = document.getElementById('createAccountContainer');
    
    // Verificar si venimos del callback de Google
    if (checkGoogleCallback()) {
        return; // Si es un callback, no continuar con la inicialización normal
    }
    
    // Ocultar botón "Crear cuenta" si el modo es trabajador
    const params = new URLSearchParams(window.location.search);
    const tipoSeleccionado = params.get('tipo') || localStorage.getItem('loginTipo');
    if (tipoSeleccionado === 'trabajador' && createAccountContainer) {
        createAccountContainer.classList.add('hidden');
    }

    // Ajustar etiqueta y placeholder: ambos modos usan RUT
    if (usernameLabel) usernameLabel.textContent = 'RUT';
    if (usernameEl) usernameEl.placeholder = '20.347.793-7';

    // Auto-rellenar desde storage si existe usuario
    try {
        const storagePrimary = (tipoSeleccionado === 'trabajador') ? window.sessionStorage : window.localStorage;
        const storageSecondary = (tipoSeleccionado === 'trabajador') ? window.localStorage : window.sessionStorage;
        const userStr = storagePrimary.getItem('user') || storageSecondary.getItem('user');
        if (userStr && usernameEl) {
            const u = JSON.parse(userStr);
            const rutDigits = (u && u.rut) || '';
            if (rutDigits) {
                usernameEl.value = formatRutFromDigits(rutDigits);
            }
        }
    } catch (e) {
        console.warn('No se pudo auto-rellenar el RUT:', e);
    }

    // Verificar disponibilidad del servidor al cargar la página
    const serverStatus = await checkServerAvailability();
    if (!serverStatus.available) {
        // Mostrar aviso, pero no bloquear el login
        showStatus('No se pudo verificar el servidor. Puedes intentar iniciar sesión.', 'info');
    }

    // Agregar event listener al formulario
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Formatear RUT al escribir en ambos modos
    if (usernameEl) {
        usernameEl.addEventListener('input', (e) => {
            const formatted = formatRut(e.target.value);
            e.target.value = formatted;
            e.target.selectionStart = e.target.selectionEnd = formatted.length;
        });
        // Opcional: limitar la longitud visual máxima según el formato (hasta 13 chars)
        try { usernameEl.maxLength = 13; } catch {}
    }
    
    // Agregar event listener al botón de Google
    if (googleLoginButton) {
        googleLoginButton.addEventListener('click', handleGoogleAuth);
    }
});
