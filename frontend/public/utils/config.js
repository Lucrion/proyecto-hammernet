// Configuración de la API (copia pública)
const isDevelopment = typeof window !== 'undefined' 
    ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    : false;

const getEnvVar = (name, defaultValue = undefined) => {
    if (typeof window !== 'undefined' && window.__ENV__) {
        return window.__ENV__[name] || defaultValue;
    }
    return defaultValue;
};

export const API_URL = isDevelopment 
    ? getEnvVar('PUBLIC_API_URL', 'http://localhost:8000/api')
    : getEnvVar('PUBLIC_API_URL_PRODUCTION', 'https://hammernet-backend.onrender.com');

export const corsConfig = {
    credentials: getEnvVar('PUBLIC_CORS_CREDENTIALS', 'include'),
    mode: getEnvVar('PUBLIC_CORS_MODE', 'cors')
};

export const API_TIMEOUT = parseInt(getEnvVar('PUBLIC_API_TIMEOUT', '10000'));

export async function checkServerAvailability() {
    try {
        const baseOrigin = API_URL.replace(/\/api$/, '');
        if (typeof window !== 'undefined' && baseOrigin === window.location.origin) {
            return {
                available: true,
                message: 'Modo desarrollo: verificación omitida'
            };
        }
        const response = await fetch(`${API_URL}/health`, { method: 'GET' });
        return {
            available: !!response && response.ok,
            message: (response && response.ok) ? 'Servidor disponible' : 'Servidor no disponible'
        };
    } catch (error) {
        console.warn('No se pudo verificar disponibilidad del servidor:', error?.message || error);
        return {
            available: false,
            message: 'Servidor no disponible'
        };
    }
}

export function handleApiError(error) {
    console.error('Error en la API:', error);
    if (!error) {
        return { type: 'unknown', message: 'Error desconocido', original: null };
    }
    if (error.name === 'AbortError') {
        return { type: 'timeout', message: 'Error en conexión del servidor', original: error };
    }
    if (error.name === 'TypeError' && error.message && error.message.includes('Failed to fetch')) {
        return { type: 'connection', message: 'Error en conexión del servidor', original: error };
    }
    if (error.message && (error.message.includes('fetch') || error.message.includes('network') || error.message.includes('conexión'))) {
        return { type: 'connection', message: 'Error en conexión del servidor', original: error };
    }
    if (error.status) {
        return { type: 'http', message: 'Error en conexión del servidor', original: error };
    }
    return { type: 'unknown', message: 'Error en conexión del servidor', original: error };
}