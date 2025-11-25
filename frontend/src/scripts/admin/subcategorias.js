// Gestión de Subcategorías en Admin
import { getData, postData, updateData, deleteData } from '../utils/api.js';

const API_BASE = '/api';

// Elementos de la vista
const filtroNombre = document.getElementById('filtroNombre');
const filtroCategoria = document.getElementById('filtroCategoria');
const btnBuscar = document.getElementById('btnBuscar');
const tablaSubcategorias = document.getElementById('tablaSubcategorias');
const paginacion = document.getElementById('paginacion');
let categoriasCache = [];

const btnNuevaSubcategoria = document.getElementById('btnNuevaSubcategoria');
const modalSubcategoria = document.getElementById('modalSubcategoria');
const tituloModal = document.getElementById('tituloModal');
const formSubcategoria = document.getElementById('formSubcategoria');
const subcategoriaIdInput = document.getElementById('subcategoriaId');
const nombreInput = document.getElementById('nombre');
const categoriaSelect = document.getElementById('categoria');
const descripcionInput = document.getElementById('descripcion');
const btnCerrarModal = document.getElementById('btnCerrarModal');
const btnCancelar = document.getElementById('btnCancelar');

const modalConfirmar = document.getElementById('modalConfirmar');
const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');

let subcategoriaAEliminar = null;

// Utilidades
const showModal = (el) => el.classList.remove('hidden');
const hideModal = (el) => el.classList.add('hidden');

// Las llamadas usarán utilitarios con token (getData/postData/updateData/deleteData)

// Cargar categorías para filtros y modal
async function cargarCategorias() {
  const categorias = await getData(`${API_BASE}/categorias`);
  categoriasCache = Array.isArray(categorias) ? categorias : [];
  // Filtro
  filtroCategoria.innerHTML = '<option value="">Todas las categorías</option>' +
    categoriasCache.map(c => `<option value="${c.id_categoria}">${c.nombre}</option>`).join('');
  // Modal
  categoriaSelect.innerHTML = categoriasCache.map(c => `<option value="${c.id_categoria}">${c.nombre}</option>`).join('');
}

// Cargar subcategorías
async function cargarSubcategorias() {
  const params = new URLSearchParams();
  const nombre = (filtroNombre.value || '').trim();
  const idCat = (filtroCategoria.value || '').trim();
  if (idCat) params.set('categoria_id', idCat);
  const data = await getData(`${API_BASE}/subcategorias?${params.toString()}`);
  const filtradas = nombre ? data.filter(s => s.nombre.toLowerCase().includes(nombre.toLowerCase())) : data;
  renderTabla(filtradas);
}

function renderTabla(items) {
  tablaSubcategorias.innerHTML = items.map(item => `
    <tr>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.id_subcategoria}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${item.nombre}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${(categoriasCache.find(c => c.id_categoria === item.id_categoria)?.nombre) || '-'}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.descripcion || '-'}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
        <button class="btn-editar bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded" data-id="${item.id_subcategoria}">Editar</button>
        <button class="btn-eliminar bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded" data-id="${item.id_subcategoria}">Eliminar</button>
      </td>
    </tr>
  `).join('');

  // Bind botones
  tablaSubcategorias.querySelectorAll('.btn-editar').forEach(btn => {
    btn.addEventListener('click', () => abrirEditar(parseInt(btn.dataset.id, 10)));
  });
  tablaSubcategorias.querySelectorAll('.btn-eliminar').forEach(btn => {
    btn.addEventListener('click', () => confirmarEliminar(parseInt(btn.dataset.id, 10)));
  });
}

function limpiarFormulario() {
  subcategoriaIdInput.value = '';
  nombreInput.value = '';
  descripcionInput.value = '';
  if (categoriaSelect.options.length) categoriaSelect.selectedIndex = 0;
}

function abrirNuevo() {
  tituloModal.textContent = 'Nueva Subcategoría';
  limpiarFormulario();
  showModal(modalSubcategoria);
}

async function abrirEditar(id) {
  const item = await getData(`${API_BASE}/subcategorias/${id}`);
  tituloModal.textContent = 'Editar Subcategoría';
  subcategoriaIdInput.value = item.id_subcategoria;
  nombreInput.value = item.nombre || '';
  descripcionInput.value = item.descripcion || '';
  if (item.id_categoria) categoriaSelect.value = String(item.id_categoria);
  showModal(modalSubcategoria);
}

function confirmarEliminar(id) {
  subcategoriaAEliminar = id;
  showModal(modalConfirmar);
}

async function eliminarConfirmado() {
  if (!subcategoriaAEliminar) return;
  await deleteData(`${API_BASE}/subcategorias/${subcategoriaAEliminar}`);
  subcategoriaAEliminar = null;
  hideModal(modalConfirmar);
  await cargarSubcategorias();
}

async function guardarSubcategoria(e) {
  e.preventDefault();
  const payload = {
    nombre: nombreInput.value.trim(),
    descripcion: (descripcionInput.value || '').trim() || null,
    id_categoria: parseInt(categoriaSelect.value, 10)
  };
  const id = subcategoriaIdInput.value ? parseInt(subcategoriaIdInput.value, 10) : null;
  if (id) {
    await updateData(`${API_BASE}/subcategorias/${id}`, payload);
  } else {
    await postData(`${API_BASE}/subcategorias`, payload);
  }
  hideModal(modalSubcategoria);
  await cargarSubcategorias();
}

// Eventos
btnBuscar.addEventListener('click', cargarSubcategorias);
btnNuevaSubcategoria.addEventListener('click', abrirNuevo);
btnCerrarModal.addEventListener('click', () => hideModal(modalSubcategoria));
btnCancelar.addEventListener('click', () => hideModal(modalSubcategoria));
btnCancelarEliminar.addEventListener('click', () => hideModal(modalConfirmar));
btnConfirmarEliminar.addEventListener('click', eliminarConfirmado);
formSubcategoria.addEventListener('submit', guardarSubcategoria);
filtroCategoria.addEventListener('change', cargarSubcategorias);

// Init
(async function init() {
  try {
    await cargarCategorias();
    await cargarSubcategorias();
  } catch (err) {
    console.error('Error inicializando subcategorías:', err);
    alert('Error cargando datos de subcategorías: ' + err.message);
  }
})();
