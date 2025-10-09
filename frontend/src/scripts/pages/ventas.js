// Funciones para la gestión de ventas
import { API_URL, handleApiError } from '../utils/config.js';
import { getData, postData, updateData } from '../utils/api.js';

// Estado global
const state = {
    ventas: [],
    usuarios: [],
    productos: [],
    productosVenta: [],
    ventaAEditar: null,
    filtros: {
        fechaInicio: null,
        fechaFin: null,
        idUsuario: null
    },
    paginacion: {
        paginaActual: 1,
        elementosPorPagina: 10,
        totalElementos: 0
    }
};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== Inicializando módulo de ventas ===');
    inicializarEventos();
    cargarDatosIniciales();
});

function inicializarEventos() {
    // Botones principales
    document.getElementById('btnNuevaVenta')?.addEventListener('click', abrirModalNuevaVenta);
    document.getElementById('btnGuardarVenta')?.addEventListener('click', guardarVenta);
    document.getElementById('btnCancelarVenta')?.addEventListener('click', cerrarModalVenta);
    
    // Filtros
    document.getElementById('btnAplicarFiltros')?.addEventListener('click', aplicarFiltros);
    document.getElementById('btnLimpiarFiltros')?.addEventListener('click', limpiarFiltros);
    
    // Productos en venta
    document.getElementById('btnAgregarProducto')?.addEventListener('click', agregarProductoAVenta);
    
    // Paginación
    document.getElementById('btnPaginaAnterior')?.addEventListener('click', paginaAnterior);
    document.getElementById('btnPaginaSiguiente')?.addEventListener('click', paginaSiguiente);
    
    // Búsqueda
    document.getElementById('inputBusqueda')?.addEventListener('input', buscarVentas);
}

async function cargarDatosIniciales() {
    try {
        mostrarLoading(true);
        
        // Cargar datos en paralelo
        await Promise.all([
            cargarVentas(),
            cargarUsuarios(),
            cargarProductos(),
            cargarEstadisticas()
        ]);
        
        console.log('Datos iniciales cargados correctamente');
    } catch (error) {
        console.error('Error al cargar datos iniciales:', error);
        mostrarError('Error al cargar los datos iniciales');
    } finally {
        mostrarLoading(false);
    }
}

async function cargarVentas() {
    try {
        const params = new URLSearchParams();
        
        // Aplicar filtros
        if (state.filtros.fechaInicio) {
            params.append('fecha_inicio', state.filtros.fechaInicio);
        }
        if (state.filtros.fechaFin) {
            params.append('fecha_fin', state.filtros.fechaFin);
        }
        if (state.filtros.idUsuario) {
            params.append('id_usuario', state.filtros.idUsuario);
        }
        
        // Paginación
        params.append('skip', (state.paginacion.paginaActual - 1) * state.paginacion.elementosPorPagina);
        params.append('limit', state.paginacion.elementosPorPagina);
        
        const url = `/api/ventas?${params.toString()}`;
        const ventas = await getData(url);
        
        // Asegurar que ventas sea un array
        state.ventas = Array.isArray(ventas) ? ventas : [];
        renderizarTablaVentas();
        actualizarPaginacion();
        
        console.log(`Cargadas ${state.ventas.length} ventas`);
    } catch (error) {
        console.error('Error al cargar ventas:', error);
        // En caso de error, asegurar que el estado sea un array vacío
        state.ventas = [];
        renderizarTablaVentas();
        mostrarError('Error al cargar las ventas');
    }
}

async function cargarUsuarios() {
    try {
        const usuarios = await getData('/api/usuarios');
        state.usuarios = usuarios;
        
        // Llenar select de usuarios en filtros
        const selectFiltroUsuario = document.getElementById('filtroUsuario');
        if (selectFiltroUsuario) {
            selectFiltroUsuario.innerHTML = '<option value="">Todos los usuarios</option>';
            usuarios.forEach(usuario => {
                const option = document.createElement('option');
                option.value = usuario.id_usuario;
                option.textContent = usuario.nombre;
                selectFiltroUsuario.appendChild(option);
            });
        }
        
        // Llenar select de usuarios en modal
        const selectVentaUsuario = document.getElementById('ventaUsuario');
        if (selectVentaUsuario) {
            selectVentaUsuario.innerHTML = '<option value="">Seleccionar usuario...</option>';
            usuarios.forEach(usuario => {
                const option = document.createElement('option');
                option.value = usuario.id_usuario;
                option.textContent = usuario.nombre;
                selectVentaUsuario.appendChild(option);
            });
        }
        
        console.log(`Cargados ${usuarios.length} usuarios`);
    } catch (error) {
        console.error('Error al cargar usuarios:', error);
        mostrarError('Error al cargar los usuarios');
    }
}

async function cargarProductos() {
    try {
        const productos = await getData('/api/productos');
        state.productos = productos.filter(p => p.cantidad_disponible > 0); // Solo productos con stock
        
        // Llenar select de productos
        const selectProducto = document.getElementById('selectProducto');
        if (selectProducto) {
            selectProducto.innerHTML = '<option value="">Seleccionar producto...</option>';
            state.productos.forEach(producto => {
                const option = document.createElement('option');
                option.value = producto.id_producto;
                option.textContent = `${producto.nombre} (Stock: ${producto.cantidad_disponible})`;
                option.dataset.precio = producto.precio_venta;
                option.dataset.stock = producto.cantidad_disponible;
                selectProducto.appendChild(option);
            });
        }
        
        console.log(`Cargados ${state.productos.length} productos con stock`);
    } catch (error) {
        console.error('Error al cargar productos:', error);
        mostrarError('Error al cargar los productos');
    }
}

async function cargarEstadisticas() {
    try {
        // Como las estadísticas están comentadas en el HTML, no necesitamos cargarlas
        console.log('Estadísticas deshabilitadas');
        return;
        
        // Código comentado para futuro uso
        /*
        const params = new URLSearchParams();
        
        // Aplicar filtros de fecha si existen
        if (state.filtros.fechaInicio) {
            params.append('fecha_inicio', state.filtros.fechaInicio);
        }
        if (state.filtros.fechaFin) {
            params.append('fecha_fin', state.filtros.fechaFin);
        }
        if (state.filtros.idUsuario) {
            params.append('id_usuario', state.filtros.idUsuario);
        }
        
        const url = `/api/ventas/estadisticas/resumen?${params.toString()}`;
        const estadisticas = await getData(url);
        
        // Actualizar elementos de estadísticas
        document.getElementById('totalVentas').textContent = `$${estadisticas.total_ventas.toFixed(2)}`;
        document.getElementById('cantidadVentas').textContent = estadisticas.cantidad_ventas;
        document.getElementById('productosVendidos').textContent = estadisticas.productos_vendidos;
        document.getElementById('promedioVenta').textContent = `$${estadisticas.promedio_venta.toFixed(2)}`;
        */
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
        // No mostrar error ya que las estadísticas están deshabilitadas
    }
}

function renderizarTablaVentas() {
    const tbody = document.getElementById('ventasTableBody');
    
    if (!tbody) {
        console.error('No se encontró el elemento ventasTableBody');
        return;
    }
    
    // Verificar si hay ventas
    if (!state.ventas || state.ventas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-8 text-center text-gray-500">
                    <div class="flex flex-col items-center">
                        <svg class="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        <p class="text-lg font-medium text-gray-900 mb-2">No hay ventas registradas</p>
                        <p class="text-sm text-gray-500">Comienza creando tu primera venta</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    // Renderizar ventas
    tbody.innerHTML = state.ventas.map(venta => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                #${venta.id}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatearFecha(venta.fecha_venta)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${venta.usuario ? venta.usuario.nombre : 'N/A'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                $${venta.total.toFixed(2)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${venta.detalles ? venta.detalles.length : 0} productos
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    venta.estado === 'completada' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                }">
                    ${venta.estado}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <!-- Botones de acción eliminados -->
            </td>
        </tr>
    `).join('');
}

function abrirModalNuevaVenta() {
    // Limpiar formulario
    document.getElementById('formNuevaVenta').reset();
    state.productosVenta = [];
    actualizarTablaProductosVenta();
    actualizarTotalVenta();
    
    // Establecer fecha actual
    const ahora = new Date();
    const fechaLocal = new Date(ahora.getTime() - ahora.getTimezoneOffset() * 60000);
    document.getElementById('ventaFecha').value = fechaLocal.toISOString().slice(0, 16);
    
    // Mostrar modal
    document.getElementById('modalNuevaVenta').style.display = 'flex';
}

function cerrarModalVenta() {
    document.getElementById('modalNuevaVenta').style.display = 'none';
    state.productosVenta = [];
}

function agregarProductoAVenta() {
    const selectProducto = document.getElementById('selectProducto');
    const cantidadInput = document.getElementById('cantidadProducto');
    
    if (!selectProducto.value) {
        mostrarError('Seleccione un producto');
        return;
    }
    
    const cantidad = parseInt(cantidadInput.value);
    if (!cantidad || cantidad <= 0) {
        mostrarError('Ingrese una cantidad válida');
        return;
    }
    
    const option = selectProducto.options[selectProducto.selectedIndex];
    const stockDisponible = parseInt(option.dataset.stock);
    const precioUnitario = parseFloat(option.dataset.precio);
    
    if (cantidad > stockDisponible) {
        mostrarError(`Stock insuficiente. Disponible: ${stockDisponible}`);
        return;
    }
    
    // Verificar si el producto ya está agregado
    const productoExistente = state.productosVenta.find(p => p.id_producto == selectProducto.value);
    if (productoExistente) {
        mostrarError('Este producto ya está agregado a la venta');
        return;
    }
    
    const producto = {
        id_producto: parseInt(selectProducto.value),
        nombre: option.textContent.split(' (Stock:')[0],
        cantidad: cantidad,
        precio_unitario: precioUnitario,
        subtotal: cantidad * precioUnitario
    };
    
    state.productosVenta.push(producto);
    actualizarTablaProductosVenta();
    actualizarTotalVenta();
    
    // Limpiar campos
    selectProducto.value = '';
    cantidadInput.value = '1';
}

function actualizarTablaProductosVenta() {
    const tbody = document.getElementById('productosVentaBody');
    if (!tbody) return;
    
    if (state.productosVenta.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">No hay productos agregados</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = state.productosVenta.map((producto, index) => `
        <tr>
            <td>${producto.nombre}</td>
            <td>${producto.cantidad}</td>
            <td>$${producto.precio_unitario.toFixed(2)}</td>
            <td>$${producto.subtotal.toFixed(2)}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="eliminarProductoVenta(${index})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function eliminarProductoVenta(index) {
    state.productosVenta.splice(index, 1);
    actualizarTablaProductosVenta();
    actualizarTotalVenta();
}

function actualizarTotalVenta() {
    const total = state.productosVenta.reduce((sum, producto) => sum + producto.subtotal, 0);
    document.getElementById('totalVenta').textContent = total.toFixed(2);
}

async function guardarVenta() {
    try {
        const form = document.getElementById('formNuevaVenta');
        const formData = new FormData(form);
        
        if (state.productosVenta.length === 0) {
            mostrarError('Agregue al menos un producto a la venta');
            return;
        }
        
        const ventaData = {
            id_usuario: parseInt(formData.get('id_usuario')),
            fecha_venta: formData.get('fecha_venta'),
            detalles: state.productosVenta.map(producto => ({
                id_producto: producto.id_producto,
                cantidad: producto.cantidad,
                precio_unitario: producto.precio_unitario
            }))
        };
        
        mostrarLoading(true);
        
        const resultado = await postData('/api/ventas', ventaData);
        
        mostrarExito('Venta creada exitosamente');
        cerrarModalVenta();
        await cargarVentas();
        await cargarEstadisticas();
        await cargarProductos(); // Recargar para actualizar stock
        
    } catch (error) {
        console.error('Error al guardar venta:', error);
        mostrarError('Error al guardar la venta: ' + error.message);
    } finally {
        mostrarLoading(false);
    }
}







function aplicarFiltros() {
    state.filtros.fechaInicio = document.getElementById('filtroFechaInicio').value || null;
    state.filtros.fechaFin = document.getElementById('filtroFechaFin').value || null;
    state.filtros.idUsuario = document.getElementById('filtroUsuario').value || null;
    
    state.paginacion.paginaActual = 1; // Resetear paginación
    cargarVentas();
    cargarEstadisticas();
}

function limpiarFiltros() {
    document.getElementById('filtroFechaInicio').value = '';
    document.getElementById('filtroFechaFin').value = '';
    document.getElementById('filtroUsuario').value = '';
    
    state.filtros = {
        fechaInicio: null,
        fechaFin: null,
        idUsuario: null
    };
    
    state.paginacion.paginaActual = 1;
    cargarVentas();
    cargarEstadisticas();
}

function buscarVentas() {
    const termino = document.getElementById('buscarVenta').value.toLowerCase();
    
    if (!termino) {
        renderizarTablaVentas();
        return;
    }
    
    const ventasFiltradas = state.ventas.filter(venta => 
        venta.id_venta.toString().includes(termino) ||
        venta.usuario.toLowerCase().includes(termino) ||
        venta.total.toString().includes(termino)
    );
    
    const tbody = document.getElementById('ventasTableBody');
    if (ventasFiltradas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center">
                    <i class="fas fa-search"></i>
                    No se encontraron ventas que coincidan con "${termino}"
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = ventasFiltradas.map(venta => `
        <tr>
            <td>#${venta.id_venta}</td>
            <td>${formatearFecha(venta.fecha_venta)}</td>
            <td>${venta.usuario}</td>
            <td>$${venta.total.toFixed(2)}</td>
            <td>${venta.detalles.length} productos</td>
            <td>
                <span class="estado-${venta.estado.toLowerCase()}">
                    ${venta.estado}
                </span>
            </td>
            <td>
                <!-- Botones de acción eliminados -->
            </td>
        </tr>
    `).join('');
}

function mostrarEstadisticas() {
    // Por ahora solo mostrar un alert, se puede expandir más tarde
    alert('Funcionalidad de estadísticas detalladas en desarrollo');
}

// Funciones de paginación
function paginaAnterior() {
    if (state.paginacion.paginaActual > 1) {
        state.paginacion.paginaActual--;
        cargarVentas();
    }
}

function paginaSiguiente() {
    const totalPaginas = Math.ceil(state.paginacion.totalElementos / state.paginacion.elementosPorPagina);
    if (state.paginacion.paginaActual < totalPaginas) {
        state.paginacion.paginaActual++;
        cargarVentas();
    }
}

function actualizarPaginacion() {
    const mostrandoDesde = document.getElementById('mostrandoDesde');
    const mostrandoHasta = document.getElementById('mostrandoHasta');
    const totalRegistros = document.getElementById('totalRegistros');
    
    if (mostrandoDesde) {
        const desde = (state.paginacion.paginaActual - 1) * state.paginacion.elementosPorPagina + 1;
        const hasta = Math.min(state.paginacion.paginaActual * state.paginacion.elementosPorPagina, state.paginacion.totalElementos);
        
        mostrandoDesde.textContent = state.ventas.length > 0 ? desde : 0;
        mostrandoHasta.textContent = state.ventas.length > 0 ? hasta : 0;
    }
    
    if (totalRegistros) {
        totalRegistros.textContent = state.paginacion.totalElementos;
    }
    
    // Actualizar botones de paginación
    const btnPrevPage = document.getElementById('btnPrevPage');
    const btnNextPage = document.getElementById('btnNextPage');
    const btnPrevPageMobile = document.getElementById('btnPrevPageMobile');
    const btnNextPageMobile = document.getElementById('btnNextPageMobile');
    
    const hasPrevPage = state.paginacion.paginaActual > 1;
    const hasNextPage = state.paginacion.paginaActual * state.paginacion.elementosPorPagina < state.paginacion.totalElementos;
    
    if (btnPrevPage) {
        btnPrevPage.disabled = !hasPrevPage;
        btnPrevPage.className = `relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 text-sm font-medium ${
            hasPrevPage ? 'bg-white text-gray-500 hover:bg-gray-50' : 'bg-gray-100 text-gray-300 cursor-not-allowed'
        }`;
    }
    
    if (btnNextPage) {
        btnNextPage.disabled = !hasNextPage;
        btnNextPage.className = `relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 text-sm font-medium ${
            hasNextPage ? 'bg-white text-gray-500 hover:bg-gray-50' : 'bg-gray-100 text-gray-300 cursor-not-allowed'
        }`;
    }
    
    if (btnPrevPageMobile) {
        btnPrevPageMobile.disabled = !hasPrevPage;
        btnPrevPageMobile.className = `relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
            hasPrevPage ? 'text-gray-700 bg-white hover:bg-gray-50' : 'text-gray-300 bg-gray-100 cursor-not-allowed'
        }`;
    }
    
    if (btnNextPageMobile) {
        btnNextPageMobile.disabled = !hasNextPage;
        btnNextPageMobile.className = `ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
            hasNextPage ? 'text-gray-700 bg-white hover:bg-gray-50' : 'text-gray-300 bg-gray-100 cursor-not-allowed'
        }`;
    }
    
    // Actualizar número de página
    const pageNumbers = document.getElementById('pageNumbers');
    if (pageNumbers) {
        pageNumbers.textContent = state.paginacion.paginaActual;
    }
}

// Funciones de utilidad
function formatearFecha(fecha) {
    return new Date(fecha).toLocaleString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function mostrarLoading(mostrar) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = mostrar ? 'flex' : 'none';
    }
}

function mostrarError(mensaje) {
    // Crear un toast de error más elegante
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300 translate-x-full';
    toast.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>${mensaje}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animar entrada
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Remover después de 5 segundos
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 5000);
}

function mostrarExito(mensaje) {
    // Implementar sistema de notificaciones más sofisticado más tarde
    alert('Éxito: ' + mensaje);
}

// Exponer funciones globales necesarias
window.eliminarProductoVenta = eliminarProductoVenta;
window.cerrarModalVenta = cerrarModalVenta;