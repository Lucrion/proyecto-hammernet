// Funciones para comunicación con la API
import { API_URL, corsConfig, handleApiError } from './config.js';

/**
 * Realiza una petición autenticada a la API con soporte para FormData
 * @param {string} endpoint - Endpoint de la API (sin incluir la URL base)
 * @param {Object} options - Opciones de fetch (method, headers, body, etc.)
 * @returns {Promise<Response>} - Respuesta de la petición
 */
export async function fetchWithAuth(endpoint, options = {}) {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('No hay token de autenticación');
        }
        
        // Crear headers con autenticación
        const headers = options.headers || {};
        headers['Authorization'] = `Bearer ${token}`;
        
        // Si no es FormData, agregar Content-Type
        if (!(options.body instanceof FormData) && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }
        
        // Realizar la petición
        // Verificar si el endpoint ya incluye la URL base
        const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            return response;
        } catch (fetchError) {
            console.error(`Error de red en fetchWithAuth para ${endpoint}:`, fetchError);
            throw new Error(`Error de conexión: ${fetchError.message}`);
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
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('No hay token de autenticación');
        }
        
        // Verificar si el endpoint ya incluye la URL base
        const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
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
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('No hay token de autenticación');
        }
        
        // Verificar si el endpoint ya incluye la URL base
        const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
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
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('No hay token de autenticación');
        }
        
        // Verificar si el endpoint ya incluye la URL base
        const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
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
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('No hay token de autenticación');
        }
        
        // Verificar si el endpoint ya incluye la URL base
        const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
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