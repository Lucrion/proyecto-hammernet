// Configuración de la API desde variables de entorno
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_URL = isDevelopment 
    ? (window.__ENV__?.PUBLIC_API_URL || 'http://localhost:8000/api')
    : (window.__ENV__?.PUBLIC_API_URL_PRODUCTION || 'https://hammernet-backend.onrender.com/api');

const corsConfig = {
    credentials: window.__ENV__?.PUBLIC_CORS_CREDENTIALS || 'include',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    },
    mode: window.__ENV__?.PUBLIC_CORS_MODE || 'cors'
};

const API_TIMEOUT = parseInt(window.__ENV__?.PUBLIC_API_TIMEOUT || '10000');

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

// Función principal de autenticación
async function handleLogin(e) {
    e.preventDefault();
    
    // Obtener los valores del formulario
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showStatus('Por favor, ingrese usuario y contraseña', 'error');
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
        
        const response = await fetch(`${API_URL}/auth/login`, fetchOptions);
        
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
            
            // Información específica para error 422
            if (response.status === 422) {
                console.error('Error 422 (Unprocessable Content): FastAPI está rechazando los datos enviados');
                console.error('Datos enviados:', formData.toString());
                console.error('Headers enviados:', fetchOptions.headers);
                console.error('URL completa:', `${API_URL}/login`);
                
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
        
        // Guardar estado de autenticación y token
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('nombreUsuario', username);
        localStorage.setItem('token', data.access_token);
        console.log('Token guardado:', data.access_token ? 'Token presente' : 'Token ausente');
        console.log('Autenticación exitosa');
        
        // Mostrar mensaje de éxito
        showStatus('Autenticación exitosa. Redirigiendo...', 'success');
        
        // Redirigir al panel de administración después de un breve retraso
        setTimeout(() => {
            window.location.href = '/admin';
        }, 1000);
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

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', async () => {
    const loginForm = document.getElementById('loginForm');
    
    // Verificar disponibilidad del servidor al cargar la página
    const serverStatus = await checkServerAvailability();
    if (!serverStatus.available) {
        console.warn('Servidor no disponible:', serverStatus.message);
        // Mostrar mensaje de error al usuario
        showStatus('El servidor no está disponible. Por favor, intente más tarde.', 'error');
        return;
    }
    
    // Agregar event listener al formulario
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});