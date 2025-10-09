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
    ? getEnvVar('PUBLIC_API_URL', 'http://localhost:8000')
    : getEnvVar('PUBLIC_API_URL_PRODUCTION', 'https://hammernet-backend.onrender.com');

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
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT / 2); // Usar la mitad del timeout configurado
        
        const response = await fetch(`${API_URL}/docs`, {
            method: 'HEAD',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        return {
            available: true,
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

/**
 * Función para manejar errores de la API de forma consistente
 * @param {Error} error - El error capturado
 * @returns {Object} Información estructurada del error
 */
export function handleApiError(error) {
    console.error('Error en la API:', error);
    
    // Determinar el tipo de error
    if (error.name === 'AbortError') {
        return {
            type: 'timeout',
            message: 'Error en conexión del servidor',
            original: error
        };
    }
    
    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
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