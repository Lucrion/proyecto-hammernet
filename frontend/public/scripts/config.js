// Configuración centralizada de la API

// Detectar automáticamente el entorno (desarrollo o producción)
const isDevelopment = typeof window !== 'undefined' 
    ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    : false;

// URL base de la API - Variables globales
const API_URL = isDevelopment 
    ? '/api'
    : 'https://hammernet-backend.onrender.com';

// Configuración CORS para las peticiones fetch - Variables globales
const corsConfig = {
    credentials: 'include',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    },
    mode: 'cors'
};

// Timeout para peticiones (en milisegundos) - Variable global
const API_TIMEOUT = 10000;

/**
 * Función para verificar si el servidor está disponible
 * @returns {Promise<{available: boolean, message: string}>}
 */
async function checkServerAvailability() {
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
function handleApiError(error) {
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