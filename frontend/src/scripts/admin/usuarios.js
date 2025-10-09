// Importar funciones de API con autenticación
import { getData, postData, updateData, deleteData } from '../utils/api.js';
import { API_URL } from '../utils/config.js';

// Variables globales
let usuarioIdEliminar = null;
let usuarioIdEliminarPermanente = null;

// Función para verificar autenticación
function verificarAutenticacion() {
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const token = localStorage.getItem('token');
    
    console.log('Usuarios Index - Estado de autenticación:', isLoggedIn);
    console.log('Usuarios Index - Token:', token ? 'Token presente' : 'Token ausente');
    
    if (!isLoggedIn || isLoggedIn !== 'true' || !token) {
        console.warn('Usuario no autenticado o token ausente, redirigiendo al login');
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Función para obtener usuarios
async function obtenerUsuarios() {
    try {
        const response = await getData('/api/usuarios/');
        if (response && Array.isArray(response)) {
            cargarUsuarios(response);
        } else {
            console.error('Respuesta inválida del servidor:', response);
            mostrarMensaje('Error al cargar usuarios', 'error');
        }
    } catch (error) {
        console.error('Error al obtener usuarios:', error);
        mostrarMensaje('Error al cargar usuarios', 'error');
    }
}

// Función para obtener usuarios desactivados
async function obtenerUsuariosDesactivados() {
    try {
        const response = await getData('/api/usuarios/desactivados');
        if (response && Array.isArray(response)) {
            cargarUsuariosDesactivados(response);
        } else {
            console.error('Respuesta inválida del servidor:', response);
            mostrarMensaje('Error al cargar usuarios desactivados', 'error');
        }
    } catch (error) {
        console.error('Error al obtener usuarios desactivados:', error);
        mostrarMensaje('Error al cargar usuarios desactivados', 'error');
    }
}

// Función para cargar usuarios en la tabla
function cargarUsuarios(usuarios) {
    const tbody = document.querySelector('#tablaUsuarios');
    if (!tbody) {
        console.error('No se encontró el tbody de la tabla');
        return;
    }

    tbody.innerHTML = '';

    if (usuarios.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-gray-500">No hay usuarios registrados</td></tr>';
        return;
    }

    usuarios.forEach(usuario => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        
        const fechaCreacion = new Date(usuario.fecha_creacion).toLocaleDateString('es-ES');
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${usuario.id_usuario}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${usuario.nombre}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${usuario.username}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${usuario.role}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${fechaCreacion}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="editarUsuario(${usuario.id_usuario})" class="text-indigo-600 hover:text-indigo-900 mr-3">Editar</button>
                <button onclick="confirmarEliminarUsuario(${usuario.id_usuario})" class="text-red-600 hover:text-red-900">Desactivar</button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Función para cargar usuarios desactivados en el modal
function cargarUsuariosDesactivados(usuarios) {
    const tbody = document.querySelector('#tablaUsuariosDesactivados');
    if (!tbody) {
        console.error('No se encontró el tbody de la tabla de usuarios desactivados');
        return;
    }

    tbody.innerHTML = '';

    if (usuarios.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-gray-500">No hay usuarios desactivados</td></tr>';
        return;
    }

    usuarios.forEach(usuario => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        
        const fechaCreacion = new Date(usuario.fecha_creacion).toLocaleDateString('es-ES');
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${usuario.id_usuario}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${usuario.nombre}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${usuario.username}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${usuario.role}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${fechaCreacion}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="eliminarUsuarioPermanente(${usuario.id_usuario})" class="text-red-600 hover:text-red-900 font-semibold">Eliminar Permanentemente</button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Función para mostrar mensajes
function mostrarMensaje(mensaje, tipo = 'info') {
    // Crear elemento de mensaje
    const messageDiv = document.createElement('div');
    messageDiv.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
        tipo === 'error' ? 'bg-red-500 text-white' : 
        tipo === 'success' ? 'bg-green-500 text-white' : 
        'bg-blue-500 text-white'
    }`;
    messageDiv.textContent = mensaje;
    
    document.body.appendChild(messageDiv);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 3000);
}

// Función para crear usuario
async function crearUsuario(formData) {
    try {
        const response = await postData('/api/usuarios/', formData);
        if (response) {
            mostrarMensaje('Usuario creado exitosamente', 'success');
            cerrarFormulario();
            obtenerUsuarios();
        }
    } catch (error) {
        console.error('Error al crear usuario:', error);
        mostrarMensaje('Error al crear usuario', 'error');
    }
}

// Función para actualizar usuario
async function actualizarUsuario(id, formData) {
    try {
        const response = await updateData(`/api/usuarios/${id}`, formData);
        if (response) {
            mostrarMensaje('Usuario actualizado exitosamente', 'success');
            cerrarFormulario();
            obtenerUsuarios();
        }
    } catch (error) {
        console.error('Error al actualizar usuario:', error);
        mostrarMensaje('Error al actualizar usuario', 'error');
    }
}

// Función para eliminar usuario (desactivar)
async function eliminarUsuario(id) {
    try {
        const response = await updateData(`/api/usuarios/${id}/desactivar`, {});
        if (response) {
            mostrarMensaje('Usuario desactivado exitosamente', 'success');
            obtenerUsuarios();
        }
    } catch (error) {
        console.error('Error al desactivar usuario:', error);
        mostrarMensaje('Error al desactivar usuario', 'error');
    }
}

// Función para eliminar usuario permanentemente
async function eliminarUsuarioPermanenteAPI(id) {
    try {
        const response = await deleteData(`/api/usuarios/${id}/eliminar-permanente`);
        if (response) {
            mostrarMensaje('Usuario eliminado permanentemente', 'success');
            obtenerUsuariosDesactivados();
        }
    } catch (error) {
        console.error('Error al eliminar usuario permanentemente:', error);
        mostrarMensaje('Error al eliminar usuario permanentemente', 'error');
    }
}

// Funciones de UI
function mostrarFormulario() {
    document.getElementById('formUsuario').classList.remove('hidden');
}

function cerrarFormulario() {
    document.getElementById('formUsuario').classList.add('hidden');
    document.getElementById('usuarioForm').reset();
    document.getElementById('userId').value = '';
    document.getElementById('formTitle').textContent = 'Nuevo Usuario';
}

function mostrarModalDesactivados() {
    document.getElementById('modalUsuariosDesactivados').classList.remove('hidden');
    obtenerUsuariosDesactivados();
}

function cerrarModalDesactivados() {
    document.getElementById('modalUsuariosDesactivados').classList.add('hidden');
}

function mostrarModalConfirmacion() {
    document.getElementById('modalConfirmar').classList.remove('hidden');
}

function cerrarModalConfirmacion() {
    document.getElementById('modalConfirmar').classList.add('hidden');
    usuarioIdEliminar = null;
}

function mostrarModalEliminacionPermanente() {
    document.getElementById('modalConfirmarEliminacionPermanente').classList.remove('hidden');
}

function cerrarModalEliminacionPermanente() {
    document.getElementById('modalConfirmarEliminacionPermanente').classList.add('hidden');
    usuarioIdEliminarPermanente = null;
}

// Funciones globales para ser llamadas desde HTML
window.editarUsuario = async function(id) {
    try {
        const response = await getData(`/api/usuarios/${id}`);
        if (response) {
            document.getElementById('userId').value = response.id_usuario;
            document.getElementById('nombre').value = response.nombre;
            document.getElementById('username').value = response.username;
            document.getElementById('role').value = response.role;
            document.getElementById('formTitle').textContent = 'Editar Usuario';
            mostrarFormulario();
        }
    } catch (error) {
        console.error('Error al obtener usuario:', error);
        mostrarMensaje('Error al cargar datos del usuario', 'error');
    }
};

window.confirmarEliminarUsuario = function(id) {
    usuarioIdEliminar = id;
    mostrarModalConfirmacion();
};

window.eliminarUsuarioPermanente = function(id) {
    usuarioIdEliminarPermanente = id;
    mostrarModalEliminacionPermanente();
};

window.confirmarEliminacionPermanente = function() {
    if (usuarioIdEliminarPermanente) {
        eliminarUsuarioPermanenteAPI(usuarioIdEliminarPermanente);
        cerrarModalEliminacionPermanente();
    }
};

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Verificar autenticación
    if (!verificarAutenticacion()) {
        return;
    }

    // Elementos del DOM
    const btnNuevoUsuario = document.getElementById('btnNuevoUsuario');
    const btnUsuariosDesactivados = document.getElementById('btnUsuariosDesactivados');
    const usuarioForm = document.getElementById('usuarioForm');
    const btnCancelar = document.getElementById('btnCancelar');
    const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    const btnCerrarModalDesactivados = document.getElementById('btnCerrarModalDesactivados');
    const btnCancelarEliminacionPermanente = document.getElementById('btnCancelarEliminacionPermanente');
    const btnConfirmarEliminacionPermanente = document.getElementById('btnConfirmarEliminacionPermanente');

    // Event listeners
    if (btnNuevoUsuario) {
        btnNuevoUsuario.addEventListener('click', mostrarFormulario);
    }

    if (btnUsuariosDesactivados) {
        btnUsuariosDesactivados.addEventListener('click', mostrarModalDesactivados);
    }

    if (btnCancelar) {
        btnCancelar.addEventListener('click', cerrarFormulario);
    }

    if (btnCancelarEliminar) {
        btnCancelarEliminar.addEventListener('click', cerrarModalConfirmacion);
    }

    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', function() {
            if (usuarioIdEliminar) {
                eliminarUsuario(usuarioIdEliminar);
                cerrarModalConfirmacion();
            }
        });
    }

    if (btnCerrarModalDesactivados) {
        btnCerrarModalDesactivados.addEventListener('click', cerrarModalDesactivados);
    }

    if (btnCancelarEliminacionPermanente) {
        btnCancelarEliminacionPermanente.addEventListener('click', cerrarModalEliminacionPermanente);
    }

    if (btnConfirmarEliminacionPermanente) {
        btnConfirmarEliminacionPermanente.addEventListener('click', confirmarEliminacionPermanente);
    }

    // Formulario de usuario
    if (usuarioForm) {
        usuarioForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(usuarioForm);
            const data = Object.fromEntries(formData.entries());
            
            const userId = document.getElementById('userId').value;
            
            if (userId) {
                await actualizarUsuario(userId, data);
            } else {
                await crearUsuario(data);
            }
        });
    }

    // Cargar usuarios al inicializar
    obtenerUsuarios();
});