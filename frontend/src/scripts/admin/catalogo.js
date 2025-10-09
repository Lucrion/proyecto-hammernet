// Importar funciones de API con autenticación
import { getData, postData, updateData, deleteData, fetchWithAuth } from '../utils/api.js';
import { API_URL } from '../utils/config.js';

// Variables globales
let base64Image = null;
let catalogarBase64Image = null; // Nueva variable para el formulario de catalogación
let editarBase64Image = null; // Nueva variable para el formulario de edición
let productos = [];
let productosCatalogados = [];
let productosInventario = [];
let categorias = [];
let inventario = [];
let tabActiva = 'completos'; // 'completos' o 'basicos'

// Elementos del DOM
let btnNuevoProducto, formProducto, formTitle, productoForm, btnCancelar;
let tablaProductos, productoId, buscador, btnBuscar;
let imagePreviewContainer, imagePreview, imageFileInput, dragText, imagenInput;

// Verificar si el usuario está autenticado
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar elementos del DOM
    btnNuevoProducto = document.getElementById('btnNuevoProducto');
    formProducto = document.getElementById('formProducto');
    formTitle = document.getElementById('formTitle');
    productoForm = document.getElementById('productoForm');
    btnCancelar = document.getElementById('btnCancelar');
    tablaProductos = document.getElementById('tablaProductos');
    productoId = document.getElementById('productoId');
    buscador = document.getElementById('buscador');
    btnBuscar = document.getElementById('btnBuscar');
    
    // Elementos para la carga de imágenes
    imagePreviewContainer = document.getElementById('imagePreviewContainer');
    imagePreview = document.getElementById('imagePreview');
    imageFileInput = document.getElementById('imageFileInput');
    dragText = document.getElementById('dragText');
    imagenInput = document.getElementById('imagen');

    // Cargar datos al iniciar la página
    cargarDatos();

    // Configurar eventos de pestañas
    const tabCompletos = document.getElementById('tabCompletos');
    const tabBasicos = document.getElementById('tabBasicos');
    
    tabCompletos.addEventListener('click', () => cambiarTab('completos'));
    tabBasicos.addEventListener('click', () => cambiarTab('basicos'));

    // Event listeners
    if (btnNuevoProducto) {
        btnNuevoProducto.addEventListener('click', mostrarFormulario);
    }
    
    if (btnCancelar) {
        btnCancelar.addEventListener('click', ocultarFormulario);
    }
    
    if (productoForm) {
        productoForm.addEventListener('submit', guardarProducto);
    }
    
    if (buscador) {
        buscador.addEventListener('input', buscarProductos);
    }
    
    if (btnBuscar) {
        btnBuscar.addEventListener('click', buscarProductos);
    }

    // Configurar drag and drop para imágenes
    if (imagePreviewContainer) {
        configurarDragAndDrop();
    }

    // Event listeners para el modal de confirmación
    const modalConfirmar = document.getElementById('modalConfirmar');
    const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    
    if (btnCancelarEliminar) {
        btnCancelarEliminar.addEventListener('click', cerrarModalConfirmar);
    }
    
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', confirmarEliminar);
    }

    // Event listeners para el modal de catalogar
    const catalogarForm = document.getElementById('catalogarProductoForm');
    if (catalogarForm) {
        catalogarForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await guardarCatalogacion();
        });
    }

    // Event listeners para manejo de imagen en catalogación
    const catalogarCambiarImagen = document.getElementById('catalogarCambiarImagen');
    const catalogarImagenFile = document.getElementById('catalogarImagenFile');
    const catalogarImagenPreview = document.getElementById('catalogarImagenPreview');
    const catalogarImagenPlaceholder = document.getElementById('catalogarImagenPlaceholder');

    if (catalogarCambiarImagen && catalogarImagenFile) {
        catalogarCambiarImagen.addEventListener('click', () => {
            catalogarImagenFile.click();
        });

        catalogarImagenFile.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    catalogarBase64Image = e.target.result;
                    catalogarImagenPreview.src = e.target.result;
                    catalogarImagenPreview.style.display = 'block';
                    catalogarImagenPlaceholder.style.display = 'none';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Event listeners para el modal de editar catalogado
    const editarForm = document.getElementById('editarProductoForm');
    if (editarForm) {
        editarForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await guardarEdicionCatalogado();
        });
    }

    // Event listeners para manejo de imagen en edición
    const editarCambiarImagen = document.getElementById('editarCambiarImagen');
    const editarImagenFile = document.getElementById('editarImagenFile');
    const editarImagenPreview = document.getElementById('editarImagenPreview');
    const editarImagenPlaceholder = document.getElementById('editarImagenPlaceholder');

    if (editarCambiarImagen && editarImagenFile) {
        editarCambiarImagen.addEventListener('click', () => {
            editarImagenFile.click();
        });

        editarImagenFile.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    editarBase64Image = e.target.result;
                    editarImagenPreview.src = e.target.result;
                    editarImagenPreview.style.display = 'block';
                    editarImagenPlaceholder.style.display = 'none';
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Cerrar modal al hacer clic fuera de él
    if (modalConfirmar) {
        modalConfirmar.addEventListener('click', (e) => {
            if (e.target === modalConfirmar) {
                cerrarModalConfirmar();
            }
        });
    }
});

// Función para obtener productos desde la API
async function obtenerProductos() {
    try {
        const response = await fetch(`${API_URL}/api/productos`);
        
        if (response.ok) {
            productos = await response.json();
            console.log('Productos cargados:', productos);
        } else {
            console.error('Error al obtener productos');
        }
    } catch (error) {
        console.error('Error al obtener productos:', error);
    }
}

// Función para obtener categorías
async function obtenerCategorias() {
    try {
        const response = await fetch(`${API_URL}/api/categorias`);
        
        if (response.ok) {
            categorias = await response.json();
            console.log('Categorías cargadas:', categorias);
        } else {
            console.error('Error al obtener categorías');
        }
    } catch (error) {
        console.error('Error al obtener categorías:', error);
    }
}

// Función para obtener inventario
async function obtenerInventario() {
    try {
        const response = await fetch(`${API_URL}/api/productos/inventario`);
        
        if (response.ok) {
            inventario = await response.json();
            console.log('Inventario cargado:', inventario);
        } else {
            console.error('Error al obtener inventario:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('Error al obtener inventario:', error);
    }
}

// Función para obtener catálogo público
async function obtenerCatalogo() {
    try {
        const response = await fetch(`${API_URL}/api/productos/catalogo`);
        
        if (response.ok) {
            const catalogo = await response.json();
            console.log('Catálogo cargado:', catalogo);
            return catalogo;
        } else {
            console.error('Error al obtener catálogo');
            return [];
        }
    } catch (error) {
        console.error('Error al obtener catálogo:', error);
        return [];
    }
}

// Función para obtener datos del catálogo e inventario unificado
async function obtenerCatalogoInventario() {
    try {
        // Obtener inventario completo
        await obtenerInventario();
        
        // Obtener catálogo público
        const catalogoPublico = await obtenerCatalogo();
        
        console.log('Inventario obtenido:', inventario);
        console.log('Catálogo público obtenido:', catalogoPublico);
        
        // Separar productos catalogados de inventario básico
        productosCatalogados = catalogoPublico;
        
        // TODOS los productos del inventario para mostrar en la pestaña "Productos Básicos"
        productosInventario = inventario.map(itemInventario => ({
            ...itemInventario.producto,
            precio_inventario: itemInventario.precio,
            cantidad_disponible: itemInventario.cantidad,
            fecha_registro: itemInventario.fecha_registro
        }));
        
        // Mantener compatibilidad con el código existente
        productos = [...productosCatalogados, ...productosInventario];
        
        console.log('Datos cargados:', {
            catalogados: productosCatalogados.length,
            inventario: productosInventario.length,
            total: productos.length
        });
        
    } catch (error) {
        console.error('Error al obtener datos del catálogo e inventario:', error);
        throw error;
    }
}

// Función para cargar datos iniciales
async function cargarDatos() {
    await Promise.all([
        obtenerCatalogoInventario(),
        obtenerCategorias()
    ]);
    actualizarContadores();
    mostrarTablaSegunPestana();
}

// Función para cambiar de pestaña
function cambiarTab(nuevaTab) {
    tabActiva = nuevaTab;
    
    // Actualizar estilos de pestañas
    document.querySelectorAll('.tab-button').forEach(tab => {
        tab.classList.remove('active', 'border-blue-500', 'text-blue-600');
        tab.classList.add('border-transparent', 'text-gray-500');
    });
    
    const tabActivo = document.getElementById(nuevaTab === 'completos' ? 'tabCompletos' : 'tabBasicos');
    tabActivo.classList.add('active', 'border-blue-500', 'text-blue-600');
    tabActivo.classList.remove('border-transparent', 'text-gray-500');
    
    mostrarTablaSegunPestana();
}

// Función para actualizar contadores
function actualizarContadores() {
    const countCompletos = document.getElementById('countCompletos');
    const countBasicos = document.getElementById('countBasicos');
    
    // Productos completos: productos catalogados
    countCompletos.textContent = productosCatalogados.length;
    
    // Productos básicos: productos en inventario
    countBasicos.textContent = productosInventario.length;
}

// Función para mostrar tabla según pestaña activa
function mostrarTablaSegunPestana() {
    const tablaHeader = document.getElementById('tablaHeader');
    
    if (tabActiva === 'completos') {
        // Header para productos completos
        tablaHeader.innerHTML = `
            <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precio</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
        `;
        
        cargarProductosCompletos(productosCatalogados);
    } else {
        // Header para productos básicos (inventario)
        tablaHeader.innerHTML = `
            <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Producto</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precio</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
        `;
        
        cargarProductosBasicos(productosInventario);
    }
}

// Cargar productos completos en la tabla
function cargarProductosCompletos(productosAMostrar) {
    tablaProductos.innerHTML = '';
    
    productosAMostrar.forEach(producto => {
        // Obtener información de categoría
        const categoria = categorias.find(c => c.id_categoria === producto.id_categoria);
        const nombreCategoria = categoria ? categoria.nombre : 'Sin categoría';
        
        // Obtener stock del inventario
        const itemInventario = inventario.find(i => i.id_producto === producto.id_producto);
        const stock = itemInventario ? itemInventario.stock_actual : 0;
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${producto.id_producto}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${producto.nombre}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${producto.precio ? '$' + producto.precio.toFixed(2) : 'Sin precio'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    ${nombreCategoria}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button data-id="${producto.id_producto}" class="btn-editar-catalogado text-blue-600 hover:text-blue-900 mr-3" title="Editar producto catalogado">
                    <svg class="h-4 w-4 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Editar
                </button>
                <button data-id="${producto.id_producto}" class="btn-eliminar-catalogado text-red-600 hover:text-red-900" title="Eliminar del catálogo">
                    <svg class="h-4 w-4 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Eliminar
                </button>
            </td>
        `;
        tablaProductos.appendChild(tr);
    });

    // Agregar eventos a los botones de editar y eliminar catalogados
    document.querySelectorAll('.btn-editar-catalogado').forEach(btn => {
        btn.addEventListener('click', editarProductoCatalogado);
    });

    document.querySelectorAll('.btn-eliminar-catalogado').forEach(btn => {
        btn.addEventListener('click', eliminarProductoCatalogado);
    });
}

// Cargar productos básicos (inventario) en la tabla
function cargarProductosBasicos(productosAMostrar) {
    tablaProductos.innerHTML = '';
    
    if (productosAMostrar.length === 0) {
        tablaProductos.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    No hay productos en inventario
                </td>
            </tr>
        `;
        return;
    }
    
    productosAMostrar.forEach(producto => {
        // Obtener información de categoría
        const categoria = categorias.find(c => c.id_categoria === producto.id_categoria);
        const nombreCategoria = categoria ? categoria.nombre : 'Sin categoría';
        
        // Usar los datos del inventario directamente
        const stock = producto.cantidad_disponible || 0;
        const precio = producto.precio_inventario || 0;
        
        // Determinar estado del stock
        let estadoStock = 'disponible';
        let estadoClass = 'bg-green-100 text-green-800';
        
        if (stock === 0) {
            estadoStock = 'agotado';
            estadoClass = 'bg-red-100 text-red-800';
        } else if (stock <= (producto.stock_minimo || 0)) {
            estadoStock = 'stock bajo';
            estadoClass = 'bg-yellow-100 text-yellow-800';
        }
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${producto.codigo_interno || 'P-' + producto.id_producto}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div>
                        <div class="text-sm font-medium text-gray-900">${producto.nombre}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${precio ? '$' + precio.toLocaleString() : 'Sin precio'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <div class="text-sm font-medium">${stock}</div>
                <div class="text-xs text-gray-500">Mín: ${producto.stock_minimo || 0}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">${nombreCategoria}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${estadoClass}">
                    ${estadoStock.charAt(0).toUpperCase() + estadoStock.slice(1)}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                    <button onclick="editarInventario(${producto.id_producto})" class="text-blue-600 hover:text-blue-900" title="Editar inventario">
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                    </button>
                    <button onclick="catalogarProducto(${producto.id_producto})" class="btn-catalogar" title="Catalogar producto">
                        <svg class="h-4 w-4 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                        Catalogar
                    </button>
                </div>
            </td>
        `;
        tablaProductos.appendChild(tr);
    });
}

// Función para buscar productos
function buscarProductos() {
    const termino = buscador.value.toLowerCase();
    
    if (tabActiva === 'completos') {
        const productosFiltrados = productosCatalogados.filter(producto => 
            producto.nombre.toLowerCase().includes(termino) ||
            (producto.descripcion && producto.descripcion.toLowerCase().includes(termino))
        );
        cargarProductosCompletos(productosFiltrados);
    } else {
        const productosFiltrados = productosInventario.filter(producto => 
            producto.nombre.toLowerCase().includes(termino) ||
            (producto.descripcion && producto.descripcion.toLowerCase().includes(termino))
        );
        cargarProductosBasicos(productosFiltrados);
    }
}

// Función para mostrar formulario
function mostrarFormulario() {
    formTitle.textContent = 'Nuevo Producto';
    productoForm.reset();
    productoId.value = '';
    base64Image = null;
    resetearVistaPrevia();
    formProducto.classList.remove('hidden');
}

// Función para ocultar formulario
function ocultarFormulario() {
    formProducto.classList.add('hidden');
    productoForm.reset();
    productoId.value = '';
    base64Image = null;
    resetearVistaPrevia();
}

// Función para resetear vista previa de imagen
function resetearVistaPrevia() {
    if (imagePreview) {
        imagePreview.src = '';
        imagePreview.classList.add('hidden');
    }
    if (dragText) {
        dragText.classList.remove('hidden');
    }
}

// Configurar drag and drop para imágenes
function configurarDragAndDrop() {
    const dropArea = imagePreviewContainer;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        dropArea.classList.add('border-blue-500', 'bg-blue-50');
    }
    
    function unhighlight(e) {
        dropArea.classList.remove('border-blue-500', 'bg-blue-50');
    }
    
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        handleFiles(files);
    }
    
    // También manejar clic en el área
    dropArea.addEventListener('click', () => {
        imageFileInput.click();
    });
    
    imageFileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
    
    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    base64Image = e.target.result;
                    imagePreview.src = base64Image;
                    imagePreview.classList.remove('hidden');
                    dragText.classList.add('hidden');
                };
                reader.readAsDataURL(file);
            }
        }
    }
}

// Función para guardar producto
async function guardarProducto(e) {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.textContent;
    
    try {
        // Deshabilitar botón y mostrar estado de carga
        submitBtn.disabled = true;
        submitBtn.textContent = 'Guardando...';
        
        const formData = new FormData(productoForm);
        
        // Agregar imagen si existe
        if (base64Image) {
            formData.append('imagen_base64', base64Image);
        }
        
        const id = productoId.value;
        
        if (id) {
            // Actualizar producto existente
            await updateData(`/api/productos/${id}/`, Object.fromEntries(formData));
            alert('Producto actualizado exitosamente');
        } else {
            // Crear nuevo producto
            await postData('/api/productos/', Object.fromEntries(formData));
            alert('Producto creado exitosamente');
        }
        
        ocultarFormulario();
        cargarDatos();
        
    } catch (error) {
        console.error('Error al guardar producto:', error);
        
        // Manejar diferentes tipos de errores
        let errorMessage = 'Error desconocido';
        
        if (error && typeof error === 'object') {
            if (error.message) {
                errorMessage = error.message;
            } else if (error.detail) {
                errorMessage = error.detail;
            } else if (error.error) {
                errorMessage = error.error;
            } else {
                errorMessage = JSON.stringify(error);
            }
        } else if (typeof error === 'string') {
            errorMessage = error;
        } else {
            errorMessage = String(error);
        }
        
        alert('Error en conexión del servidor');
    } finally {
        // Restaurar el botón de envío
        submitBtn.disabled = false;
        submitBtn.textContent = originalBtnText;
    }
}

// Función para catalogar producto
function catalogarProducto(idProducto) {
    const producto = productosInventario.find(p => p.id_producto === idProducto);
    if (!producto) {
        alert('Producto no encontrado');
        return;
    }
    
    // Abrir modal de catalogación
    const modal = document.getElementById('modalCatalogar');
    if (modal) {
        // Llenar datos del producto
        document.getElementById('catalogarProductoId').value = producto.id_producto;
        document.getElementById('catalogarNombre').value = producto.nombre;
        document.getElementById('catalogarDescripcion').value = producto.descripcion || '';
        document.getElementById('catalogarCaracteristicas').value = producto.caracteristicas || '';
        document.getElementById('catalogarMarca').value = producto.marca || '';
        
        modal.classList.remove('hidden');
    }
}

// Función para cerrar modal de catalogar
function cerrarCatalogarModal() {
    const modal = document.getElementById('modalCatalogar');
    if (modal) {
        modal.classList.add('hidden');
        // Resetear imagen
        catalogarBase64Image = null;
        const catalogarImagenPreview = document.getElementById('catalogarImagenPreview');
        const catalogarImagenPlaceholder = document.getElementById('catalogarImagenPlaceholder');
        if (catalogarImagenPreview && catalogarImagenPlaceholder) {
            catalogarImagenPreview.style.display = 'none';
            catalogarImagenPlaceholder.style.display = 'flex';
        }
    }
}

// Función para editar producto catalogado
function editarProductoCatalogado(e) {
    const idProducto = parseInt(e.target.closest('button').dataset.id);
    const producto = productosCatalogados.find(p => p.id_producto === idProducto);
    
    if (!producto) {
        alert('Producto no encontrado');
        return;
    }
    
    // Debug: Verificar estructura de datos del producto
    console.log('Producto seleccionado para editar:', producto);
    console.log('imagen_url del producto:', producto.imagen_url);
    
    // Abrir modal de edición
    const modal = document.getElementById('modalEditarCatalogado');
    if (modal) {
        // Llenar datos del producto
        document.getElementById('editarProductoId').value = producto.id_producto;
        document.getElementById('editarNombre').value = producto.nombre;
        document.getElementById('editarMarca').value = producto.marca || '';
        document.getElementById('editarDescripcion').value = producto.descripcion || '';
        document.getElementById('editarCaracteristicas').value = producto.caracteristicas || '';
        
        // Manejar imagen del producto
        const editarImagenPreview = document.getElementById('editarImagenPreview');
        const editarImagenPlaceholder = document.getElementById('editarImagenPlaceholder');
        
        console.log('Elementos de imagen encontrados:', {
            editarImagenPreview: !!editarImagenPreview,
            editarImagenPlaceholder: !!editarImagenPlaceholder
        });
        
        if (producto.imagen_url) {
            console.log('Mostrando imagen:', producto.imagen_url);
            editarImagenPreview.src = producto.imagen_url;
            editarImagenPreview.style.display = 'block';
            editarImagenPlaceholder.style.display = 'none';
        } else {
            console.log('No hay imagen_url, mostrando placeholder');
            editarImagenPreview.style.display = 'none';
            editarImagenPlaceholder.style.display = 'flex';
        }
        
        // Resetear imagen base64
        editarBase64Image = null;
        
        modal.classList.remove('hidden');
    }
}

// Función para cerrar modal de editar
function cerrarEditarModal() {
    const modal = document.getElementById('modalEditarCatalogado');
    if (modal) {
        modal.classList.add('hidden');
        // Resetear imagen
        editarBase64Image = null;
        const editarImagenPreview = document.getElementById('editarImagenPreview');
        const editarImagenPlaceholder = document.getElementById('editarImagenPlaceholder');
        if (editarImagenPreview && editarImagenPlaceholder) {
            editarImagenPreview.style.display = 'none';
            editarImagenPlaceholder.style.display = 'flex';
        }
    }
}

// Función para editar inventario
function editarInventario(idProducto) {
    // Redirigir a la página de inventario con el ID del producto
    window.location.href = `/admin/inventario?producto=${idProducto}`;
}

// Función para eliminar producto catalogado
function eliminarProductoCatalogado(e) {
    const idProducto = parseInt(e.target.closest('button').dataset.id);
    const producto = productosCatalogados.find(p => p.id_producto === idProducto);
    
    if (!producto) {
        alert('Producto no encontrado');
        return;
    }
    
    // Mostrar modal de confirmación
    const modal = document.getElementById('modalConfirmar');
    const mensaje = document.getElementById('mensajeConfirmacion');
    
    if (modal && mensaje) {
        mensaje.textContent = `¿Está seguro que desea eliminar "${producto.nombre}" del catálogo?`;
        modal.dataset.productoId = idProducto;
        modal.classList.remove('hidden');
    }
}

// Función para cerrar modal de confirmación
function cerrarModalConfirmar() {
    const modal = document.getElementById('modalConfirmar');
    if (modal) {
        modal.classList.add('hidden');
        delete modal.dataset.productoId;
    }
}

// Función para confirmar eliminación
async function confirmarEliminar() {
    const modal = document.getElementById('modalConfirmar');
    const idProducto = modal.dataset.productoId;
    
    if (!idProducto) {
        alert('Error: ID de producto no encontrado');
        return;
    }
    
    try {
        await updateData(`/api/productos/${idProducto}/quitar-catalogo`, {});
        alert('Producto eliminado del catálogo exitosamente');
        cerrarModalConfirmar();
        cargarDatos();
    } catch (error) {
        console.error('Error al eliminar producto:', error);
        alert('Error en conexión del servidor');
    }
}

// Función para guardar catalogación
async function guardarCatalogacion() {
    const form = document.getElementById('catalogarProductoForm');
    const formData = new FormData(form);
    
    const productoId = parseInt(document.getElementById('catalogarProductoId').value);
    
    const data = {
        descripcion: document.getElementById('catalogarDescripcion').value || null,
        caracteristicas: document.getElementById('catalogarCaracteristicas').value || null,
        marca: document.getElementById('catalogarMarca').value || null,
        imagen_base64: null // Se actualizará si hay imagen
    };

    // Agregar imagen si existe
    if (catalogarBase64Image) {
        data.imagen_base64 = catalogarBase64Image;
    }

    try {
        const response = await postData(`/api/productos/${productoId}/agregar-catalogo`, data);
        if (response) {
            alert('Producto catalogado exitosamente');
            cerrarCatalogarModal();
            await cargarDatos(); // Recargar datos
        }
    } catch (error) {
        console.error('Error al catalogar producto:', error);
        alert('Error al catalogar producto');
    }
}

// Función para guardar edición de producto catalogado
async function guardarEdicionCatalogado() {
    console.log('=== INICIANDO GUARDADO DE EDICIÓN ===');
    const form = document.getElementById('editarProductoForm');
    
    const data = {
        nombre: document.getElementById('editarNombre').value,
        marca: document.getElementById('editarMarca').value || null,
        descripcion: document.getElementById('editarDescripcion').value || null,
        caracteristicas: document.getElementById('editarCaracteristicas').value || null
    };

    // Agregar imagen si se seleccionó una nueva
    if (editarBase64Image) {
        console.log('Imagen base64 detectada, agregando al payload');
        data.imagen_base64 = editarBase64Image;
    } else {
        console.log('No hay imagen base64 nueva');
    }

    const idProducto = document.getElementById('editarProductoId').value;
    
    console.log('Datos a enviar:', {
        idProducto,
        data,
        hasImage: !!editarBase64Image
    });

    try {
        console.log('Enviando petición PUT a:', `/api/productos/catalogo/${idProducto}/`);
        const response = await updateData(`/api/productos/catalogo/${idProducto}/`, data);
        console.log('Respuesta recibida:', response);
        
        if (response) {
            alert('Producto actualizado exitosamente');
            cerrarEditarModal();
            await cargarDatos(); // Recargar datos
        }
    } catch (error) {
        console.error('Error al actualizar producto:', error);
        alert('Error al actualizar producto');
    }
}

// Hacer las funciones globales para que puedan ser accedidas desde onclick
window.catalogarProducto = catalogarProducto;
window.cerrarCatalogarModal = cerrarCatalogarModal;
window.editarProductoCatalogado = editarProductoCatalogado;
window.cerrarEditarModal = cerrarEditarModal;
window.editarInventario = editarInventario;
window.eliminarProductoCatalogado = eliminarProductoCatalogado;
window.cerrarModalConfirmar = cerrarModalConfirmar;
window.confirmarEliminar = confirmarEliminar;