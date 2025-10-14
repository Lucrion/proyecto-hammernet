// Funciones para comunicación con la API
import { API_URL, corsConfig, handleApiError } from './config.js';

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
        // TODO: Reactivar validación de token después del desarrollo
        // const token = localStorage.getItem('token');
        // if (!token) {
        //     throw new Error('No hay token de autenticación');
        // }
        
        // Crear headers con autenticación
        const headers = options.headers || {};
        // TODO: Reactivar autorización
        // headers['Authorization'] = `Bearer ${token}`;
        
        // Si no es FormData, agregar Content-Type
        if (!(options.body instanceof FormData) && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }
        
        // Realizar la petición usando URL normalizada
        const url = buildUrl(endpoint);
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
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
        // TODO: Reactivar validación de token después del desarrollo
        // const token = localStorage.getItem('token');
        // if (!token) {
        //     throw new Error('No hay token de autenticación');
        // }
        
        // Construir URL normalizada (evita doble /api)
        const url = buildUrl(endpoint);
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                // TODO: Reactivar autorización
                // 'Authorization': `Bearer ${token}`,
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
        // TODO: Reactivar validación de token después del desarrollo
        // const token = localStorage.getItem('token');
        // if (!token) {
        //     throw new Error('No hay token de autenticación');
        // }
        
        // Construir URL normalizada para desarrollo y producción
        const url = buildUrl(endpoint);
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                // TODO: Reactivar autorización
                // 'Authorization': `Bearer ${token}`,
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
        console.log('=== updateData INICIADO ===');
        console.log('Endpoint:', endpoint);
        console.log('Data:', data);
        
        // TODO: Reactivar validación de token después del desarrollo
        // const token = localStorage.getItem('token');
        // if (!token) {
        //     throw new Error('No hay token de autenticación');
        // }
        
        // Construir URL normalizada para desarrollo y producción
        const url = buildUrl(endpoint);
        console.log('URL completa:', url);
        
        const requestOptions = {
            method: 'PUT',
            headers: {
                // TODO: Reactivar autorización
                // 'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        };
        
        console.log('Opciones de petición:', requestOptions);
        console.log('Body serializado:', JSON.stringify(data));
        
        const response = await fetch(url, requestOptions);
        
        console.log('Respuesta recibida:', {
            status: response.status,
            statusText: response.statusText,
            ok: response.ok
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error en respuesta:', errorText);
            throw new Error(`Error ${response.status}: ${errorText}`);
        }
        
        const result = await response.json();
        console.log('Resultado parseado:', result);
        return result;
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
        // TODO: Reactivar validación de token después del desarrollo
        // const token = localStorage.getItem('token');
        // if (!token) {
        //     throw new Error('No hay token de autenticación');
        // }
        
        // Construir URL normalizada para desarrollo y producción
        const url = buildUrl(endpoint);
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                // TODO: Reactivar autorización
                // 'Authorization': `Bearer ${token}`,
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