// Importar funciones de API
import { getData, postData, updateData, deleteData } from '../utils/api.js';

// Variables globales
let categorias = [];
let categoriasFiltradas = null;
let paginaActual = 1;
const itemsPorPagina = 10;
let categoriaAEliminar = null;

// Elementos del DOM
let tablaCategorias, modalCategoria, modalConfirmar, formCategoria;
let btnNuevaCategoria, btnCerrarModal, btnCancelar, btnBuscar;
let btnCancelarEliminar, btnConfirmarEliminar, filtroNombre;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del DOM
    tablaCategorias = document.getElementById('tablaCategorias');
    modalCategoria = document.getElementById('modalCategoria');
    modalConfirmar = document.getElementById('modalConfirmar');
    formCategoria = document.getElementById('formCategoria');
    btnNuevaCategoria = document.getElementById('btnNuevaCategoria');
    btnCerrarModal = document.getElementById('btnCerrarModal');
    btnCancelar = document.getElementById('btnCancelar');
    btnBuscar = document.getElementById('btnBuscar');
    btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    filtroNombre = document.getElementById('filtroNombre');

    // Event listeners
    btnNuevaCategoria.addEventListener('click', abrirModalNueva);
    btnCerrarModal.addEventListener('click', cerrarModal);
    btnCancelar.addEventListener('click', cerrarModal);
    btnBuscar.addEventListener('click', buscarCategorias);
    btnCancelarEliminar.addEventListener('click', cerrarModalConfirmar);
    btnConfirmarEliminar.addEventListener('click', confirmarEliminar);
    formCategoria.addEventListener('submit', guardarCategoria);

    // Cargar categorías al iniciar
    if (!verificarAuth()) return;
    cargarCategorias();
});

// Funciones principales
async function cargarCategorias() {
    try {
        categorias = await getData(`/api/categorias/?_=${Date.now()}`);
        categoriasFiltradas = null;
        mostrarCategorias();
    } catch (error) {
        console.error('Error al cargar categorías:', error);
        alert('Error en conexión del servidor');
    }
}

function mostrarCategorias() {
    const base = categoriasFiltradas ?? categorias;
    const inicio = (paginaActual - 1) * itemsPorPagina;
    const fin = inicio + itemsPorPagina;
    const categoriasPagina = base.slice(inicio, fin);

    tablaCategorias.innerHTML = '';

    if (categoriasPagina.length === 0) {
        tablaCategorias.innerHTML = `
            <tr>
                <td colspan="4" class="px-6 py-4 text-center text-gray-500">
                    No se encontraron categorías
                </td>
            </tr>
        `;
        return;
    }

    categoriasPagina.forEach(categoria => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${categoria.id_categoria}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${categoria.nombre}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${categoria.descripcion || 'Sin descripción'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button onclick="editarCategoria(${categoria.id_categoria})" class="text-blue-600 hover:text-blue-900 mr-3">
                    <i class="fas fa-edit"></i> Editar
                </button>
                <button onclick="eliminarCategoria(${categoria.id_categoria})" class="text-red-600 hover:text-red-900">
                    <i class="fas fa-trash"></i> Eliminar
                </button>
            </td>
        `;
        tablaCategorias.appendChild(fila);
    });

    generarPaginacion(base.length);
}

function generarPaginacion(totalItems) {
    const totalPaginas = Math.ceil(totalItems / itemsPorPagina);
    const paginacion = document.getElementById('paginacion');

    if (totalPaginas <= 1) {
        paginacion.innerHTML = '';
        return;
    }

    let html = '';

    // Botón anterior
    if (paginaActual > 1) {
        html += `<button onclick="cambiarPagina(${paginaActual - 1})" class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded-l">Anterior</button>`;
    }

    // Números de página
    for (let i = 1; i <= totalPaginas; i++) {
        const clase = i === paginaActual ? 'bg-blue-500 text-white' : 'bg-gray-300 hover:bg-gray-400 text-gray-800';
        html += `<button onclick="cambiarPagina(${i})" class="${clase} font-bold py-2 px-4">${i}</button>`;
    }

    // Botón siguiente
    if (paginaActual < totalPaginas) {
        html += `<button onclick="cambiarPagina(${paginaActual + 1})" class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded-r">Siguiente</button>`;
    }

    paginacion.innerHTML = html;
}

function cambiarPagina(pagina) {
    paginaActual = pagina;
    mostrarCategorias();
}

function abrirModalNueva() {
    document.getElementById('tituloModal').textContent = 'Nueva Categoría';
    formCategoria.reset();
    document.getElementById('categoriaId').value = '';
    modalCategoria.classList.remove('hidden');
}

function editarCategoria(id) {
    const categoria = categorias.find(c => c.id_categoria === id);
    if (categoria) {
        document.getElementById('tituloModal').textContent = 'Editar Categoría';
        document.getElementById('categoriaId').value = categoria.id_categoria;
        document.getElementById('nombre').value = categoria.nombre;
        document.getElementById('descripcion').value = categoria.descripcion || '';
        modalCategoria.classList.remove('hidden');
    }
}

function eliminarCategoria(id) {
    categoriaAEliminar = id;
    modalConfirmar.classList.remove('hidden');
}

// Hacer las funciones globales para que puedan ser accedidas desde onclick
window.editarCategoria = editarCategoria;
window.eliminarCategoria = eliminarCategoria;
window.cambiarPagina = cambiarPagina;

function cerrarModal() {
    modalCategoria.classList.add('hidden');
}

function cerrarModalConfirmar() {
    modalConfirmar.classList.add('hidden');
    categoriaAEliminar = null;
}

async function guardarCategoria(e) {
    e.preventDefault();

    const id = document.getElementById('categoriaId').value;
    const nombre = document.getElementById('nombre').value;
    const descripcion = document.getElementById('descripcion').value;

    const datos = {
        nombre: nombre,
        descripcion: descripcion
    };

    try {
        if (id) {
            await updateData(`/api/categorias/${id}`, datos);
            alert('Categoría actualizada exitosamente');
        } else {
            await postData('/api/categorias/', datos);
            alert('Categoría creada exitosamente');
        }
        cerrarModal();
        await cargarCategorias();
    } catch (error) {
        console.error('Error:', error);
        alert('Error en conexión del servidor');
    }
}

async function confirmarEliminar() {
    if (!categoriaAEliminar) return;

    try {
        await deleteData(`/api/categorias/${categoriaAEliminar}`);
        alert('Categoría eliminada exitosamente');
        cerrarModalConfirmar();
        await cargarCategorias();
    } catch (error) {
        console.error('Error al eliminar categoría:', error);
        let msg = 'Error al eliminar categoría';
        const txt = String(error && error.message ? error.message : '');
        if (/Error\s+401/.test(txt) || /Error\s+403/.test(txt)) {
            alert('No autorizado. Inicie sesión como administrador.');
            window.location.href = '/login?tipo=trabajador';
            return;
        }
        try {
            const jsonStr = txt.replace(/^Error\s+\d+:\s+/, '');
            const data = JSON.parse(jsonStr);
            if (data && data.detail) {
                msg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
            }
        } catch {}
        alert(msg);
    }
}

function buscarCategorias() {
    const filtro = filtroNombre.value.toLowerCase();
    if (filtro) {
        const base = categorias;
        categoriasFiltradas = base.filter(categoria => 
            String(categoria.nombre || '').toLowerCase().includes(filtro)
        );
    } else {
        categoriasFiltradas = null;
    }
    paginaActual = 1;
    mostrarCategorias();
}

function verificarAuth() {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token') || localStorage.getItem('access_token');
    const isLoggedIn = sessionStorage.getItem('isLoggedIn') || localStorage.getItem('isLoggedIn');
    if (!token || isLoggedIn !== 'true') {
        window.location.href = '/login?tipo=trabajador';
        return false;
    }
    return true;
}
