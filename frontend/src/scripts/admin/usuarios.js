// Importar funciones de API con autenticación
import { getData, postData, updateData, deleteData } from '../utils/api.js';
import { API_URL } from '../utils/config.js';

// Variables globales
let usuarioIdEliminar = null;
let usuarioIdEliminarPermanente = null;

// Función para verificar autenticación
function verificarAutenticacion() {
    const isLoggedIn = sessionStorage.getItem('isLoggedIn') || localStorage.getItem('isLoggedIn');
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
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
            // Mostrar solo trabajadores (excluir clientes)
            const trabajadores = response.filter(u => u.role !== 'cliente');
            cargarUsuarios(trabajadores);
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

// Estado de vista actual: trabajadores por defecto
let vistaActual = 'trabajadores';
let usuariosLista = [];
let paginaActual = 1;
let tamPagina = 10;

// mostrarMensaje: definido más abajo con UI de notificación fija

function validarFormularioUsuario(data) {
    const errores = [];
    // Email
    if (data.email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.email)) {
            errores.push('El correo electrónico no es válido.');
        }
    }
    // Password (si viene en el formulario)
    if (data.password !== undefined && data.password.trim().length > 0) {
        if (data.password.length < 8) {
            errores.push('La contraseña debe tener al menos 8 caracteres.');
        }
    }
    // RUT chileno
    if (data.rut) {
        const rutValido = validarRutChileno(data.rut);
        if (!rutValido) {
            errores.push('El RUT ingresado no es válido.');
        }
    }
    return errores;
}

function validarRutChileno(rut) {
    // Limpieza y separación
    const limpio = rut.replace(/\./g, '').replace(/-/g, '').toUpperCase();
    if (limpio.length < 2) return false;
    const cuerpo = limpio.slice(0, -1);
    const dv = limpio.slice(-1);
    if (!/^\d+$/.test(cuerpo)) return false;
    // Cálculo dígito verificador
    let suma = 0;
    let multiplicador = 2;
    for (let i = cuerpo.length - 1; i >= 0; i--) {
        suma += parseInt(cuerpo[i], 10) * multiplicador;
        multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
    }
    const resto = suma % 11;
    const dvCalc = 11 - resto;
    let dvFinal = '';
    if (dvCalc === 11) dvFinal = '0';
    else if (dvCalc === 10) dvFinal = 'K';
    else dvFinal = String(dvCalc);
    return dvFinal === dv;
}

function renderPagina() {
    const total = usuariosLista.length;
    const desdeIdx = (paginaActual - 1) * tamPagina;
    const hastaIdx = Math.min(desdeIdx + tamPagina, total);
    const pagina = usuariosLista.slice(desdeIdx, hastaIdx);
    cargarUsuarios(pagina);
    actualizarPaginacionUI(desdeIdx + (pagina.length > 0 ? 1 : 0), hastaIdx, total);
}

function actualizarPaginacionUI(desde, hasta, total) {
    const desdeEl = document.getElementById('mostrandoDesde');
    const hastaEl = document.getElementById('mostrandoHasta');
    const totalEl = document.getElementById('totalUsuarios');
    const btnPrev = document.getElementById('btnPrevUsuarios');
    const btnNext = document.getElementById('btnNextUsuarios');
    if (desdeEl) desdeEl.textContent = total > 0 ? desde : 0;
    if (hastaEl) hastaEl.textContent = total > 0 ? hasta : 0;
    if (totalEl) totalEl.textContent = total;
    if (btnPrev) btnPrev.disabled = paginaActual <= 1;
    if (btnNext) btnNext.disabled = hasta >= total;
}

// Mostrar trabajadores en la tabla principal
async function mostrarTrabajadores() {
    try {
        const response = await getData('/api/usuarios/');
        if (response && Array.isArray(response)) {
            usuariosLista = response.filter(u => u.role !== 'cliente');
            paginaActual = 1;
            renderPagina();
        }
    } catch (error) {
        console.error('Error al cargar trabajadores:', error);
    }
}

// Mostrar clientes en la tabla principal
async function mostrarClientes() {
    try {
        const response = await getData('/api/usuarios/');
        if (response && Array.isArray(response)) {
            usuariosLista = response.filter(u => u.role === 'cliente');
            paginaActual = 1;
            renderPagina();
        }
    } catch (error) {
        console.error('Error al cargar clientes:', error);
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
        
        // Generar botones de acción
        let botonesAccion = '';
        if (usuario.role !== 'cliente') {
            botonesAccion = `
                <button onclick="editarUsuario(${usuario.id_usuario})" class="text-indigo-600 hover:text-indigo-900 mr-3">Editar</button>
                <button onclick="confirmarEliminarUsuario(${usuario.id_usuario})" class="text-red-600 hover:text-red-900">Desactivar</button>
            `;
        } else {
            // Para clientes, permitir ver información de perfil
            botonesAccion = `
                <button onclick="verInfoUsuario(${usuario.id_usuario})" class="text-blue-600 hover:text-blue-900">Ver Información</button>
            `;
        }
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${usuario.id_usuario}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${usuario.nombre}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatearRut(usuario.rut)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${usuario.role}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${fechaCreacion}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                ${botonesAccion}
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Nota: los clientes se renderizan en la misma tabla usando cargarUsuarios

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
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatearRut(usuario.rut)}</td>
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

// Eliminado modal de clientes: se usará la tabla principal

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

// Modal de información de usuario
function mostrarModalInfo() {
    document.getElementById('modalInfoUsuario').classList.remove('hidden');
}

function cerrarModalInfo() {
    document.getElementById('modalInfoUsuario').classList.add('hidden');
}

window.verInfoUsuario = async function(id) {
    try {
        const usuario = await getData(`/api/usuarios/${id}`);
        if (usuario) {
            // Rellenar datos básicos
            document.getElementById('infoId').textContent = usuario.id_usuario ?? '—';
            document.getElementById('infoNombre').textContent = usuario.nombre ?? '—';
            document.getElementById('infoApellido').textContent = usuario.apellido ?? '—';
            document.getElementById('infoUsername').textContent = formatearRut(usuario.rut) ?? '—';
            document.getElementById('infoRut').textContent = usuario.rut ?? '—';
            document.getElementById('infoEmail').textContent = usuario.email ?? '—';
            document.getElementById('infoTelefono').textContent = usuario.telefono ?? '—';
            document.getElementById('infoRol').textContent = usuario.role ?? '—';
            document.getElementById('infoActivo').textContent = usuario.activo ? 'Activo' : 'Desactivado';
            document.getElementById('infoFechaCreacion').textContent = usuario.fecha_creacion ? new Date(usuario.fecha_creacion).toLocaleDateString('es-ES') : '—';

            // Direcciones de despacho
            const lista = document.getElementById('listaDespachos');
            if (lista) {
                try {
                    const despachos = await getData(`/api/despachos/usuario/${id}`);
                    lista.innerHTML = '';
                    if (Array.isArray(despachos) && despachos.length > 0) {
                        despachos.forEach(d => {
                            const li = document.createElement('li');
                            const partes = [d.calle, d.numero, d.depto, d.adicional].filter(Boolean);
                            li.textContent = partes.join(', ');
                            lista.appendChild(li);
                        });
                    } else {
                        lista.innerHTML = '<li class="text-gray-400">Sin direcciones registradas</li>';
                    }
                } catch (e) {
                    console.error('Error al obtener direcciones de despacho:', e);
                    lista.innerHTML = '<li class="text-gray-400">Sin direcciones registradas</li>';
                }
            }

            // Cargar y renderizar auditoría del usuario
            try {
                const registros = await getData(`/api/auditoria/usuario/${id}`);
                renderAuditoriaUsuario(registros);
            } catch (e) {
                console.error('Error al obtener auditoría del usuario:', e);
                renderAuditoriaUsuario([]);
            }

            mostrarModalInfo();
        }
    } catch (error) {
        console.error('Error al obtener información del usuario:', error);
        mostrarMensaje('Error al cargar información del usuario', 'error');
    }
};

// Renderizar auditoría en el modal de información de usuario
function renderAuditoriaUsuario(registros) {
    // Crear contenedor si no existe
    let contenedor = document.getElementById('contenedorAuditoriaUsuario');
    if (!contenedor) {
        const modalBody = document.getElementById('modalInfoUsuario');
        if (!modalBody) return;
        contenedor = document.createElement('div');
        contenedor.id = 'contenedorAuditoriaUsuario';
        contenedor.className = 'mt-4 border-t pt-4';
        const titulo = document.createElement('h3');
        titulo.className = 'text-lg font-semibold text-gray-800 mb-2';
        titulo.textContent = 'Actividad reciente';
        const lista = document.createElement('ul');
        lista.id = 'listaAuditoriaUsuario';
        lista.className = 'space-y-2 max-h-48 overflow-auto';
        contenedor.appendChild(titulo);
        contenedor.appendChild(lista);
        modalBody.appendChild(contenedor);
    }
    const listaEl = document.getElementById('listaAuditoriaUsuario');
    if (!listaEl) return;
    listaEl.innerHTML = '';
    if (!Array.isArray(registros) || registros.length === 0) {
        const li = document.createElement('li');
        li.className = 'text-gray-400';
        li.textContent = 'Sin actividad registrada';
        listaEl.appendChild(li);
        return;
    }
    registros.forEach(r => {
        const li = document.createElement('li');
        li.className = 'text-sm text-gray-700';
        const fecha = r.fecha ? new Date(r.fecha).toLocaleString('es-ES') : '';
        const actor = r.usuario_actor_id ? ` · actor #${r.usuario_actor_id}` : '';
        li.textContent = `${fecha} · ${r.accion}${actor}${r.detalle ? ' · ' + r.detalle : ''}`;
        listaEl.appendChild(li);
    });
}

// Funciones globales para ser llamadas desde HTML
window.editarUsuario = async function(id) {
    try {
        const response = await getData(`/api/usuarios/${id}`);
        if (response) {
            document.getElementById('userId').value = response.id_usuario;
            document.getElementById('nombre').value = response.nombre;
            const rutInput = document.getElementById('rut');
            if (rutInput) {
                rutInput.value = formatearRut(response.rut);
            }
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
    const btnClientes = document.getElementById('btnClientes');
    const usuarioForm = document.getElementById('usuarioForm');
    const btnCancelar = document.getElementById('btnCancelar');
    const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    const btnCerrarModalDesactivados = document.getElementById('btnCerrarModalDesactivados');
    // Sin modal de clientes
    const btnCancelarEliminacionPermanente = document.getElementById('btnCancelarEliminacionPermanente');
    const btnConfirmarEliminacionPermanente = document.getElementById('btnConfirmarEliminacionPermanente');
    const btnCerrarModalInfo = document.getElementById('btnCerrarModalInfo');

    // Event listeners
    if (btnNuevoUsuario) {
        btnNuevoUsuario.addEventListener('click', mostrarFormulario);
    }

    if (btnUsuariosDesactivados) {
        btnUsuariosDesactivados.addEventListener('click', mostrarModalDesactivados);
    }

    if (btnClientes) {
        btnClientes.addEventListener('click', async function() {
            if (vistaActual === 'trabajadores') {
                await mostrarClientes();
                vistaActual = 'clientes';
                btnClientes.textContent = 'Trabajadores';
                btnClientes.classList.remove('bg-green-600','hover:bg-green-700');
                btnClientes.classList.add('bg-blue-600','hover:bg-blue-700');
            } else {
                await mostrarTrabajadores();
                vistaActual = 'trabajadores';
                btnClientes.textContent = 'Clientes';
                btnClientes.classList.remove('bg-blue-600','hover:bg-blue-700');
                btnClientes.classList.add('bg-green-600','hover:bg-green-700');
            }
        });
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

    if (btnCerrarModalInfo) {
        btnCerrarModalInfo.addEventListener('click', cerrarModalInfo);
    }

    // Formulario de usuario
    if (usuarioForm) {
        usuarioForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(usuarioForm);
            const data = Object.fromEntries(formData.entries());

            // Normalizar y sanitizar RUT (solo dígitos)
            if (data.rut) {
                const soloDigitos = String(data.rut).replace(/\D/g, '');
                data.rut = soloDigitos ? parseInt(soloDigitos, 10) : null;
            }

            // Si la contraseña está vacía al editar, no enviar campo
            if (data.password !== undefined && String(data.password).trim() === '') {
                delete data.password;
            }

            // Validaciones estrictas
            const errores = validarFormularioUsuario(data);
            if (errores.length > 0) {
                errores.forEach(err => mostrarMensaje(err, 'error'));
                return;
            }
            
            const userId = document.getElementById('userId').value;
            
            if (userId) {
                await actualizarUsuario(userId, data);
            } else {
                await crearUsuario(data);
            }
        });
    }

    // Eventos de paginación
    const selectTam = document.getElementById('selectTamPaginaUsuarios');
    const btnPrev = document.getElementById('btnPrevUsuarios');
    const btnNext = document.getElementById('btnNextUsuarios');

    if (selectTam) {
        selectTam.addEventListener('change', () => {
            const val = parseInt(selectTam.value, 10);
            tamPagina = isNaN(val) ? 10 : val;
            paginaActual = 1;
            renderPagina();
        });
    }
    if (btnPrev) {
        btnPrev.addEventListener('click', () => {
            if (paginaActual > 1) {
                paginaActual -= 1;
                renderPagina();
            }
        });
    }
    if (btnNext) {
        btnNext.addEventListener('click', () => {
            const total = usuariosLista.length;
            const maxPagina = Math.ceil(total / tamPagina) || 1;
            if (paginaActual < maxPagina) {
                paginaActual += 1;
                renderPagina();
            }
        });
    }

    // Cargar trabajadores al iniciar
mostrarTrabajadores();
});

// Utilidad: formatear RUT entero a formato con DV (sin puntos)
function formatearRut(rut) {
    if (rut === null || rut === undefined) return '—';
    const cuerpo = String(rut).replace(/\D/g, '');
    if (!cuerpo) return '—';
    let suma = 0;
    let multiplicador = 2;
    for (let i = cuerpo.length - 1; i >= 0; i--) {
        suma += parseInt(cuerpo[i], 10) * multiplicador;
        multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
    }
    const resto = suma % 11;
    const dvCalc = 11 - resto;
    let dvFinal = '';
    if (dvCalc === 11) dvFinal = '0';
    else if (dvCalc === 10) dvFinal = 'K';
    else dvFinal = String(dvCalc);
    return `${cuerpo}-${dvFinal}`;
}