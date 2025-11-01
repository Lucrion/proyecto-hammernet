// Importar funciones de API con autenticación
import { getData, postData, updateData, deleteData, fetchWithAuth } from '../utils/api.js';

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
        productos = await getData('/api/productos');
        console.log('Productos cargados:', productos);
    } catch (error) {
        console.error('Error al obtener productos:', error);
    }
}

// Función para obtener categorías
async function obtenerCategorias() {
    try {
        categorias = await getData('/api/categorias');
        console.log('Categorías cargadas:', categorias);
    } catch (error) {
        console.error('Error al obtener categorías:', error);
    }
}

// Función para obtener inventario
async function obtenerInventario() {
    try {
        inventario = await getData('/api/productos/inventario');
        console.log('Inventario cargado:', inventario);
    } catch (error) {
        console.error('Error al obtener inventario:', error);
    }
}

// Función para obtener catálogo público
async function obtenerCatalogo() {
    try {
        const catalogo = await getData('/api/productos/catalogo');
        console.log('Catálogo cargado:', catalogo);
        return catalogo;
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
        // Header para productos completos (catálogo)
        tablaHeader.innerHTML = `
            <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Imagen del Producto</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre del Producto</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Marca</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descripción</th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
        `;
        
        cargarProductosCompletos(productosCatalogados);
    } else {
        // Header para productos básicos (inventario): Código, Nombre, Precio, Categoría
        tablaHeader.innerHTML = `
            <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precio</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
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
        const imagen = producto.imagen_url || '/herramientas.webp';
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <img src="${imagen}" alt="${producto.nombre}" class="h-12 w-12 rounded object-cover" onerror="this.src='/herramientas.webp'">
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${producto.nombre || 'Sin nombre'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${producto.marca || 'Sin marca'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${producto.descripcion || 'Sin descripción'}</td>
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
                <td colspan="5" class="px-6 py-4 text-center text-gray-500">
                    No hay productos en inventario
                </td>
            </tr>
        `;
        return;
    }
    
    productosAMostrar.forEach(producto => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${producto.codigo_interno || 'N/A'}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">${producto.nombre || 'Sin nombre'}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${(producto.precio_inventario != null ? producto.precio_inventario : (producto.precio_venta != null ? producto.precio_venta : 0)).toLocaleString()}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${producto.categoria || 'Sin categoría'}</td>
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
        // Ofertas
        const ofertaActivaEl = document.getElementById('editarOfertaActiva');
        const tipoOfertaEl = document.getElementById('editarTipoOferta');
        const valorOfertaEl = document.getElementById('editarValorOferta');
        const inicioOfertaEl = document.getElementById('editarInicioOferta');
        const finOfertaEl = document.getElementById('editarFinOferta');

        if (ofertaActivaEl) ofertaActivaEl.checked = !!producto.oferta_activa;
        if (tipoOfertaEl) tipoOfertaEl.value = producto.tipo_oferta || '';
        if (valorOfertaEl) valorOfertaEl.value = (producto.valor_oferta ?? '');
        // Fechas (si el catálogo no trae fechas, quedan vacías)
        const toLocalInput = (iso) => {
            try {
                if (!iso) return '';
                const d = new Date(iso);
                const pad = (n) => String(n).padStart(2, '0');
                const yyyy = d.getFullYear();
                const mm = pad(d.getMonth() + 1);
                const dd = pad(d.getDate());
                const hh = pad(d.getHours());
                const mi = pad(d.getMinutes());
                return `${yyyy}-${mm}-${dd}T${hh}:${mi}`;
            } catch { return ''; }
        };
        if (inicioOfertaEl) inicioOfertaEl.value = toLocalInput(producto.fecha_inicio_oferta);
        if (finOfertaEl) finOfertaEl.value = toLocalInput(producto.fecha_fin_oferta);
        
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
        imagen_base64: null, // Se actualizará si hay imagen
        // Oferta
        oferta_activa: document.getElementById('catalogarOfertaActiva')?.checked || false,
        tipo_oferta: document.getElementById('catalogarTipoOferta')?.value || null,
        valor_oferta: (function(){
            const v = document.getElementById('catalogarValorOferta')?.value;
            return v !== '' ? parseFloat(v) : null;
        })(),
        fecha_inicio_oferta: (function(){
            const v = document.getElementById('catalogarInicioOferta')?.value;
            return v ? new Date(v).toISOString() : null;
        })(),
        fecha_fin_oferta: (function(){
            const v = document.getElementById('catalogarFinOferta')?.value;
            return v ? new Date(v).toISOString() : null;
        })()
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
        caracteristicas: document.getElementById('editarCaracteristicas').value || null,
        // Ofertas
        oferta_activa: document.getElementById('editarOfertaActiva')?.checked || false,
        tipo_oferta: document.getElementById('editarTipoOferta')?.value || null,
        valor_oferta: (function(){
            const v = document.getElementById('editarValorOferta')?.value;
            return v !== '' ? parseFloat(v) : null;
        })(),
        fecha_inicio_oferta: (function(){
            const v = document.getElementById('editarInicioOferta')?.value;
            return v ? new Date(v).toISOString() : null;
        })(),
        fecha_fin_oferta: (function(){
            const v = document.getElementById('editarFinOferta')?.value;
            return v ? new Date(v).toISOString() : null;
        })()
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