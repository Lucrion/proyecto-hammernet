// Script para la gestión de mensajes
import { API_URL } from '../utils/config.js';
import { getData, updateData, deleteData } from '../utils/api.js';

// Variables globales
let mensajes = [];
let token = '';
let mensPagina = 1;
const mensTam = 20;

// Variables para el modal de eliminación
let mensajeAEliminar = null;

// Elementos del DOM
let loadingState, emptyState, tableContainer, tablaMensajes;

// Inicialización cuando se carga el DOM
document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del DOM
    tablaMensajes = document.getElementById('tablaMensajes');
    loadingState = document.getElementById('loadingState');
    emptyState = document.getElementById('emptyState');
    tableContainer = document.getElementById('tableContainer');
    
    // Obtener token de autenticación (compatibilidad con login de trabajador en sessionStorage)
    try {
        token = sessionStorage.getItem('token') || localStorage.getItem('token') || '';
    } catch {}
    // No redirigir automáticamente: los endpoints están protegidos y fetchWithAuth añadirá Authorization si hay token
    
    // Configurar event listeners para el modal de ver mensaje
    const closeModal = document.getElementById('closeModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const modalMensaje = document.getElementById('modalMensaje');
    
    if (closeModal) {
        closeModal.addEventListener('click', cerrarModalYMarcarLeido);
    }
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', cerrarModalYMarcarLeido);
    }
    
    if (modalMensaje) {
        modalMensaje.addEventListener('click', function(e) {
            if (e.target === modalMensaje) {
                cerrarModalYMarcarLeido();
            }
        });
    }
    
    // Configurar event listeners para el modal de eliminar mensaje
    const btnConfirmarEliminarMensaje = document.getElementById('btnConfirmarEliminarMensaje');
    const btnCancelarEliminarMensaje = document.getElementById('btnCancelarEliminarMensaje');
    
    if (btnConfirmarEliminarMensaje) {
        btnConfirmarEliminarMensaje.addEventListener('click', confirmarEliminacionMensaje);
    }
    
    if (btnCancelarEliminarMensaje) {
        btnCancelarEliminarMensaje.addEventListener('click', cerrarModalEliminarMensaje);
    }
    
    // Controles de paginación
    const prevBtn = document.getElementById('mensPrev');
    const nextBtn = document.getElementById('mensNext');
    if (prevBtn) prevBtn.addEventListener('click', () => { if (mensPagina > 1) { mensPagina--; cargarMensajes(); } });
    if (nextBtn) nextBtn.addEventListener('click', () => {
        const maxPagina = Math.ceil(mensajes.length / mensTam) || 1;
        if (mensPagina < maxPagina) { mensPagina++; cargarMensajes(); }
    });

    // Cargar mensajes
    obtenerMensajes();
});

// Función para cerrar modal y marcar como leído
function cerrarModalYMarcarLeido() {
    const modal = document.getElementById('modalMensaje');
    const mensajeId = modal.dataset.mensajeId;
    
    console.log('Cerrando modal, mensaje ID:', mensajeId); // Debug
    
    if (mensajeId) {
        const mensaje = mensajes.find(m => m.id == mensajeId);
        console.log('Mensaje encontrado:', mensaje); // Debug
        if (mensaje && !mensaje.leido) {
            console.log('Marcando como leído...'); // Debug
            marcarComoLeido(mensajeId);
        }
    }
    
    modal.classList.add('hidden');
    modal.dataset.mensajeId = ''; // Limpiar el ID
}

// Obtener mensajes del servidor
async function obtenerMensajes() {
    try {
        // Mostrar estado de carga
        mostrarEstado('loading');
        
        mensajes = await getData('/api/mensajes');
            console.log('Mensajes obtenidos:', mensajes);
            cargarMensajes();
    } catch (error) {
        console.error('Error de conexión:', error);
        mostrarEstado('empty');
    }
}

// Mostrar diferentes estados de la interfaz
function mostrarEstado(estado) {
    // Ocultar todos los estados
    if (loadingState) loadingState.classList.add('hidden');
    if (emptyState) emptyState.classList.add('hidden');
    if (tableContainer) tableContainer.classList.add('hidden');
    
    // Mostrar el estado correspondiente
    switch (estado) {
        case 'loading':
            if (loadingState) loadingState.classList.remove('hidden');
            break;
        case 'empty':
            if (emptyState) emptyState.classList.remove('hidden');
            break;
        case 'table':
            if (tableContainer) tableContainer.classList.remove('hidden');
            break;
    }
}

// Cargar mensajes en la tabla
function cargarMensajes() {
    if (!tablaMensajes) {
        console.error('Elemento tablaMensajes no encontrado');
        return;
    }

    if (mensajes.length === 0) {
        mostrarEstado('empty');
        return;
    }

    // Mostrar la tabla con datos
    mostrarEstado('table');
    
    const total = mensajes.length;
    const desdeIdx = (mensPagina - 1) * mensTam;
    const hastaIdx = Math.min(desdeIdx + mensTam, total);
    const pagina = mensajes.slice(desdeIdx, hastaIdx);
    tablaMensajes.innerHTML = pagina.map(mensaje => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${new Date(mensaje.fecha_envio).toLocaleDateString()}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${mensaje.nombre}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${mensaje.email}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${mensaje.asunto}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${mensaje.leido ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
                    ${mensaje.leido ? 'Leído' : 'No leído'}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="verMensaje(${mensaje.id})" 
                        class="text-indigo-600 hover:text-indigo-900 mr-3">
                    Ver
                </button>
                <button onclick="eliminarMensaje(${mensaje.id})" 
                        class="text-red-600 hover:text-red-900">
                    Eliminar
                </button>
            </td>
        </tr>
    `).join('');

    const desdeEl = document.getElementById('mensDesde');
    const hastaEl = document.getElementById('mensHasta');
    const totalEl = document.getElementById('mensTotal');
    if (desdeEl) desdeEl.textContent = total > 0 ? (desdeIdx + (pagina.length ? 1 : 0)) : 0;
    if (hastaEl) hastaEl.textContent = total > 0 ? hastaIdx : 0;
    if (totalEl) totalEl.textContent = total;
    const prevBtn2 = document.getElementById('mensPrev');
    const nextBtn2 = document.getElementById('mensNext');
    const hasPrev = mensPagina > 1;
    const hasNext = hastaIdx < total;
    if (prevBtn2) {
        prevBtn2.disabled = !hasPrev;
        prevBtn2.classList.toggle('opacity-50', !hasPrev);
        prevBtn2.classList.toggle('cursor-not-allowed', !hasPrev);
    }
    if (nextBtn2) {
        nextBtn2.disabled = !hasNext;
        nextBtn2.classList.toggle('opacity-50', !hasNext);
        nextBtn2.classList.toggle('cursor-not-allowed', !hasNext);
    }
}

// Ver mensaje completo
window.verMensaje = function(id) {
    console.log('Ver mensaje ID:', id); // Debug
    console.log('Mensajes disponibles:', mensajes); // Debug
    
    const mensaje = mensajes.find(m => m.id == id);
    console.log('Mensaje encontrado:', mensaje); // Debug
    
    if (mensaje) {
        // Actualizar el contenido del modal
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        
        modalTitle.textContent = `Mensaje de ${mensaje.nombre}`;
        
        modalContent.innerHTML = `
            <div class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre:</label>
                        <p class="text-gray-900">${mensaje.nombre}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Email:</label>
                        <p class="text-gray-900">${mensaje.email}</p>
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Asunto:</label>
                    <p class="text-gray-900 font-medium">${mensaje.asunto}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Fecha:</label>
                    <p class="text-gray-900">${new Date(mensaje.fecha_envio).toLocaleString()}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Mensaje:</label>
                    <div class="bg-gray-50 p-4 rounded-lg border">
                        <p class="text-gray-900 whitespace-pre-wrap">${mensaje.mensaje}</p>
                    </div>
                </div>
            </div>
        `;
        
        // Mostrar el modal
        const modal = document.getElementById('modalMensaje');
        modal.classList.remove('hidden');
        
        // Guardar el ID del mensaje actual para marcarlo como leído al cerrar
        modal.dataset.mensajeId = id;
    }
}

// Marcar mensaje como leído
async function marcarComoLeido(id) {
    console.log('Ejecutando marcarComoLeido con ID:', id); // Debug
    try {
        await updateData(`/api/mensajes/${id}/marcar-leido`, {});
        console.log('Mensaje marcado como leído, recargando tabla...'); // Debug
        obtenerMensajes(); // Recargar mensajes
    } catch (error) {
        console.error('Error al marcar como leído:', error);
    }
}

// Función para eliminar mensaje con confirmación
window.eliminarMensaje = function(id) {
    console.log('Preparando eliminación del mensaje con ID:', id);
    mensajeAEliminar = id;
    
    // Mostrar modal de confirmación
    const modalEliminarMensaje = document.getElementById('modalEliminarMensaje');
    if (modalEliminarMensaje) {
        modalEliminarMensaje.classList.remove('hidden');
    }
}

// Función para confirmar la eliminación
async function confirmarEliminacionMensaje() {
    if (!mensajeAEliminar) {
        console.error('No hay mensaje seleccionado para eliminar');
        return;
    }
    
    console.log('Confirmando eliminación del mensaje:', mensajeAEliminar);
    
    try {
        await deleteData(`/api/mensajes/${mensajeAEliminar}`);
        console.log('Mensaje eliminado exitosamente');
        // Cerrar modal
        cerrarModalEliminarMensaje();
        // Recargar mensajes
        obtenerMensajes();
    } catch (error) {
        console.error('Error en la petición:', error);
        alert('Error de conexión al eliminar el mensaje');
    }
}

// Función para cerrar el modal de eliminación
function cerrarModalEliminarMensaje() {
    const modalEliminarMensaje = document.getElementById('modalEliminarMensaje');
    if (modalEliminarMensaje) {
        modalEliminarMensaje.classList.add('hidden');
    }
    mensajeAEliminar = null;
}
