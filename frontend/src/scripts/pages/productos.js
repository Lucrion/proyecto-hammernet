// Funciones para la página de productos
import { API_URL, checkServerAvailability, handleApiError } from '../utils/config.js';
import { getData } from '../utils/api.js';

// Función para formatear precios con puntos como separador de miles (formato chileno)
function formatearPrecio(precio) {
    return precio.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

// Estado global para almacenar productos y filtros
const state = {
    productos: [],
    todosProductos: [],
    totalProductos: 0,
    filtros: {
        busqueda: '',
        precioMin: 0,
        precioMax: 100000,
        categorias: [],
        enStock: false
    },
    paginacion: {
        paginaActual: 1,
        productosPorPagina: 10,
        totalPaginas: 1
    }
};

// Elementos del DOM
let contenedorProductos;
let inputBusqueda;
let rangoPrecio;
let checkboxesCategorias;
let radioStock;

// Inicializar la aplicación cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', () => {
    // Obtener referencias a elementos del DOM
    contenedorProductos = document.getElementById('productos-grid');
    inputBusqueda = document.getElementById('busqueda');
    rangoPrecio = document.getElementById('precio-rango');
    checkboxesCategorias = document.querySelectorAll('input[name="categoria"]');
    radioStock = document.querySelectorAll('input[name="stock"]');
    
    // Configurar eventos
    configurarEventos();
    
    // Cargar productos iniciales
    cargarProductos();
});

// Configurar event listeners
function configurarEventos() {
    // Búsqueda en tiempo real
    if (inputBusqueda) {
        inputBusqueda.addEventListener('input', (e) => {
            state.filtros.busqueda = e.target.value.toLowerCase();
            state.paginacion.paginaActual = 1;
            aplicarFiltros();
        });
    }
    
    // Filtro de precio
    if (rangoPrecio) {
        rangoPrecio.addEventListener('input', (e) => {
            state.filtros.precioMax = parseInt(e.target.value);
            document.getElementById('precio-valor').textContent = formatearPrecio(e.target.value);
            state.paginacion.paginaActual = 1;
            aplicarFiltros();
        });
    }
    
    // Filtros de categoría
    checkboxesCategorias.forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const categoria = e.target.value;
            if (e.target.checked) {
                state.filtros.categorias.push(categoria);
            } else {
                state.filtros.categorias = state.filtros.categorias.filter(c => c !== categoria);
            }
            state.paginacion.paginaActual = 1;
            aplicarFiltros();
        });
    });
    
    // Filtro de stock
    radioStock.forEach(radio => {
        radio.addEventListener('change', (e) => {
            state.filtros.enStock = e.target.value === 'true';
            state.paginacion.paginaActual = 1;
            aplicarFiltros();
        });
    });
}

// Cargar productos desde la API
export async function cargarProductos() {
    try {
        mostrarCargando();
        
        // Verificar disponibilidad del servidor (no bloquear si falla)
        try {
            await checkServerAvailability();
        } catch (error) {
            console.warn('Advertencia: No se pudo verificar la disponibilidad del servidor:', error);
        }

        // Obtener todos los productos del catálogo
        const productos = await getData('/api/productos/catalogo');
        state.todosProductos = Array.isArray(productos) ? productos : [];
        
        if (!Array.isArray(productos)) {
            throw new Error('La respuesta no es un array válido');
        }

        // Aplicar filtros y paginación local sobre todosProductos
        state.paginacion.paginaActual = 1;
        aplicarFiltros();
        
    } catch (error) {
        console.error('Error al cargar productos:', error);
        // Evitar errores adicionales en el manejo de errores
        // handleApiError(error);
        mostrarError('Error al cargar el catalogo.');
    }
}

// Aplicar filtros a los productos
export function aplicarFiltros() {
    let productosFiltrados = Array.isArray(state.todosProductos) ? [...state.todosProductos] : [];
    
    // Filtro de búsqueda
    if (state.filtros.busqueda) {
        productosFiltrados = productosFiltrados.filter(producto =>
            producto.nombre.toLowerCase().includes(state.filtros.busqueda) ||
            (producto.descripcion && producto.descripcion.toLowerCase().includes(state.filtros.busqueda))
        );
    }
    
    // Filtro de precio
    productosFiltrados = productosFiltrados.filter(producto => {
        const precio = Number(producto.precio_venta ?? producto.precio ?? 0);
        return precio >= state.filtros.precioMin && precio <= state.filtros.precioMax;
    });
    
    // Filtro de categorías
    if (state.filtros.categorias.length > 0) {
        productosFiltrados = productosFiltrados.filter(producto =>
            state.filtros.categorias.includes(producto.categoria)
        );
    }
    
    // Filtro de stock
    if (state.filtros.enStock) {
        productosFiltrados = productosFiltrados.filter(producto => (producto.disponible === true) || ((producto.cantidad_disponible ?? 0) > 0));
    }
    
    // Calcular paginación
    state.totalProductos = productosFiltrados.length;
    state.paginacion.totalPaginas = Math.ceil(state.totalProductos / state.paginacion.productosPorPagina);
    
    // Obtener productos de la página actual
    const inicio = (state.paginacion.paginaActual - 1) * state.paginacion.productosPorPagina;
    const fin = inicio + state.paginacion.productosPorPagina;
    const productosPagina = productosFiltrados.slice(inicio, fin);
    
    // Mostrar productos y actualizar paginación
    mostrarProductos(productosPagina);
    actualizarInfoPaginacion();
    actualizarPaginacion();
}

// Mostrar productos en el grid
function mostrarProductos(productos) {
    if (!contenedorProductos) return;
    
    if (productos.length === 0) {
        contenedorProductos.innerHTML = `
            <div class="col-span-full text-center py-12">
                <div class="text-gray-400 mb-4">
                    <svg class="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2 2v-5m16 0h-2M4 13h2m13-8l-4 4m0 0l-4-4m4 4V3" />
                    </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">No se encontraron productos</h3>
                <p class="text-gray-500">Intenta ajustar los filtros de búsqueda</p>
            </div>
        `;
        return;
    }
    
    contenedorProductos.innerHTML = productos.map(producto => `
        <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 cursor-pointer" onclick="verProducto(${producto.id_producto})">
            <div class="aspect-w-1 aspect-h-1">
                <img src="${producto.imagen_url || '/images/placeholder-product.jpg'}" 
                     alt="${producto.nombre}" 
                     class="w-full h-48 object-cover">
            </div>
            <div class="p-4">
                <h3 class="text-lg font-semibold text-gray-800 mb-2 text-center">${producto.nombre}</h3>
                <p class="text-gray-600 text-sm mb-3 line-clamp-2 text-center">${producto.descripcion || 'Sin descripción'}</p>
                <div class="flex justify-center items-center my-3">
                    <span class="px-4 py-2 bg-black text-white rounded text-xl font-bold">$${formatearPrecio(producto.precio_venta)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

// Actualizar información de paginación
function actualizarInfoPaginacion() {
    const infoPaginacionContainer = document.getElementById('info-paginacion');
    if (!infoPaginacionContainer) return;
    
    if (state.totalProductos === 0) {
        infoPaginacionContainer.innerHTML = '<p class="text-gray-500">No se encontraron productos</p>';
        return;
    }
    
    const inicio = (state.paginacion.paginaActual - 1) * state.paginacion.productosPorPagina + 1;
    const fin = Math.min(state.paginacion.paginaActual * state.paginacion.productosPorPagina, state.totalProductos);
    
    infoPaginacionContainer.innerHTML = `
        <p>Mostrando ${inicio} a ${fin} de ${state.totalProductos} resultados</p>
    `;
}

// Actualizar controles de paginación
function actualizarPaginacion() {
    const paginacionContainer = document.getElementById('paginacion');
    if (!paginacionContainer) return;
    
    if (state.paginacion.totalPaginas <= 1) {
        paginacionContainer.innerHTML = '';
        return;
    }
    
    let paginacionHTML = '';
    
    // Botón anterior
    if (state.paginacion.paginaActual > 1) {
        paginacionHTML += `
            <button onclick="cambiarPagina(${state.paginacion.paginaActual - 1})" 
                    class="px-4 py-2 text-gray-500 hover:text-gray-700 transition-colors duration-200">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
            </button>
        `;
    }
    
    // Contenedor de números de página
    paginacionHTML += '<div class="flex gap-2">';
    
    // Números de página
    for (let i = 1; i <= state.paginacion.totalPaginas; i++) {
        if (i === state.paginacion.paginaActual) {
            paginacionHTML += `
                <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200">
                    ${i}
                </button>
            `;
        } else {
            paginacionHTML += `
                <button onclick="cambiarPagina(${i})" 
                        class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-200">
                    ${i}
                </button>
            `;
        }
    }
    
    paginacionHTML += '</div>';
    
    // Botón siguiente
    if (state.paginacion.paginaActual < state.paginacion.totalPaginas) {
        paginacionHTML += `
            <button onclick="cambiarPagina(${state.paginacion.paginaActual + 1})" 
                    class="px-4 py-2 text-gray-500 hover:text-gray-700 transition-colors duration-200">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
            </button>
        `;
    }
    
    paginacionContainer.innerHTML = paginacionHTML;
}

// Cambiar página
export function cambiarPagina(pagina) {
    if (pagina >= 1 && pagina <= state.paginacion.totalPaginas) {
        state.paginacion.paginaActual = pagina;
        aplicarFiltros();
        
        // Scroll hacia arriba
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Mostrar estado de carga
function mostrarCargando() {
    if (!contenedorProductos) return;
    
    contenedorProductos.innerHTML = `
        <div class="col-span-full flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <span class="ml-3 text-gray-600">Cargando productos...</span>
        </div>
    `;
}

// Mostrar mensaje de error
function mostrarError(mensaje) {
    if (!contenedorProductos) return;
    
    contenedorProductos.innerHTML = `
        <div class="col-span-full text-center py-12">
            <div class="text-red-600 mb-4">
                <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
            </div>
            <p class="text-gray-600">${mensaje}</p>
        </div>
    `;
}

// Función global para ver producto (para onclick)
window.verProducto = function(id) {
    window.location.href = `/productos/${id}`;
};

// Exportar funciones globales para compatibilidad
window.cargarProductos = cargarProductos;
window.aplicarFiltros = aplicarFiltros;
window.cambiarPagina = cambiarPagina;