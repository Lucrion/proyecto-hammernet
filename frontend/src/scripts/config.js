// Configuración centralizada de la API

// Detectar automáticamente el entorno (desarrollo o producción)
const isDevelopment = typeof window !== 'undefined' 
    ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    : import.meta.env.MODE === 'development' || import.meta.env.PUBLIC_ENVIRONMENT === 'development';

// URL base de la API desde variables de entorno
export const API_URL = isDevelopment 
    ? import.meta.env.PUBLIC_API_URL
    : import.meta.env.PUBLIC_API_URL_PRODUCTION;

// Configuración CORS para las peticiones fetch desde variables de entorno
export const corsConfig = {
    credentials: import.meta.env.PUBLIC_CORS_CREDENTIALS,
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    },
    mode: import.meta.env.PUBLIC_CORS_MODE
};

// Timeout para peticiones desde variables de entorno
export const API_TIMEOUT = parseInt(import.meta.env.PUBLIC_API_TIMEOUT);

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