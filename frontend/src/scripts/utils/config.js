// Configuración de la API usando variables de entorno
const isDevelopment = typeof window !== 'undefined' 
    ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    : false;

// Obtener variables de entorno con valores por defecto
const getEnvVar = (name, defaultValue = undefined) => {
    if (typeof window !== 'undefined' && window.__ENV__) {
        return window.__ENV__[name] || defaultValue;
    }
    return defaultValue;
};

// Configuración de la API
export const API_URL = isDevelopment 
    ? getEnvVar('PUBLIC_API_URL', 'http://localhost:8000/api')
    : getEnvVar('PUBLIC_API_URL_PRODUCTION', 'https://hammernet-backend.onrender.com/api');

// Configuración de CORS
export const corsConfig = {
    credentials: getEnvVar('PUBLIC_CORS_CREDENTIALS', 'include'),
    mode: getEnvVar('PUBLIC_CORS_MODE', 'cors')
};

// Configuración de timeout
export const API_TIMEOUT = parseInt(getEnvVar('PUBLIC_API_TIMEOUT', '10000'));

/**
 * Función para verificar si el servidor está disponible
 * @returns {Promise<{available: boolean, message: string}>}
 */
export async function checkServerAvailability() {
    try {
        const baseOrigin = API_URL.replace(/\/api$/, '');
        // Si el origen de la API coincide con el origen del frontend, omitir verificación
        if (typeof window !== 'undefined' && baseOrigin === window.location.origin) {
            return {
                available: true,
                message: 'Modo desarrollo: verificación omitida'
            };
        }
        // Ping estable del backend en cualquier entorno
        const response = await fetch(`${API_URL}/health`, { method: 'GET' });
        return {
            available: !!response && response.ok,
            message: (response && response.ok) ? 'Servidor disponible' : 'Servidor no disponible'
        };
    } catch (error) {
        // No usar console.error para evitar ruido en el navegador
        console.warn('No se pudo verificar disponibilidad del servidor:', error?.message || error);
        return {
            available: false,
            message: 'Servidor no disponible'
        };
    }
}

/**
 * Función para manejar errores de la API de forma consistente
 * @param {Error} error - El error capturado
 * @returns {Object} Información estructurada del error
 */
export function handleApiError(error) {
    console.error('Error en la API:', error);
    
    // Verificar si error es válido
    if (!error) {
        return {
            type: 'unknown',
            message: 'Error desconocido',
            original: null
        };
    }
    
    // Determinar el tipo de error
    if (error.name === 'AbortError') {
        return {
            type: 'timeout',
            message: 'Error en conexión del servidor',
            original: error
        };
    }
    
    if (error.name === 'TypeError' && error.message && error.message.includes('Failed to fetch')) {
        return {
            type: 'connection',
            message: 'Error en conexión del servidor',
            original: error
        };
    }
    
    // Para errores de red o conexión
    if (error.message && (error.message.includes('fetch') || error.message.includes('network') || error.message.includes('conexión'))) {
        return {
            type: 'connection',
            message: 'Error en conexión del servidor',
            original: error
        };
    }
    
    // Para errores HTTP específicos
    if (error.status) {
        return {
            type: 'http',
            message: 'Error en conexión del servidor',
            original: error
        };
    }
    
    return {
        type: 'unknown',
        message: 'Error en conexión del servidor',
        original: error
    };
}