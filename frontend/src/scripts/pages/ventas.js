// Funciones para la gestión de ventas
import { API_URL, handleApiError } from '../utils/config.js';
import { getData } from '../utils/api.js';
import { mostrarErrorToast } from '../utils/ui.js';

// Estado global
const state = {
    ventas: [],
    ventaDetalleActual: null,
    filtros: {
        fechaInicio: null,
        fechaFin: null,
        estado: null
    },
    paginacion: {
        paginaActual: 1,
        elementosPorPagina: 10,
        totalElementos: 0
    },
    orden: {
        clave: null,
        direccion: 'asc'
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
    // Eliminado: acciones de creación manual de ventas
    
    // Filtros
    document.getElementById('btnFiltrar')?.addEventListener('click', aplicarFiltros);
    // document.getElementById('btnLimpiarFiltros')?.addEventListener('click', limpiarFiltros);
    
    // Búsqueda con debounce
    const inputBusqueda = document.getElementById('inputBusqueda');
    if (inputBusqueda) {
        const debouncedBuscar = debounce(() => buscarVentas(), 300);
        inputBusqueda.addEventListener('input', debouncedBuscar);
    }

    // Exportar CSV
    const btnExportar = document.getElementById('btnExportarVentas');
    btnExportar?.addEventListener('click', exportarVentasCSV);

    // Ordenamiento por cabeceras
    const thead = document.getElementById('ventasTableHead');
    if (thead) {
        thead.addEventListener('click', (e) => {
            const th = e.target.closest('th');
            const clave = th?.dataset?.sortKey;
            if (!clave) return;
            if (state.orden.clave === clave) {
                state.orden.direccion = state.orden.direccion === 'asc' ? 'desc' : 'asc';
            } else {
                state.orden.clave = clave;
                state.orden.direccion = 'asc';
            }
            renderizarTablaVentas();
        });
    }

    // Eliminado: agregar productos en modal de nueva venta
    
    // Paginación
    document.getElementById('btnPrevPage')?.addEventListener('click', paginaAnterior);
    document.getElementById('btnNextPage')?.addEventListener('click', paginaSiguiente);
    document.getElementById('btnPrevPageMobile')?.addEventListener('click', paginaAnterior);
    document.getElementById('btnNextPageMobile')?.addEventListener('click', paginaSiguiente);
    
    // Búsqueda (si existe caja de búsqueda)
    // const inputBusqueda = document.getElementById('inputBusqueda') || document.getElementById('buscarVenta');
    // inputBusqueda?.addEventListener('input', buscarVentas);
}

async function cargarDatosIniciales() {
    try {
        mostrarLoading(true);
        
        // Cargar datos en paralelo
        await Promise.all([
            cargarVentas(),
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
        if (state.filtros.estado) {
            params.append('estado', state.filtros.estado);
        }
        
        // Paginación
        params.append('skip', (state.paginacion.paginaActual - 1) * state.paginacion.elementosPorPagina);
        params.append('limit', state.paginacion.elementosPorPagina);
        
        const url = `/api/ventas?${params.toString()}`;
        const ventas = await getData(url);
        
        // Asegurar que ventas sea un array
        state.ventas = Array.isArray(ventas) ? ventas : [];
        // El backend devuelve una lista simple; usamos su longitud como total conocido
        state.paginacion.totalElementos = state.ventas.length;
        renderizarTablaVentas();
        actualizarPaginacion();
        
        console.log(`Cargadas ${state.ventas.length} ventas`);
    } catch (error) {
        console.error('Error al cargar ventas:', error);
        // En caso de error, asegurar que el estado sea un array vacío
        state.ventas = [];
        state.paginacion.totalElementos = 0;
        renderizarTablaVentas();
        mostrarError('Error al cargar las ventas');
    }
}

// Eliminado: cargarUsuarios y cargarProductos (no se requieren para ventas online)

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
    
    // Ordenar según estado.orden
    const ventasOrdenadas = [...state.ventas];
    if (state.orden.clave) {
        ventasOrdenadas.sort((a, b) => {
            const dir = state.orden.direccion === 'asc' ? 1 : -1;
            const va = a[state.orden.clave];
            const vb = b[state.orden.clave];
            if (state.orden.clave === 'fecha_venta') {
                const ta = new Date(va).getTime();
                const tb = new Date(vb).getTime();
                return (ta - tb) * dir;
            }
            if (typeof va === 'number' && typeof vb === 'number') {
                return (va - vb) * dir;
            }
            return String(va || '').localeCompare(String(vb || ''), 'es') * dir;
        });
    }

    // Renderizar ventas
    tbody.innerHTML = ventasOrdenadas.map(venta => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                #${venta.id_venta}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatearFecha(venta.fecha_venta)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${venta.usuario || 'N/A'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${formatearDinero(venta.total_venta)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${venta.detalles_venta ? venta.detalles_venta.length : 0} productos
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    venta.estado === 'completada'
                        ? 'bg-green-100 text-green-800'
                        : (venta.estado === 'cancelada'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800')
                }">
                    ${venta.estado}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                    <button class="inline-flex items-center px-3 py-1 rounded-md text-sm text-blue-700 bg-blue-100 hover:bg-blue-200" data-action="ver-detalle" data-id="${venta.id_venta}">
                        Ver detalle
                    </button>
                    <button class="inline-flex items-center px-3 py-1 rounded-md text-sm text-indigo-700 bg-indigo-100 hover:bg-indigo-200" data-action="entrega" data-id="${venta.id_venta}">
                        Recibir entrega
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Delegación de eventos para acciones de la tabla
document.getElementById('ventasTableBody')?.addEventListener('click', async (e) => {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const action = btn.getAttribute('data-action');
    const id = btn.getAttribute('data-id');
    if (!id) return;
    try {
        if (action === 'ver-detalle') {
            await cargarDetalleVenta(id);
            abrirModalDetalleVenta();
        } else if (action === 'entrega') {
            await cargarDetalleVenta(id);
            abrirModalDetalleVenta();
        }
    } catch (err) {
        console.error('Acción en ventas falló:', err);
        mostrarError('No se pudo procesar la acción de la venta');
    }
});

async function cargarDetalleVenta(idVenta) {
    try {
        mostrarLoading(true);
        const venta = await getData(`/api/ventas/${idVenta}`);
        // Asegurar formato de detalles
        venta.detalles_venta = Array.isArray(venta.detalles_venta) ? venta.detalles_venta : [];
        state.ventaDetalleActual = venta;
        renderDetalleVenta(venta);
    } catch (error) {
        console.error('Error al cargar detalle de venta:', error);
        mostrarError('No se pudo cargar el detalle de la venta');
        throw error;
    } finally {
        mostrarLoading(false);
    }
}

function renderDetalleVenta(venta) {
    const header = document.getElementById('detalleVentaHeader');
    const body = document.getElementById('detalleVentaBody');
    if (header) {
        header.innerHTML = `
            <div><span class="text-gray-500">Nº venta:</span> <span class="font-medium">${venta.id_venta}</span></div>
            <div><span class="text-gray-500">Fecha:</span> <span class="font-medium">${formatearFecha(venta.fecha_venta)}</span></div>
            <div><span class="text-gray-500">Usuario:</span> <span class="font-medium">${venta.usuario || 'N/A'}</span></div>
            <div><span class="text-gray-500">Total:</span> <span class="font-semibold">$${Number(venta.total_venta).toFixed(2)}</span></div>
        `;
    }
    if (body) {
        const filas = (venta.detalles_venta || []).map(d => `
            <tr>
                <td class="px-4 py-2 text-sm">${d.producto_nombre || `Producto #${d.id_producto}`}</td>
                <td class="px-4 py-2 text-sm">${d.cantidad}</td>
                <td class="px-4 py-2 text-sm">$${Number(d.precio_unitario).toFixed(2)}</td>
                <td class="px-4 py-2 text-sm font-medium">$${Number(d.subtotal || (d.precio_unitario * d.cantidad)).toFixed(2)}</td>
            </tr>
        `).join('');
        body.innerHTML = filas || '<tr><td colspan="4" class="px-4 py-3 text-center text-gray-500">Sin detalles</td></tr>';
    }
}

function abrirModalDetalleVenta() {
    const modal = document.getElementById('modalDetalleVenta');
    if (modal) modal.style.display = 'flex';
    // Preparar acciones de copiar e imprimir
    const btnCopiar = document.getElementById('btnCopiarEntrega');
    const btnImprimir = document.getElementById('btnImprimirEntrega');
    if (btnCopiar) {
        btnCopiar.onclick = copiarOrdenEntrega;
    }
    if (btnImprimir) {
        btnImprimir.onclick = imprimirOrdenEntrega;
    }
}

function cerrarModalDetalleVenta() {
    const modal = document.getElementById('modalDetalleVenta');
    if (modal) modal.style.display = 'none';
}

async function copiarOrdenEntrega() {
    try {
        const venta = state.ventaDetalleActual;
        if (!venta) return;
        const texto = generarTextoEntrega(venta);
        await navigator.clipboard.writeText(texto);
        mostrarExito('Datos de entrega copiados');
        try { sessionStorage.setItem('orden_entrega', JSON.stringify(venta)); } catch {}
    } catch (err) {
        console.error('No se pudo copiar orden de entrega:', err);
        mostrarError('No se pudo copiar los datos de entrega');
    }
}

function imprimirOrdenEntrega() {
    try {
        const venta = state.ventaDetalleActual;
        if (!venta) return;
        const popup = window.open('', '_blank');
        if (!popup) { mostrarError('Bloqueador de ventanas impide imprimir'); return; }
        const contenido = `
            <html><head><title>Guía de Entrega #${venta.id_venta}</title>
            <style>body{font-family:sans-serif;padding:20px} h1{font-size:18px} table{width:100%;border-collapse:collapse} th,td{border:1px solid #ddd;padding:6px;text-align:left} th{background:#f3f4f6}</style>
            </head><body>
            <h1>Guía de Entrega - Venta #${venta.id_venta}</h1>
            <p><strong>Fecha:</strong> ${formatearFecha(venta.fecha_venta)}<br/>
            <strong>Usuario:</strong> ${venta.usuario || 'N/A'}<br/>
            <strong>Total:</strong> $${Number(venta.total_venta).toFixed(2)}</p>
            <table><thead><tr><th>Producto</th><th>Cantidad</th><th>Precio</th><th>Subtotal</th></tr></thead><tbody>
            ${(venta.detalles_venta || []).map(d => `<tr><td>${d.producto_nombre || `Producto #${d.id_producto}`}</td><td>${d.cantidad}</td><td>$${Number(d.precio_unitario).toFixed(2)}</td><td>$${Number(d.subtotal || (d.precio_unitario * d.cantidad)).toFixed(2)}</td></tr>`).join('')}
            </tbody></table>
            </body></html>`;
        popup.document.write(contenido);
        popup.document.close();
        popup.focus();
        popup.print();
    } catch (err) {
        console.error('No se pudo imprimir guía de entrega:', err);
        mostrarError('No se pudo imprimir la guía de entrega');
    }
}

function generarTextoEntrega(venta) {
    const lineas = [];
    lineas.push(`Orden de Entrega - Venta #${venta.id_venta}`);
    lineas.push(`Fecha: ${formatearFecha(venta.fecha_venta)}`);
    lineas.push(`Usuario: ${venta.usuario || 'N/A'}`);
    lineas.push(`Total: $${Number(venta.total_venta).toFixed(2)}`);
    lineas.push('Detalles:');
    (venta.detalles_venta || []).forEach(d => {
        lineas.push(`- ${d.producto_nombre || `Producto #${d.id_producto}`} x${d.cantidad} ($${Number(d.precio_unitario).toFixed(2)} c/u)`);
    });
    return lineas.join('\n');
}

// Exponer función de cierre del modal de detalle para el botón del HTML
window.cerrarModalDetalleVenta = cerrarModalDetalleVenta;

function aplicarFiltros() {
    state.filtros.fechaInicio = document.getElementById('filtroFechaInicio').value || null;
    state.filtros.fechaFin = document.getElementById('filtroFechaFin').value || null;
    state.filtros.estado = document.getElementById('filtroEstado')?.value || null;
    
    state.paginacion.paginaActual = 1; // Resetear paginación
    cargarVentas();
    cargarEstadisticas();
}

function limpiarFiltros() {
    document.getElementById('filtroFechaInicio').value = '';
    document.getElementById('filtroFechaFin').value = '';
    document.getElementById('filtroEstado') && (document.getElementById('filtroEstado').value = '');
    
    state.filtros = {
        fechaInicio: null,
        fechaFin: null,
        estado: null
    };
    
    state.paginacion.paginaActual = 1;
    cargarVentas();
    cargarEstadisticas();
}

function buscarVentas() {
    const input = document.getElementById('buscarVenta') || document.getElementById('inputBusqueda');
    const termino = (input?.value || '').toLowerCase();
    
    if (!termino) {
        renderizarTablaVentas();
        return;
    }
    
    const ventasFiltradas = state.ventas.filter(venta => 
        (venta.id_venta?.toString() || '').includes(termino) ||
        ((venta.usuario || '').toLowerCase()).includes(termino) ||
        String(venta.total_venta).includes(termino)
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
            <td>${venta.usuario || 'N/A'}</td>
            <td>$${Number(venta.total_venta).toFixed(2)}</td>
            <td>${venta.detalles_venta ? venta.detalles_venta.length : 0} productos</td>
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
    // Delegar al toast común
    mostrarErrorToast(mensaje);
}

function mostrarExito(mensaje) {
    // Implementar sistema de notificaciones más sofisticado más tarde
    alert('Éxito: ' + mensaje);
}

// Exponer funciones globales necesarias
window.exportarVentasCSV = exportarVentasCSV;

// Formateo consistente de dinero
function formatearDinero(valor) {
    try {
        const num = Number(valor || 0);
        return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(num);
    } catch {
        return `$${Number(valor || 0).toFixed(2)}`;
    }
}

// Utilidad: debounce
function debounce(fn, delay) {
    let t;
    return (...args) => {
        clearTimeout(t);
        t = setTimeout(() => fn.apply(this, args), delay);
    };
}

// Exportación CSV
function exportarVentasCSV() {
    try {
        const filas = state.ventas.map(v => ({
            ID: v.id_venta,
            Fecha: v.fecha_venta,
            Usuario: v.usuario || '',
            Total: v.total_venta,
            Estado: v.estado || '',
            Productos: Array.isArray(v.detalles_venta) ? v.detalles_venta.length : 0
        }));
        const encabezados = Object.keys(filas[0] || { ID: '', Fecha: '', Usuario: '', Total: '', Estado: '', Productos: '' });
        const csv = [encabezados.join(','), ...filas.map(row => encabezados.map(h => JSON.stringify(row[h] ?? '')).join(','))].join('\n');
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ventas_${new Date().toISOString().slice(0,10)}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (e) {
        console.error('Error al exportar CSV:', e);
        mostrarError('No se pudo exportar el CSV');
    }
}