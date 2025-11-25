// Configuración centralizada
import { API_URL, corsConfig, API_TIMEOUT } from '../utils/config.js';
import { digitsOnly, formatRutUI, formatRutFromDigits } from '../utils/rut.js';
// Asegurar headers adecuados para este flujo
corsConfig.headers = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Accept': 'application/json'
};

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

// El backend espera sólo dígitos; la UI muestra puntos y guion con DV

// Función principal de autenticación
async function handleLogin(e) {
    e.preventDefault();
    
    // Detectar tipo de acceso (cliente/trabajador)
    const params = new URLSearchParams(window.location.search);
    const tipoSeleccionado = params.get('tipo') || localStorage.getItem('loginTipo');

    // Obtener los valores del formulario
    const usernameInput = document.getElementById('username').value.trim();
    const baseRut = usernameInput.includes('-') ? usernameInput.split('-')[0] : usernameInput;
    const username = digitsOnly(baseRut);
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
        
        let response = await fetch(`${API_URL}/auth/login`, fetchOptions);
        
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
            
            // Sin fallback: siempre enviamos sólo dígitos al backend

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
            
            if (response.status === 401) { errorMessage = 'Credenciales incorrectas'; }
            showStatus(errorMessage, 'error');
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
        const workerRoles = ['administrador','admin','trabajador','vendedor','bodeguero'];
        const isWorkerRole = workerRoles.includes(String(user.rol).toLowerCase());
        if ((tipoSeleccionado === 'trabajador') && !isWorkerRole) {
            showStatus('Acceso denegado: tu cuenta es de cliente y no corresponde el inicio como trabajador. Por favor usa el modo Cliente.', 'error');
            showLoading(false);
            return;
        }
        
        // Guardar estado de autenticación y token usando el nombre real
        const storage = (tipoSeleccionado === 'trabajador') ? window.sessionStorage : window.localStorage;
        storage.setItem('isLoggedIn', 'true');
        storage.setItem('token', data.access_token);
        storage.setItem('user', JSON.stringify(user));
        storage.setItem('role', user.rol);
        // Preferir el nombre real para mostrar en el header; si no viene, usar lo ingresado
        storage.setItem('nombreUsuario', user.nombre || formatRutFromDigits(user.rut));
        document.cookie = `isLoggedIn=true; path=/; SameSite=Lax`;
        document.cookie = `role=${encodeURIComponent(user.rol)}; path=/; SameSite=Lax`;
        document.cookie = `loginTipo=${encodeURIComponent(tipoSeleccionado || '')}; path=/; SameSite=Lax`;
        console.log('Token guardado:', data.access_token ? 'Token presente' : 'Token ausente');
        console.log('Autenticación exitosa');

        // Intentar obtener el usuario completo (email y teléfono) y actualizar storage
        try {
            const uResp = await fetch(`${API_URL}/usuarios/${user.id_usuario}`, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${data.access_token}`
                }
            });
            if (uResp.ok) {
                const fullUser = await uResp.json();
                if (fullUser && (fullUser.email || fullUser.telefono)) {
                    storage.setItem('user', JSON.stringify(fullUser));
                }
            } else {
                console.warn('No se pudo cargar usuario completo, status:', uResp.status);
            }
        } catch (err) {
            console.warn('Fallo al cargar usuario completo:', err);
        }
        
        // Mostrar mensaje de éxito
        showStatus('Autenticación exitosa. Redirigiendo...', 'success');
        
        const roleStr = String(user.rol || user.role || '').toLowerCase();
        const workerRolesArr = ['administrador','admin','trabajador','vendedor','bodeguero'];
        const allowWorker = workerRolesArr.includes(roleStr);
        const tipoFinal = tipoSeleccionado ? tipoSeleccionado : (allowWorker ? 'trabajador' : 'cliente');
        const destino = tipoFinal === 'trabajador' ? '/admin' : '/';
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
            showStatus('Credenciales incorrectas', 'error');
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

    // Auto-rellenar el RUT si hay usuario guardado (cliente o trabajador)
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
    
    // Formatear RUT al escribir en ambos modos (cliente y trabajador)
    if (usernameEl) {
        usernameEl.addEventListener('input', (e) => {
            const formatted = formatRutUI(e.target.value);
            e.target.value = formatted;
            e.target.selectionStart = e.target.selectionEnd = formatted.length;
        });
    }
    
    // Agregar event listener al botón de Google
    if (googleLoginButton) {
        googleLoginButton.addEventListener('click', handleGoogleAuth);
    }
});