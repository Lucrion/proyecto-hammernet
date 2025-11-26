// Funciones para comunicación con la API
import { API_URL, corsConfig, handleApiError, API_TIMEOUT } from './config.js';

// Construye URL robusta evitando doble "/api" y soportando endpoints absolutos
function buildUrl(endpoint) {
    const baseOrigin = API_URL.replace(/\/api$/, '');
    if (endpoint.startsWith('http')) {
        return endpoint;
    }
    if (endpoint.startsWith('/')) {
        return `${baseOrigin}${endpoint}`;
    }
    return `${API_URL}${endpoint}`;
}

/**
 * Realiza una petición autenticada a la API con soporte para FormData
 * @param {string} endpoint - Endpoint de la API (sin incluir la URL base)
 * @param {Object} options - Opciones de fetch (method, headers, body, etc.)
 * @returns {Promise<Response>} - Respuesta de la petición
 */
export async function fetchWithAuth(endpoint, options = {}) {
    try {
        // Obtener token desde sessionStorage y localStorage
        let token = '';
        try {
            token = sessionStorage.getItem('token') || localStorage.getItem('token') || localStorage.getItem('access_token') || '';
        } catch {}
        
        // Crear headers con autenticación
        const headers = options.headers || {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Si no es FormData, agregar Content-Type
        if (!(options.body instanceof FormData) && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }
        
        // Realizar la petición usando URL normalizada
        const url = buildUrl(endpoint);
        
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), Number(API_TIMEOUT || 10000));
            const response = await fetch(url, {
                ...options,
                headers,
                mode: corsConfig?.mode || 'cors',
                credentials: corsConfig?.credentials || 'include',
                signal: controller.signal
            });
            clearTimeout(timeout);
            
            return response;
        } catch (fetchError) {
            console.error(`Error de red en fetchWithAuth para ${endpoint}:`, fetchError);
            throw new Error('Error en conexión del servidor');
        }
    } catch (error) {
        console.error(`Error en fetchWithAuth para ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Realiza una petición GET autenticada a la API
 * @param {string} endpoint - Endpoint de la API (sin incluir la URL base)
 * @returns {Promise<any>} - Datos de la respuesta
 */
export async function getData(endpoint) {
    try {
        const response = await fetchWithAuth(endpoint, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error ${response.status}: ${errorText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`Error al obtener datos de ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Realiza una petición POST autenticada a la API
 * @param {string} endpoint - Endpoint de la API (sin incluir la URL base)
 * @param {Object} data - Datos a enviar en el cuerpo de la petición
 * @returns {Promise<any>} - Datos de la respuesta
 */
export async function postData(endpoint, data) {
    try {
        const response = await fetchWithAuth(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error ${response.status}: ${errorText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`Error al enviar datos a ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Realiza una petición PUT autenticada a la API
 * @param {string} endpoint - Endpoint de la API (sin incluir la URL base)
 * @param {Object} data - Datos a enviar en el cuerpo de la petición
 * @returns {Promise<any>} - Datos de la respuesta
 */
export async function updateData(endpoint, data) {
    try {
        const response = await fetchWithAuth(endpoint, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error en respuesta:', errorText);
            throw new Error(`Error ${response.status}: ${errorText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`Error al actualizar datos en ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Realiza una petición DELETE autenticada a la API
 * @param {string} endpoint - Endpoint de la API (sin incluir la URL base)
 * @returns {Promise<any>} - Datos de la respuesta
 */
export async function deleteData(endpoint) {
    try {
        const response = await fetchWithAuth(endpoint, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error ${response.status}: ${errorText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`Error al eliminar datos en ${endpoint}:`, error);
        throw error;
    }
}
