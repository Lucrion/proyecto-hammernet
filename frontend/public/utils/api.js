// Funciones para comunicación con la API (copia pública)
import { API_URL, corsConfig, handleApiError } from './config.js';

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

export async function fetchWithAuth(endpoint, options = {}) {
    try {
        const headers = options.headers || {};
        if (!(options.body instanceof FormData) && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }
        const url = buildUrl(endpoint);
        try {
            const response = await fetch(url, { ...options, headers });
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

export async function getData(endpoint) {
    try {
        const url = buildUrl(endpoint);
        const response = await fetch(url, {
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

export async function postData(endpoint, data) {
    try {
        const url = buildUrl(endpoint);
        const response = await fetch(url, {
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

export async function updateData(endpoint, data) {
    try {
        const url = buildUrl(endpoint);
        const response = await fetch(url, {
            method: 'PUT',
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
        console.error(`Error al actualizar datos en ${endpoint}:`, error);
        throw error;
    }
}

export async function deleteData(endpoint) {
    try {
        const url = buildUrl(endpoint);
        const response = await fetch(url, {
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