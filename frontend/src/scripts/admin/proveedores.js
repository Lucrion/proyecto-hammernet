// Script para la gestión de proveedores
import { getData, postData, updateData, deleteData } from '../utils/api.js';
import { formatRutUI } from '../utils/rut.js';

// Autenticación manejada por AdminLayout; no forzar redirección aquí

// Variables globales
let proveedores = [];
let proveedorEditando = null;
let proveedorAEliminar = null;

// Elementos del DOM
const tablaProveedores = document.getElementById('tablaProveedores');
const formProveedor = document.getElementById('formProveedor');
const modalProveedor = document.getElementById('modalProveedor');
const modalConfirmar = document.getElementById('modalConfirmar');
const btnNuevoProveedor = document.getElementById('btnNuevoProveedor');
const btnCerrarModal = document.getElementById('btnCerrarModal');
const btnCancelar = document.getElementById('btnCancelar');
const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    obtenerProveedores();
    
    if (btnNuevoProveedor) {
        btnNuevoProveedor.addEventListener('click', abrirModalNuevo);
    }
    
    if (btnCerrarModal) {
        btnCerrarModal.addEventListener('click', cerrarModal);
    }
    
    if (btnCancelar) {
        btnCancelar.addEventListener('click', cerrarModal);
    }
    
    if (btnCancelarEliminar) {
        btnCancelarEliminar.addEventListener('click', cerrarModalConfirmar);
    }
    
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', confirmarEliminar);
    }
    
    if (formProveedor) {
        // Aplicar máscara RUT al input si existe
        const rutEl = document.getElementById('rut');
        if (rutEl) {
            rutEl.addEventListener('input', (e) => {
                const formatted = formatRutUI(e.target.value);
                e.target.value = formatted;
                e.target.selectionStart = e.target.selectionEnd = formatted.length;
            });
        }
        formProveedor.addEventListener('submit', guardarProveedor);
    }
});

// Obtener proveedores del servidor
async function obtenerProveedores() {
    try {
        proveedores = await getData('/api/proveedores/');
        cargarProveedores();
    } catch (error) {
        console.error('Error de conexión:', error);
    }
}

// Cargar proveedores en la tabla
function cargarProveedores() {
    if (!tablaProveedores) return;

    if (proveedores.length === 0) {
        tablaProveedores.innerHTML = '<tr><td colspan="6" class="text-center py-4">No hay proveedores registrados</td></tr>';
        return;
    }

    tablaProveedores.innerHTML = proveedores.map(proveedor => `
        <tr class="border-b hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${proveedor.id_proveedor}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${proveedor.nombre}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${proveedor.rut || 'N/A'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${proveedor.razon_social || 'N/A'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${proveedor.contacto || 'N/A'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button onclick="editarProveedor(${proveedor.id_proveedor})" class="text-blue-600 hover:text-blue-900 mr-3">
                    <i class="fas fa-edit"></i> Editar
                </button>
                <button onclick="eliminarProveedor(${proveedor.id_proveedor})" class="text-red-600 hover:text-red-900">
                    <i class="fas fa-trash"></i> Eliminar
                </button>
            </td>
        </tr>
    `).join('');
}

// Abrir modal para nuevo proveedor
function abrirModalNuevo() {
    proveedorEditando = null;
    formProveedor.reset();
    document.getElementById('tituloModal').textContent = 'Nuevo Proveedor';
    modalProveedor.classList.remove('hidden');
}

// Editar proveedor
window.editarProveedor = function(id) {
    proveedorEditando = proveedores.find(p => p.id_proveedor === id);
    if (proveedorEditando) {
        document.getElementById('nombre').value = proveedorEditando.nombre;
        document.getElementById('rut').value = proveedorEditando.rut || '';
        document.getElementById('razon_social').value = proveedorEditando.razon_social || '';
        document.getElementById('sucursal').value = proveedorEditando.sucursal || '';
        document.getElementById('ciudad').value = proveedorEditando.ciudad || '';
        document.getElementById('contacto').value = proveedorEditando.contacto || '';
        document.getElementById('celular').value = proveedorEditando.celular || '';
        document.getElementById('correo').value = proveedorEditando.correo || '';
        const telefonoEl = document.getElementById('telefono');
        if (telefonoEl) telefonoEl.value = proveedorEditando.telefono || '';
        document.getElementById('direccion').value = proveedorEditando.direccion || '';
        
        document.getElementById('tituloModal').textContent = 'Editar Proveedor';
        modalProveedor.classList.remove('hidden');
    }
}

// Guardar proveedor
async function guardarProveedor(e) {
    e.preventDefault();
    
    const formData = new FormData(formProveedor);
    const proveedorData = {
        nombre: formData.get('nombre'),
        rut: formData.get('rut'),
        razon_social: formData.get('razon_social'),
        sucursal: formData.get('sucursal'),
        ciudad: formData.get('ciudad'),
        contacto: formData.get('contacto'),
        celular: formData.get('celular'),
        correo: formData.get('correo'),
        telefono: formData.get('telefono'),
        direccion: formData.get('direccion')
    };

    try {
        if (proveedorEditando) {
            await updateData(`/api/proveedores/${proveedorEditando.id_proveedor}`, proveedorData);
            cerrarModal();
            obtenerProveedores();
            alert('Proveedor actualizado correctamente');
        } else {
            await postData('/api/proveedores/', proveedorData);
            cerrarModal();
            obtenerProveedores();
            alert('Proveedor creado correctamente');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error de conexión');
    }
}

// Eliminar proveedor
window.eliminarProveedor = function(id) {
    proveedorAEliminar = id;
    modalConfirmar.classList.remove('hidden');
}

// Cerrar modal
function cerrarModal() {
    modalProveedor.classList.add('hidden');
    proveedorEditando = null;
}

// Cerrar modal de confirmación
window.cerrarModalConfirmar = function() {
    modalConfirmar.classList.add('hidden');
    proveedorAEliminar = null;
}

// Confirmar eliminación
window.confirmarEliminar = async function() {
    if (proveedorAEliminar) {
        try {
            await deleteData(`/api/proveedores/${proveedorAEliminar}`);
            obtenerProveedores();
            alert('Proveedor eliminado correctamente');
        } catch (error) {
            console.error('Error:', error);
            alert('Error de conexión');
        }
    }
    cerrarModalConfirmar();
}
