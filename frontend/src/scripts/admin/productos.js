// Importar configuración de API
import { API_URL } from '../utils/config.js';
import { getData, fetchWithAuth, postData, updateData, deleteData } from '../utils/api.js';

// Variables globales
let paginaActual = 0;
const productosPorPagina = 20;
let totalProductos = 0;
let productoEditando = null;
let productoAEliminar = null;
let categorias = [];
let proveedores = [];
let subcategorias = [];

// Elementos del DOM
const tablaProductos = document.getElementById('tablaProductos');
const modalProducto = document.getElementById('modalProducto');
const modalEliminar = document.getElementById('modalEliminar');
const formProducto = document.getElementById('formProducto');
const tituloModal = document.getElementById('tituloModal');
const btnNuevoProducto = document.getElementById('btnNuevoProducto');
const btnCancelar = document.getElementById('btnCancelar');
const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
const btnAnterior = document.getElementById('btnAnterior');
const btnSiguiente = document.getElementById('btnSiguiente');
const btnFiltrar = document.getElementById('btnFiltrar');

// Obtener token de autenticación
function getAuthToken() {
    return sessionStorage.getItem('token') || localStorage.getItem('token');
}

// Verificar autenticación
function verificarAuth() {
    const token = getAuthToken();
    if (!token) {
        window.location.href = '/login?tipo=trabajador';
        return false;
    }
    return true;
}

// Cargar categorías
async function cargarCategorias() {
    try {
        const data = await getData('/api/categorias/');
        categorias = data;
            const selectCategoria = document.getElementById('id_categoria');
            const filtroCategoria = document.getElementById('filtroCategoria');
            
            selectCategoria.innerHTML = '<option value="">Seleccionar categoría</option>';
            filtroCategoria.innerHTML = '<option value="">Todas las categorías</option>';
            
            categorias.forEach(categoria => {
                const option1 = new Option(categoria.nombre, categoria.id_categoria);
                const option2 = new Option(categoria.nombre, categoria.id_categoria);
                selectCategoria.add(option1);
                filtroCategoria.add(option2);
            });

            if (selectCategoria) {
                selectCategoria.onchange = async (e) => {
                    const categoriaId = parseInt(e.target.value) || null;
                    const subEl = document.getElementById('id_subcategoria');
                    if (subEl) {
                        subEl.innerHTML = '<option value="">Seleccionar subcategoría</option>';
                        subEl.disabled = true;
                    }
                    await cargarSubcategorias(categoriaId);
                };
            }
    } catch (error) {
        console.error('Error al cargar categorías:', error);
    }
}

// Cargar proveedores
async function cargarProveedores() {
    try {
        const data = await getData('/api/proveedores/');
        proveedores = data;
            const selectProveedor = document.getElementById('id_proveedor');
            const filtroProveedor = document.getElementById('filtroProveedor');
            
            selectProveedor.innerHTML = '<option value="">Seleccionar proveedor</option>';
            filtroProveedor.innerHTML = '<option value="">Todos los proveedores</option>';
            
            proveedores.forEach(proveedor => {
                const option1 = new Option(proveedor.nombre, proveedor.id_proveedor);
                const option2 = new Option(proveedor.nombre, proveedor.id_proveedor);
                selectProveedor.add(option1);
                filtroProveedor.add(option2);
            });
    } catch (error) {
        console.error('Error al cargar proveedores:', error);
    }
}

async function cargarSubcategorias(categoriaId) {
    try {
        const subEl = document.getElementById('id_subcategoria');
        if (!subEl) return;
        subEl.innerHTML = '<option value="">Seleccionar subcategoría</option>';
        if (!categoriaId) { subEl.disabled = true; subcategorias = []; return; }
        const data = await getData(`/api/subcategorias?categoria_id=${categoriaId}&_=${Date.now()}`);
        subcategorias = Array.isArray(data) ? data : [];
        if (subcategorias.length > 0) {
            subcategorias.forEach(sub => {
                const opt = new Option(sub.nombre, sub.id_subcategoria);
                subEl.add(opt);
            });
            subEl.disabled = false;
        } else {
            subEl.disabled = true;
        }
    } catch (error) {
        console.error('Error al cargar subcategorías:', error);
        const subEl = document.getElementById('id_subcategoria');
        if (subEl) subEl.disabled = true;
    }
}

// Cargar productos
async function cargarProductos() {
    try {
        const filtroNombre = document.getElementById('filtroNombre').value;
        const filtroCategoria = document.getElementById('filtroCategoria').value;
        const filtroProveedor = document.getElementById('filtroProveedor').value;
        
        let endpoint = `/api/productos/?skip=${paginaActual * productosPorPagina}&limit=${productosPorPagina}&_=${Date.now()}`;
        
        if (filtroCategoria) {
            endpoint += `&categoria_id=${filtroCategoria}`;
        }
        if (filtroProveedor) {
            endpoint += `&proveedor_id=${filtroProveedor}`;
        }
        
        const productos = await getData(endpoint);
        // Obtener total desde backend con los mismos filtros
        let totalEndpoint = `/api/productos/total`;
        const filtros = [];
        if (filtroCategoria) filtros.push(`categoria_id=${filtroCategoria}`);
        if (filtroProveedor) filtros.push(`proveedor_id=${filtroProveedor}`);
        if (filtros.length > 0) totalEndpoint += `?${filtros.join('&')}`;
        totalEndpoint += (totalEndpoint.includes('?') ? '&' : '?') + `_=${Date.now()}`;
        try {
            const totalResp = await getData(totalEndpoint);
            totalProductos = (totalResp && typeof totalResp.total === 'number') ? totalResp.total : productos.length;
        } catch (e) {
            totalProductos = productos.length;
        }
            
            // Filtrar por nombre en el frontend si se especifica
            let productosFiltrados = productos;
            if (filtroNombre) {
                productosFiltrados = productos.filter(producto => 
                    producto.nombre.toLowerCase().includes(filtroNombre.toLowerCase())
                );
            }
            
            mostrarProductos(productosFiltrados);
            actualizarPaginacion(productosFiltrados.length);
    } catch (error) {
        console.error('Error al cargar productos:', error);
    }
}

// Mostrar productos en la tabla
function mostrarProductos(productos) {
    tablaProductos.innerHTML = '';
    
    productos.forEach(producto => {
        // El backend ahora devuelve categoria como string, no como ID
        // y no incluye id_categoria ni id_proveedor en la respuesta
        
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${producto.id_producto}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${producto.nombre}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${producto.categoria || 'N/A'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${producto.proveedor || 'N/A'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$${producto.precio_venta || 0}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${producto.cantidad_disponible || 0}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${producto.stock_minimo || 0}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${producto.codigo_interno || 'N/A'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button onclick="window.editarProducto(${producto.id_producto})" class="text-indigo-600 hover:text-indigo-900 mr-3">Editar</button>
                <button onclick="window.eliminarProducto(${producto.id_producto})" class="text-red-600 hover:text-red-900">Eliminar</button>
            </td>
        `;
        tablaProductos.appendChild(fila);
    });
}

// Actualizar información de paginación
function actualizarPaginacion(cantidadMostrada) {
    const desde = paginaActual * productosPorPagina + 1;
    const hasta = Math.min(desde + cantidadMostrada - 1, totalProductos);
    
    document.getElementById('mostrandoDesde').textContent = cantidadMostrada > 0 ? desde : 0;
    document.getElementById('mostrandoHasta').textContent = hasta;
    document.getElementById('totalProductos').textContent = totalProductos;
    
    btnAnterior.disabled = paginaActual === 0;
    btnSiguiente.disabled = hasta >= totalProductos;
}

// Abrir modal para nuevo producto
function abrirModalNuevo() {
    productoEditando = null;
    tituloModal.textContent = 'Nuevo Producto';
    formProducto.reset();
    modalProducto.classList.remove('hidden');
}

// Editar producto
window.editarProducto = async function(id) {
    console.log('Editando producto con ID:', id);
    try {
        const producto = await getData(`/api/productos/${id}?_=${Date.now()}`);
            console.log('Producto recibido:', producto);
            productoEditando = producto;
            tituloModal.textContent = 'Editar Producto';
            
            // Llenar el formulario
            document.getElementById('nombre').value = producto.nombre || '';
            document.getElementById('descripcion').value = producto.descripcion || '';
            document.getElementById('precio_venta').value = producto.precio_venta || '';
            document.getElementById('costo_bruto').value = producto.costo_bruto || '';
            document.getElementById('costo_neto').value = producto.costo_neto || '';
            document.getElementById('porcentaje_utilidad').value = producto.porcentaje_utilidad || '';
            document.getElementById('utilidad_pesos').value = producto.utilidad_pesos || '';
            document.getElementById('cantidad_actual').value = producto.cantidad_disponible || 0;
            document.getElementById('stock_minimo').value = producto.stock_minimo || 5;
            document.getElementById('marca').value = producto.marca || '';
            
            // Buscar la categoría por nombre en lugar de ID
            if (producto.categoria) {
                const categoriaObj = categorias.find(c => c.nombre === producto.categoria);
                if (categoriaObj) {
                    document.getElementById('id_categoria').value = categoriaObj.id_categoria;
                    await cargarSubcategorias(categoriaObj.id_categoria);
                    const subEl = document.getElementById('id_subcategoria');
                    if (subEl && producto.id_subcategoria) {
                        subEl.value = producto.id_subcategoria;
                        subEl.disabled = false;
                    }
                } else {
                    document.getElementById('id_categoria').value = '';
                }
            } else {
                document.getElementById('id_categoria').value = '';
            }
            
            // El proveedor ya no se usa en el nuevo formato
            
            console.log('Abriendo modal...');
            modalProducto.classList.remove('hidden');
    } catch (error) {
        console.error('Error al cargar producto:', error);
    }
}

// Eliminar producto
window.eliminarProducto = function(id) {
    productoAEliminar = id;
    modalEliminar.classList.remove('hidden');
}

// Confirmar eliminación
async function confirmarEliminacion() {
    try {
        const response = await deleteData(`/api/productos/${productoAEliminar}`);
        if (response) {
            modalEliminar.classList.add('hidden');
            cargarProductos();
        } else {
            alert('Error en conexión del servidor');
        }
    } catch (error) {
        console.error('Error al eliminar producto:', error);
        let errorMessage = 'Error al eliminar producto';
        
        // Intentar extraer el mensaje de error detallado
        if (error.message) {
            errorMessage += ': ' + error.message;
        } else if (typeof error === 'object') {
            errorMessage += ': ' + JSON.stringify(error);
        }
        
        alert('Error en conexión del servidor');
    }
}

// Guardar producto
async function guardarProducto(event) {
    event.preventDefault();
    console.log('Iniciando guardado de producto...');
    
    const formData = new FormData(formProducto);
    const subcatRaw = (document.getElementById('id_subcategoria')?.value || '').trim();
    
    // Obtener y validar id_categoria
    const categoriaValue = formData.get('id_categoria');
    const id_categoria = categoriaValue && categoriaValue !== '' ? parseInt(categoriaValue) : null;
    
    // Obtener y validar id_proveedor
    const proveedorValue = formData.get('id_proveedor');
    const id_proveedor = proveedorValue && proveedorValue !== '' ? parseInt(proveedorValue) : null;
    
    const producto = {
        nombre: formData.get('nombre'),
        descripcion: formData.get('descripcion'),
        marca: formData.get('marca'),
        id_categoria: id_categoria,
        id_proveedor: id_proveedor,
        id_subcategoria: (function(){
            const val = (subcatRaw || (formData.get('id_subcategoria') || '')).trim();
            if (val === '' || val.toLowerCase() === 'null') return null;
            const num = parseInt(val, 10);
            return isNaN(num) ? null : num;
        })(),
        costo_bruto: parseFloat(formData.get('costo_bruto')) || 0,
        costo_neto: parseFloat(formData.get('costo_neto')) || 0,
        precio_venta: parseFloat(formData.get('precio_venta')) || 0,
        porcentaje_utilidad: parseFloat(formData.get('porcentaje_utilidad')) || 0,
        utilidad_pesos: parseFloat(formData.get('utilidad_pesos')) || 0,
        cantidad_actual: parseInt(formData.get('cantidad_actual')) || 0,
        stock_minimo: parseInt(formData.get('stock_minimo')) || 5
    };
    
    console.log('Datos del producto a guardar:', producto);
    
    // Validar que id_categoria no sea null (es requerido)
    if (!id_categoria) {
        alert('Por favor selecciona una categoría');
        return;
    }
    
    try {
        const endpoint = productoEditando ? `/api/productos/${productoEditando.id_producto}` : `/api/productos/`;
        const method = productoEditando ? 'PUT' : 'POST';
        
        console.log('Endpoint:', endpoint);
        console.log('Method:', method);
        console.log('Producto editando:', productoEditando);
        
        const response = method === 'PUT' 
            ? await updateData(endpoint, producto)
            : await postData(endpoint, producto);

    if (response) {
        console.log('Producto guardado exitosamente');
        modalProducto.classList.add('hidden');
        cargarProductos();
    } else {
        alert(`Error del servidor`);
    }
    } catch (error) {
        console.error('Error al guardar producto:', error);
        let msg = 'Error al guardar producto';
        const text = String(error && error.message ? error.message : '');
        try {
            const jsonStr = text.replace(/^Error\s+\d+:\s+/, '');
            const data = JSON.parse(jsonStr);
            if (data && data.detail) {
                msg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
            }
        } catch {}
        alert(msg);
    }
}

// Event listeners
btnNuevoProducto.addEventListener('click', abrirModalNuevo);
btnCancelar.addEventListener('click', () => modalProducto.classList.add('hidden'));
btnCancelarEliminar.addEventListener('click', () => modalEliminar.classList.add('hidden'));
btnConfirmarEliminar.addEventListener('click', confirmarEliminacion);
formProducto.addEventListener('submit', guardarProducto);
btnFiltrar.addEventListener('click', () => {
    paginaActual = 0;
    cargarProductos();
});
btnAnterior.addEventListener('click', () => {
    if (paginaActual > 0) {
        paginaActual--;
        cargarProductos();
    }
});
btnSiguiente.addEventListener('click', () => {
    paginaActual++;
    cargarProductos();
});

// Cerrar modales al hacer clic fuera
modalProducto.addEventListener('click', (e) => {
    if (e.target === modalProducto) {
        modalProducto.classList.add('hidden');
    }
});
modalEliminar.addEventListener('click', (e) => {
    if (e.target === modalEliminar) {
        modalEliminar.classList.add('hidden');
    }
});

// Inicializar página
document.addEventListener('DOMContentLoaded', () => {
    if (verificarAuth()) {
        cargarCategorias();
        cargarProveedores();
        cargarProductos();
    }
});
