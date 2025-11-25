// Importar configuración de API
import { API_URL } from '../utils/config.js';
import { getData, fetchWithAuth, deleteData, updateData } from '../utils/api.js';

// Variables globales
let inventarios = [];
let productos = [];
let categorias = [];
let proveedores = [];
let subcategorias = [];
let paginaActual = 0;
const registrosPorPagina = 20;
let totalRegistros = 0;
let inventarioEditando = null;
let inventarioAEliminar = null;

// Referencias a elementos del DOM
const tablaInventario = document.getElementById('tablaInventario');
const modalInventario = document.getElementById('modalInventario');
const modalEliminar = document.getElementById('modalEliminar');
const formInventario = document.getElementById('formInventario');
const tituloModal = document.getElementById('tituloModal');
const btnNuevoInventario = document.getElementById('btnNuevoInventario');
const btnProveedores = document.getElementById('btnProveedores');
const btnCategorias = document.getElementById('btnCategorias');
const btnSubcategorias = document.getElementById('btnSubcategorias');
const btnCancelar = document.getElementById('btnCancelar');
const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
const btnAnterior = document.getElementById('btnAnterior');
const btnSiguiente = document.getElementById('btnSiguiente');
const btnAnteriorMobile = document.getElementById('btnAnteriorMobile');
const btnSiguienteMobile = document.getElementById('btnSiguienteMobile');
const btnFiltrar = document.getElementById('btnFiltrar');

// Obtener token de autenticación
function getAuthToken() {
    const token = (
        sessionStorage.getItem('token') ||
        localStorage.getItem('token') ||
        localStorage.getItem('access_token')
    );
    console.log('Token de autenticación:', token ? 'Presente' : 'No encontrado');
    return token;
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

// Cargar productos para el selector
async function cargarProductos() {
    try {
        const data = await getData(`/api/productos/?_=${Date.now()}`);
        productos = data;
        console.log('Productos cargados:', productos);
    } catch (error) {
        console.error('Error al cargar productos:', error);
    }
}

// Cargar categorías
async function cargarCategorias() {
    try {
        console.log('Cargando categorías...');
        const data = await getData('/api/categorias/');
        categorias = data;
        console.log('Categorías cargadas:', categorias);
            
            const filtroCategoria = document.getElementById('filtroCategoria');
            const categoriaProducto = document.getElementById('categoriaProducto');
            
            if (filtroCategoria) filtroCategoria.innerHTML = '<option value="">Todas las categorías</option>';
            if (categoriaProducto) categoriaProducto.innerHTML = '<option value="">Seleccionar categoría</option>';
            
            categorias.forEach(categoria => {
                if (filtroCategoria) {
                    const option1 = new Option(categoria.nombre, categoria.id_categoria);
                    filtroCategoria.add(option1);
                }
                
                if (categoriaProducto) {
                    const option2 = new Option(categoria.nombre, categoria.id_categoria);
                    categoriaProducto.add(option2);
                }
            });
            // Vincular cambio de categoría para cargar subcategorías dependientes
            if (categoriaProducto) {
                // Evitar listeners duplicados cuando se reabre el modal
                categoriaProducto.onchange = async (e) => {
                    const categoriaId = parseInt(e.target.value) || null;
                    const subEl = document.getElementById('subcategoriaProducto');
                    if (subEl) {
                        subEl.value = '';
                        subEl.disabled = true;
                        subEl.innerHTML = '<option value="">Seleccionar subcategoría</option>';
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
        console.log('Cargando proveedores...');
        const data = await getData('/api/proveedores/');
        proveedores = data;
        console.log('Proveedores cargados:', proveedores);
            
            // Cargar proveedores en el modal de producto
            const proveedorProducto = document.getElementById('proveedorProducto');
            if (proveedorProducto) {
                proveedorProducto.innerHTML = '<option value="">Seleccionar proveedor</option>';
                
                proveedores.forEach(proveedor => {
                    const option = new Option(proveedor.nombre, proveedor.id_proveedor);
                    proveedorProducto.add(option);
                });
            } else {
                console.error('Elemento proveedorProducto no encontrado');
            }

            // Cargar proveedores en el filtro
            const filtroProveedor = document.getElementById('filtroProveedor');
            if (filtroProveedor) {
                filtroProveedor.innerHTML = '<option value="">Todos los proveedores</option>';
                
                proveedores.forEach(proveedor => {
                    const option = new Option(proveedor.nombre, proveedor.id_proveedor);
                    filtroProveedor.add(option);
                });
            } else {
                console.error('Elemento filtroProveedor no encontrado');
            }
    } catch (error) {
        console.error('Error al cargar proveedores:', error);
    }
}

// Cargar subcategorías dependientes de una categoría
async function cargarSubcategorias(categoriaId) {
    try {
        const subcategoriaProducto = document.getElementById('subcategoriaProducto');
        if (!subcategoriaProducto) return;

        subcategoriaProducto.innerHTML = '<option value="">Seleccionar subcategoría</option>';

        if (!categoriaId) {
            subcategoriaProducto.disabled = true;
            subcategorias = [];
            return;
        }

        console.log('Cargando subcategorías para categoría:', categoriaId);
        const data = await getData(`/api/subcategorias?categoria_id=${categoriaId}`);
        subcategorias = data;

        if (Array.isArray(subcategorias) && subcategorias.length > 0) {
            subcategorias.forEach(sub => {
                const option = new Option(sub.nombre, sub.id_subcategoria);
                subcategoriaProducto.add(option);
            });
            subcategoriaProducto.disabled = false;
        } else {
            subcategoriaProducto.disabled = true;
        }
    } catch (error) {
        console.error('Error al cargar subcategorías:', error);
        const subcategoriaProducto = document.getElementById('subcategoriaProducto');
        if (subcategoriaProducto) {
            subcategoriaProducto.disabled = true;
        }
    }
}

// Cargar inventario
async function cargarInventario() {
    try {
        const filtroProducto = document.getElementById('filtroProducto').value;
        const filtroProveedor = document.getElementById('filtroProveedor').value;
        const filtroCategoria = document.getElementById('filtroCategoria').value;
        
        // Primero obtener el total de productos
        try {
            const totalData = await getData(`/api/productos/inventario/total?_=${Date.now()}`);
            totalRegistros = totalData.total;
        } catch (e) {
            console.warn('No se pudo obtener el total de inventario:', e);
        }
        
        // Luego obtener los productos paginados
        const urlEndpoint = `/api/productos/inventario?skip=${paginaActual * registrosPorPagina}&limit=${registrosPorPagina}&_=${Date.now()}`;
        let inventario = await getData(urlEndpoint);
            
            // Aplicar filtros en el frontend si es necesario
            if (filtroProducto) {
                inventario = inventario.filter(item => {
                    const producto = productos.find(p => 
                        (p.id && p.id === item.id_producto) || 
                        (p.id_producto && p.id_producto === item.id_producto)
                    );
                    return producto && producto.nombre.toLowerCase().includes(filtroProducto.toLowerCase());
                });
            }

            if (filtroProveedor) {
                inventario = inventario.filter(item => {
                    const producto = productos.find(p => 
                        (p.id && p.id === item.id_producto) || 
                        (p.id_producto && p.id_producto === item.id_producto)
                    );
                    return producto && producto.id_proveedor == filtroProveedor;
                });
            }
            
            if (filtroCategoria) {
                inventario = inventario.filter(item => {
                    const producto = productos.find(p => 
                        (p.id && p.id === item.id_producto) || 
                        (p.id_producto && p.id_producto === item.id_producto)
                    );
                    // Comprobar tanto id_categoria como categoria
                    return producto && 
                        ((producto.id_categoria && producto.id_categoria == filtroCategoria) ||
                         (producto.categoria && categorias.find(c => c.nombre === producto.categoria && c.id_categoria == filtroCategoria)));
                });
            }
            
            mostrarInventario(inventario);
            actualizarPaginacion(inventario.length);
    } catch (error) {
        console.error('Error al cargar inventario:', error);
    }
}

// Mostrar inventario en la tabla
function mostrarInventario(inventario) {
    tablaInventario.innerHTML = '';
    
    inventario.forEach(item => {
        // Buscar producto por id o id_producto para compatibilidad con ambos formatos
        const producto = productos.find(p => (p.id && p.id === item.id_producto) || 
                                           (p.id_producto && p.id_producto === item.id_producto));
        const nombreProducto = producto ? producto.nombre : 'Producto no encontrado';
        const codigoInterno = producto ? producto.codigo_interno : 'N/A';
        
        // Buscar proveedor
        const proveedor = proveedores.find(p => p.id_proveedor === (producto ? producto.id_proveedor : null));
        const nombreProveedor = proveedor ? proveedor.nombre : 'N/A';
        
        // Buscar categoría
        const categoria = categorias.find(c => c.id_categoria === (producto ? producto.id_categoria : null));
        const nombreCategoria = categoria ? categoria.nombre : 'N/A';
        
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${codigoInterno}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${nombreProducto}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${producto ? (producto.cantidad_disponible || 0).toLocaleString() : '0'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$${(item?.precio || 0).toLocaleString()}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${nombreProveedor}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${nombreCategoria}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button onclick="editarInventario(${item.id_inventario})" class="text-indigo-600 hover:text-indigo-900 mr-3">Editar</button>
                <button onclick="eliminarInventario(${item.id_inventario})" class="text-red-600 hover:text-red-900">Eliminar</button>
            </td>
        `;
        tablaInventario.appendChild(fila);
    });
}

// Actualizar información de paginación
function actualizarPaginacion(cantidadMostrada) {
    const desde = paginaActual * registrosPorPagina + 1;
    const hasta = Math.min(desde + cantidadMostrada - 1, totalRegistros);
    
    document.getElementById('mostrandoDesde').textContent = cantidadMostrada > 0 ? desde : 0;
    document.getElementById('mostrandoHasta').textContent = hasta;
    document.getElementById('totalRegistros').textContent = totalRegistros;
    
    // Actualizar estado de botones desktop
    btnAnterior.disabled = paginaActual === 0;
    btnSiguiente.disabled = hasta >= totalRegistros;
    
    // Actualizar estado de botones móviles
    if (btnAnteriorMobile) {
        btnAnteriorMobile.disabled = paginaActual === 0;
    }
    if (btnSiguienteMobile) {
        btnSiguienteMobile.disabled = hasta >= totalRegistros;
    }
}

// Función para redondear a la decena más cercana
function redondearADecena(valor) {
    // Truncar decimales
    const valorTruncado = Math.trunc(valor);
    // Obtener el último dígito
    const ultimoDigito = valorTruncado % 10;
    // Si el último dígito es 0, no hacer nada
    if (ultimoDigito === 0) {
        return valorTruncado;
    }
    // Redondear a la decena superior
    return valorTruncado + (10 - ultimoDigito);
}

// Función para calcular precio automáticamente
function calcularPrecio() {
    const brutoEl = document.getElementById('costoBruto');
    const netoEl = document.getElementById('costoNeto');
    const utilPctEl = document.getElementById('porcentajeUtilidad');
    const utilPesEl = document.getElementById('utilidadPesos');
    const precioEl = document.getElementById('precio');

    const brutoVal = parseFloat(brutoEl.value) || 0;
    const netoVal = parseFloat(netoEl.value) || 0;
    const utilPct = parseFloat(utilPctEl.value) || 0;
    const utilPes = parseFloat(utilPesEl.value) || 0;
    const precioVal = parseFloat(precioEl.value) || 0;

    const calcPrecioDesdeNeto = (neto) => {
        let p = neto;
        if (utilPct > 0) p = p * (1 + utilPct / 100);
        if (utilPes > 0) p = p + utilPes;
        return redondearADecena(p);
    };
    const calcNetoDesdePrecio = (precio) => {
        let base = precio;
        if (utilPes > 0) base = base - utilPes;
        if (utilPct > 0) base = base / (1 + utilPct / 100);
        if (base < 0) base = 0;
        return redondearADecena(base);
    };

    if (campoEnEdicion === 'costoNeto') {
        const bruto = redondearADecena(netoVal * 1.19);
        brutoEl.value = bruto;
        precioEl.value = calcPrecioDesdeNeto(netoVal);
        return;
    }
    if (campoEnEdicion === 'costoBruto') {
        const neto = redondearADecena(brutoVal / 1.19);
        netoEl.value = neto;
        precioEl.value = calcPrecioDesdeNeto(neto);
        return;
    }
    if (campoEnEdicion === 'precio') {
        const neto = calcNetoDesdePrecio(precioVal);
        netoEl.value = neto;
        brutoEl.value = redondearADecena(neto * 1.19);
        return;
    }
    if (campoEnEdicion === 'porcentajeUtilidad' || campoEnEdicion === 'utilidadPesos') {
        if (netoVal > 0) {
            precioEl.value = calcPrecioDesdeNeto(netoVal);
            brutoEl.value = redondearADecena(netoVal * 1.19);
            return;
        }
        if (precioVal > 0) {
            const neto = calcNetoDesdePrecio(precioVal);
            netoEl.value = neto;
            brutoEl.value = redondearADecena(neto * 1.19);
            return;
        }
    }
    if (netoVal > 0) {
        precioEl.value = calcPrecioDesdeNeto(netoVal);
        brutoEl.value = redondearADecena(netoVal * 1.19);
        return;
    }
    if (brutoVal > 0) {
        const neto = redondearADecena(brutoVal / 1.19);
        netoEl.value = neto;
        precioEl.value = calcPrecioDesdeNeto(neto);
        return;
    }
}

// Abrir modal para nuevo registro
function abrirModalNuevo() {
    inventarioEditando = null;
    tituloModal.textContent = 'Nuevo Registro de Inventario';
    formInventario.reset();
    
    // Establecer valores por defecto en cero para los nuevos campos
    document.getElementById('costoBruto').value = '0';
    document.getElementById('costoNeto').value = '0';
    document.getElementById('porcentajeUtilidad').value = '0';
    document.getElementById('utilidadPesos').value = '0';
    document.getElementById('stockMinimo').value = '0';
    
    // Establecer campos requeridos correctamente
    document.getElementById('nombreProducto').setAttribute('required', 'required');
    document.getElementById('categoriaProducto').setAttribute('required', 'required');
    document.getElementById('proveedorProducto').setAttribute('required', 'required');
    
    // Cargar categorías y proveedores
    cargarCategorias();
    cargarProveedores();
    // Resetear subcategorías
    const subcategoriaProducto = document.getElementById('subcategoriaProducto');
    if (subcategoriaProducto) {
        subcategoriaProducto.innerHTML = '<option value="">Seleccionar subcategoría</option>';
        subcategoriaProducto.disabled = true;
    }
    
    modalInventario.classList.remove('hidden');
}

// Editar inventario
async function editarInventario(id) {
    try {
        console.log('Editando inventario con ID:', id);
        const response = await fetchWithAuth(`/api/productos/inventario/${id}`);
        if (response.ok) {
            const inventario = await response.json();
            console.log('Inventario cargado para edición:', inventario);
            inventarioEditando = inventario;
            tituloModal.textContent = 'Editar Inventario';
            
            // Cargar categorías y proveedores primero
            await cargarCategorias();
            await cargarProveedores();
            
            // Usar los datos del producto que vienen en la respuesta del inventario
            const producto = inventario.producto;
            
            // Llenar el formulario con los datos del inventario
            document.getElementById('precio').value = producto ? (producto.precio_venta || '') : '';
            document.getElementById('cantidad').value = (inventario.cantidad ?? (producto ? producto.cantidad_disponible : '')) || '';
            
            if (producto) {
                // Llenar campos del producto
                document.getElementById('nombreProducto').value = producto.nombre || '';
                document.getElementById('codigoInterno').value = producto.codigo_interno || '';
                
                // Llenar campos de costos y precios
                document.getElementById('costoBruto').value = producto.costo_bruto || '0';
                document.getElementById('costoNeto').value = producto.costo_neto || '0';
                document.getElementById('porcentajeUtilidad').value = producto.porcentaje_utilidad || '0';
                document.getElementById('utilidadPesos').value = producto.utilidad_pesos || '0';
                document.getElementById('stockMinimo').value = producto.stock_minimo || '0';
                
                // Seleccionar categoría
                if (producto.id_categoria) {
                    document.getElementById('categoriaProducto').value = producto.id_categoria;
                    // Cargar y seleccionar subcategoría dependiente
                    await cargarSubcategorias(producto.id_categoria);
                }
                // Seleccionar subcategoría
                if (producto.id_subcategoria) {
                    const subEl = document.getElementById('subcategoriaProducto');
                    if (subEl) {
                        subEl.value = producto.id_subcategoria;
                    }
                }
                
                // Seleccionar proveedor
                if (producto.id_proveedor) {
                    document.getElementById('proveedorProducto').value = producto.id_proveedor;
                }
            }
            
            modalInventario.classList.remove('hidden');
        } else if (response.status === 401) {
            console.log('Error de autenticación al editar inventario. Redirigiendo a login...');
            alert('Sesión expirada. Por favor, inicie sesión nuevamente.');
            localStorage.removeItem('token');
            window.location.href = '/login';
            return;
        } else {
            const error = await response.json();
            console.error('Error al cargar inventario:', error);
            let errorMsg = 'Error al cargar inventario';
            if (error.detail) {
                errorMsg += ': ' + error.detail;
            }
            alert(errorMsg);
        }
    } catch (error) {
        console.error('Error al cargar inventario:', error);
        alert('Error de conexión con el servidor');
    }
}

// Eliminar inventario
function eliminarInventario(id) {
    console.log('Preparando eliminación de inventario con ID:', id);
    inventarioAEliminar = id;
    modalEliminar.classList.remove('hidden');
}

// Confirmar eliminación
async function confirmarEliminacion() {
    try {
        console.log('Confirmando eliminación de inventario ID:', inventarioAEliminar);
        
        // Usar utilitario con autenticación
        const responseData = await deleteData(`/api/productos/inventario/${inventarioAEliminar}`);
        
        if (responseData) {
            console.log('Inventario eliminado exitosamente');
            modalEliminar.classList.add('hidden');
            inventarioAEliminar = null;
            await cargarInventario();
            alert('Registro de inventario eliminado exitosamente');
        } else {
            // Si no hay respuesta válida, considerar error genérico
            throw new Error('Error desconocido al eliminar inventario');
        }
    } catch (error) {
        // Manejo específico de 401 si proviene del utilitario
        if (error && (error.message || '').includes('401')) {
            console.log('Error de autenticación al eliminar inventario. Redirigiendo a login...');
            alert('Sesión expirada. Por favor, inicie sesión nuevamente.');
            localStorage.removeItem('token');
            window.location.href = '/login';
            return;
        }
        console.error('Error al eliminar inventario:', error);
        let errorMessage = 'Error al eliminar registro';
        
        // Intentar extraer el mensaje de error detallado
        if (error.message) {
            errorMessage += ': ' + error.message;
        } else if (typeof error === 'object') {
            errorMessage += ': ' + JSON.stringify(error);
        }
        
        alert(errorMessage);
    }
}

// Guardar inventario
async function guardarInventario(event) {
    console.log('🔥 INICIO guardarInventario - event:', event);
    event.preventDefault();
    
    console.log('🔥 formInventario:', formInventario);
    const formData = new FormData(formInventario);
    
    console.log('🔥 FormData creado, contenido:');
    for (let [key, value] of formData.entries()) {
        console.log(`  ${key}: ${value}`);
    }
    
    // Validar campos requeridos
    const camposRequeridos = ['nombreProducto', 'categoriaProducto', 'precio', 'cantidad'];
    const camposFaltantes = [];
    
    for (const campo of camposRequeridos) {
        const valor = formData.get(campo);
        if (!valor || valor.trim() === '') {
            camposFaltantes.push(campo);
        }
    }
    
    if (camposFaltantes.length > 0) {
        console.log('🔥 ERROR: Campos faltantes:', camposFaltantes);
        alert(`Error: Los siguientes campos son requeridos: ${camposFaltantes.join(', ')}`);
        return;
    }
    
    console.log('🔥 Validación pasada, continuando...');
    
    try {
        // Si estamos editando un inventario existente
        if (inventarioEditando) {
            console.log('🔥 EDITANDO inventario existente:', inventarioEditando.id_inventario);
            
            // Crear objeto de actualización para el inventario
            const inventarioActualizado = {
                precio: parseFloat(formData.get('precio')),
                cantidad_disponible: parseInt(formData.get('cantidad'))
            };
            
            console.log('🔥 Datos de inventario a actualizar:', inventarioActualizado);
            
            console.log('🔥 Enviando actualización de inventario');
            const urlInv = `/api/productos/inventario/${inventarioEditando.id_inventario}?cantidad=${inventarioActualizado.cantidad_disponible}` +
                (isNaN(inventarioActualizado.precio) ? '' : `&precio=${inventarioActualizado.precio}`);
            const invResponse = await fetchWithAuth(urlInv, { method: 'PUT' });
            let inventarioResp = null;
            if (invResponse.ok) {
                inventarioResp = await invResponse.json();
            } else {
                const errText = await invResponse.text();
                throw new Error(`Error ${invResponse.status}: ${errText}`);
            }
            
            // También actualizar el producto si hay cambios
            const nombreProducto = formData.get('nombreProducto');
            const producto = inventarioEditando.producto;
            
            if (producto) {
                const productoActualizado = {
                    nombre: nombreProducto,
                    id_categoria: parseInt(formData.get('categoriaProducto')) || producto.id_categoria,
                    id_proveedor: parseInt(formData.get('proveedorProducto')) || null,
                    id_subcategoria: (function(){
                        const val = (formData.get('subcategoriaProducto') || '').trim();
                        if (val === '' || val.toLowerCase() === 'null') return null;
                        const num = parseInt(val, 10);
                        return isNaN(num) ? null : num;
                    })(),
                    codigo_interno: formData.get('codigoInterno') || producto.codigo_interno,
                    costo_bruto: parseFloat(formData.get('costoBruto')) || producto.costo_bruto || 0,
                    costo_neto: parseFloat(formData.get('costoNeto')) || producto.costo_neto || 0,
                    porcentaje_utilidad: parseFloat(formData.get('porcentajeUtilidad')) || producto.porcentaje_utilidad || 0,
                    utilidad_pesos: parseFloat(formData.get('utilidadPesos')) || producto.utilidad_pesos || 0,
                    stock_minimo: parseInt(formData.get('stockMinimo')) || producto.stock_minimo || 0
                };
                
                // Validar que id_categoria sea un número válido
                if (!productoActualizado.id_categoria || isNaN(productoActualizado.id_categoria)) {
                    productoActualizado.id_categoria = producto.id_categoria;
                }
                
                // Si id_proveedor es 0 o NaN, convertir a null
                if (!productoActualizado.id_proveedor || isNaN(productoActualizado.id_proveedor)) {
                    productoActualizado.id_proveedor = null;
                }
                // Validar id_subcategoria opcional
                if (productoActualizado.id_subcategoria !== null && isNaN(productoActualizado.id_subcategoria)) {
                    productoActualizado.id_subcategoria = null;
                }
                
                console.log('Datos de producto a actualizar:', productoActualizado);
                
                // Llamar al endpoint PUT para actualizar el producto
                const productoResponse = await updateData(`/api/productos/${producto.id_producto}`, productoActualizado);
                
                if (!productoResponse) {
                    console.error('Error al actualizar el producto');
                }
            }
            
            if (!inventarioResp || inventarioResp.error) {
                const error = inventarioResp?.error || inventarioResp;
                let errorMsg = 'Error al actualizar inventario';
                
                // Verificar si es un error de autenticación
                if (String(error).includes('401')) {
                    console.log('Error de autenticación al actualizar inventario. Redirigiendo a login...');
                    alert('Sesión expirada. Por favor, inicie sesión nuevamente.');
                    localStorage.removeItem('token');
                    window.location.href = '/login';
                    return;
                }
                
                if (error && error.detail) {
                    if (typeof error.detail === 'string') {
                        errorMsg += ': ' + error.detail;
                    } else if (Array.isArray(error.detail)) {
                        errorMsg += ': ' + error.detail.map(err => err.msg).join(', ');
                    } else {
                        errorMsg += ': ' + JSON.stringify(error.detail);
                    }
                } else {
                    errorMsg += ': ' + JSON.stringify(error || {});
                }
                
                console.error('Error de respuesta:', error);
                alert(errorMsg);
                return;
            }
            
            console.log('Inventario actualizado exitosamente:', inventarioResp);
            
            modalInventario.classList.add('hidden');
            inventarioEditando = null;
            
            await cargarProductos();
            await cargarCategorias();
            await cargarProveedores();
            await cargarInventario();
            
            // Mostrar mensaje de éxito
            alert('Inventario actualizado exitosamente.');
        } else {
            // Crear nuevo producto con inventario
            const nuevoProducto = {
                nombre: formData.get('nombreProducto'),
                id_categoria: parseInt(formData.get('categoriaProducto')) || null,
                id_proveedor: parseInt(formData.get('proveedorProducto')) || null,
                id_subcategoria: (function(){
                    const val = (formData.get('subcategoriaProducto') || '').trim();
                    if (val === '' || val.toLowerCase() === 'null') return null;
                    const num = parseInt(val, 10);
                    return isNaN(num) ? null : num;
                })(),
                codigo_interno: formData.get('codigoInterno') || null,
                costo_bruto: parseFloat(formData.get('costoBruto')) || 0,
                costo_neto: parseFloat(formData.get('costoNeto')) || 0,
                precio_venta: parseFloat(formData.get('precio')) || 0,
                porcentaje_utilidad: parseFloat(formData.get('porcentajeUtilidad')) || 0,
                utilidad_pesos: parseFloat(formData.get('utilidadPesos')) || 0,
                cantidad_disponible: parseInt(formData.get('cantidad')) || 0,
                stock_minimo: parseInt(formData.get('stockMinimo')) || 0
            };
            
            // Validar que id_categoria sea un número válido
            if (!nuevoProducto.id_categoria || isNaN(nuevoProducto.id_categoria)) {
                alert('Por favor selecciona una categoría válida');
                return;
            }
            
            // Si id_proveedor es 0 o NaN, convertir a null
            if (!nuevoProducto.id_proveedor || isNaN(nuevoProducto.id_proveedor)) {
                nuevoProducto.id_proveedor = null;
            }
            // Validar id_subcategoria opcional
            if (nuevoProducto.id_subcategoria !== null && isNaN(nuevoProducto.id_subcategoria)) {
                nuevoProducto.id_subcategoria = null;
            }
            
            console.log('Creando nuevo producto:', nuevoProducto);
            
            const productoResponse = await fetchWithAuth(`/api/productos/`, {
                method: 'POST',
                body: JSON.stringify(nuevoProducto)
            });
            
            if (!productoResponse.ok) {
                const error = await productoResponse.json();
                let errorMsg = 'Error al crear producto';
                
                if (productoResponse.status === 401) {
                    console.log('Error de autenticación al crear producto. Redirigiendo a login...');
                    alert('Sesión expirada. Por favor, inicie sesión nuevamente.');
                    localStorage.removeItem('token');
                    window.location.href = '/login';
                    return;
                }
                
                if (error.detail) {
                    if (typeof error.detail === 'string') {
                        errorMsg += ': ' + error.detail;
                    } else if (Array.isArray(error.detail)) {
                        errorMsg += ': ' + error.detail.map(err => err.msg).join(', ');
                    } else {
                        errorMsg += ': ' + JSON.stringify(error.detail);
                    }
                } else {
                    errorMsg += ': ' + JSON.stringify(error);
                }
                
                console.error('Error de respuesta al crear producto:', error);
                alert(errorMsg);
                return;
            }
            
            const productoCreado = await productoResponse.json();
            console.log('Producto creado exitosamente:', productoCreado);
            
            modalInventario.classList.add('hidden');
            
            await cargarProductos();
            await cargarCategorias();
            await cargarProveedores();
            await cargarInventario();
            
            // Mostrar mensaje de éxito
            alert('Producto creado exitosamente.');
        }
    } catch (error) {
        console.error('Error al guardar inventario:', error);
        let errorMessage = 'Error al guardar';
        
        if (error.message) {
            errorMessage += ': ' + error.message;
        } else if (typeof error === 'object') {
            errorMessage += ': ' + JSON.stringify(error);
        }
        
        alert(errorMessage);
    }
}

// Cargar categorías y proveedores al iniciar
function cargarDatosIniciales() {
    cargarCategorias();
    cargarProveedores();
}

// Hacer las funciones globales para que puedan ser llamadas desde el HTML
window.editarInventario = editarInventario;
window.eliminarInventario = eliminarInventario;

// Event listeners
btnNuevoInventario.addEventListener('click', abrirModalNuevo);
btnProveedores.addEventListener('click', () => {
    window.location.href = '/admin/proveedores';
});
btnCategorias.addEventListener('click', () => {
    window.location.href = '/admin/categorias';
});
if (btnSubcategorias) {
    btnSubcategorias.addEventListener('click', () => {
        window.location.href = '/admin/subcategorias';
    });
}
btnCancelar.addEventListener('click', () => modalInventario.classList.add('hidden'));
btnCancelarEliminar.addEventListener('click', () => modalEliminar.classList.add('hidden'));
btnConfirmarEliminar.addEventListener('click', confirmarEliminacion);

// Variable para el debounce
let debounceTimer = null;
let campoEnEdicion = null;

// Función con debounce para cálculo de precio
function calcularPrecioConDebounce(campoActual) {
    // Limpiar el timer anterior si existe
    if (debounceTimer) {
        clearTimeout(debounceTimer);
    }
    
    // Guardar qué campo se está editando
    campoEnEdicion = campoActual;
    
    // Establecer nuevo timer de 5ms
    debounceTimer = setTimeout(() => {
        calcularPrecio();
        campoEnEdicion = null;
    }, 5);
}

// Event listeners para cálculo automático de precio
document.addEventListener('DOMContentLoaded', function() {
    const costoBrutoInput = document.getElementById('costoBruto');
    const costoNetoInput = document.getElementById('costoNeto');
    const porcentajeUtilidadInput = document.getElementById('porcentajeUtilidad');
    const utilidadPesosInput = document.getElementById('utilidadPesos');
    const precioInput = document.getElementById('precio');
    
    if (costoBrutoInput) costoBrutoInput.addEventListener('input', () => calcularPrecioConDebounce('costoBruto'));
    if (costoNetoInput) costoNetoInput.addEventListener('input', () => calcularPrecioConDebounce('costoNeto'));
    if (porcentajeUtilidadInput) porcentajeUtilidadInput.addEventListener('input', () => calcularPrecioConDebounce('porcentajeUtilidad'));
    if (utilidadPesosInput) utilidadPesosInput.addEventListener('input', () => calcularPrecioConDebounce('utilidadPesos'));
    if (precioInput) precioInput.addEventListener('input', () => calcularPrecioConDebounce('precio'));
});

formInventario.addEventListener('submit', guardarInventario);
btnFiltrar.addEventListener('click', () => {
    paginaActual = 0;
    cargarInventario();
});
btnAnterior.addEventListener('click', () => {
    if (paginaActual > 0) {
        paginaActual--;
        cargarInventario();
    }
});
btnSiguiente.addEventListener('click', () => {
    paginaActual++;
    cargarInventario();
});

// Event listeners para botones móviles
if (btnAnteriorMobile) {
    btnAnteriorMobile.addEventListener('click', () => {
        if (paginaActual > 0) {
            paginaActual--;
            cargarInventario();
        }
    });
}
if (btnSiguienteMobile) {
    btnSiguienteMobile.addEventListener('click', () => {
        paginaActual++;
        cargarInventario();
    });
}

// Cerrar modales al hacer clic fuera
modalInventario.addEventListener('click', (e) => {
    if (e.target === modalInventario) {
        modalInventario.classList.add('hidden');
    }
});
modalEliminar.addEventListener('click', (e) => {
    if (e.target === modalEliminar) {
        modalEliminar.classList.add('hidden');
    }
});

// Inicializar página
document.addEventListener('DOMContentLoaded', async () => {
    if (!verificarAuth()) {
        console.log('Redirigiendo a login por falta de autenticación');
        return;
    }
    try {
        const q = new URLSearchParams(window.location.search).get('q');
        await cargarProductos();
        await cargarCategorias();
        await cargarProveedores();
        if (q) {
            const inp = document.getElementById('filtroProducto');
            if (inp) inp.value = q;
        }
        await cargarInventario();
    } catch (error) {
        console.error('Error al cargar datos del inventario:', error);
        alert('Error en conexión del servidor');
    }
});
