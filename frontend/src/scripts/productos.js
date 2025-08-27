// Importar la configuración de la API
import { API_URL } from './config.js';

// Función para formatear precios con puntos como separador de miles (formato chileno)
function formatearPrecio(precio) {
    return precio.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

// Estado global para almacenar productos y filtros
const state = {
    productos: [],
    filtros: {
        busqueda: '',
        precioMin: 0,
        precioMax: 100000,
        categorias: [],
        enStock: false
    },
    paginacion: {
        paginaActual: 1,
        productosPorPagina: 12,
        totalPaginas: 1
    }
};

// Elementos del DOM
let contenedorProductos;
let inputBusqueda;
let rangoPrecio;
let checkboxesCategorias;
let radioStock;
let botonesPaginacion;

// Inicializar la aplicación cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', () => {
    // Obtener referencias a elementos del DOM
    contenedorProductos = document.querySelector('.flex-1.grid');
    inputBusqueda = document.querySelector('input[placeholder="Buscar Producto"]');
    rangoPrecio = document.querySelector('input[type="range"]');
    checkboxesCategorias = document.querySelectorAll('input[type="checkbox"]');
    radioStock = document.querySelectorAll('input[name="disponibilidad"]');
    botonesPaginacion = document.querySelector('.mt-12.flex.justify-center');

    // Configurar eventos
    configurarEventos();

    // Cargar productos
    cargarProductos();
});

// Configurar eventos de los elementos de filtrado
function configurarEventos() {
    // Evento de búsqueda
    inputBusqueda.addEventListener('input', (e) => {
        state.filtros.busqueda = e.target.value.toLowerCase().trim();
        aplicarFiltros();
    });

    // Evento de rango de precio
    rangoPrecio.addEventListener('input', (e) => {
        state.filtros.precioMax = parseInt(e.target.value);
        const precioMaxSpan = document.querySelectorAll('.flex.justify-between span')[1];
        if (precioMaxSpan) {
            if (state.filtros.precioMax >= 100000) {
                precioMaxSpan.textContent = '$100.000+';
            } else {
                precioMaxSpan.textContent = `$${formatearPrecio(state.filtros.precioMax)}`;
            }
        }
        aplicarFiltros();
    });

    // Eventos de categorías
    checkboxesCategorias.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            // Actualizar categorías seleccionadas
            state.filtros.categorias = Array.from(checkboxesCategorias)
                .filter(cb => cb.checked)
                .map(cb => cb.nextElementSibling.textContent.trim());
            aplicarFiltros();
        });
    });

    // Eventos de disponibilidad
    radioStock.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const label = e.target.nextElementSibling.textContent.trim();
            state.filtros.enStock = label === 'En stock';
            aplicarFiltros();
        });
    });
}

// Cargar productos desde la API
async function cargarProductos() {
    try {
        // Mostrar indicador de carga
        mostrarCargando();

        // Obtener productos de la API
        const response = await fetch(`${API_URL}/productos`);
        if (!response.ok) {
            throw new Error(`Error al obtener productos: ${response.status}`);
        }

        const productos = await response.json();
        state.productos = productos;

        // Calcular total de páginas
        state.paginacion.totalPaginas = Math.ceil(productos.length / state.paginacion.productosPorPagina);

        // Aplicar filtros iniciales
        aplicarFiltros();
    } catch (error) {
        console.error('Error al cargar productos:', error);
        mostrarError('No se pudieron cargar los productos. Por favor, intente más tarde.');
    }
}

// Aplicar filtros a los productos
function aplicarFiltros() {
    // Filtrar productos según los criterios seleccionados
    let productosFiltrados = state.productos.filter(producto => {
        // Filtro por búsqueda
        const coincideBusqueda = state.filtros.busqueda === '' || 
            producto.nombre.toLowerCase().includes(state.filtros.busqueda) ||
            (producto.descripcion && producto.descripcion.toLowerCase().includes(state.filtros.busqueda)) ||
            (producto.caracteristicas && producto.caracteristicas.toLowerCase().includes(state.filtros.busqueda));

        // Filtro por precio
        const coincidePrecio = producto.precio >= state.filtros.precioMin && 
                              (state.filtros.precioMax >= 100000 ? true : producto.precio <= state.filtros.precioMax);

        // Filtro por categoría
        const coincideCategoria = state.filtros.categorias.length === 0 || 
                                 state.filtros.categorias.includes(producto.categoria);

        // Filtro por stock
        const coincideStock = !state.filtros.enStock || producto.stock > 0;

        return coincideBusqueda && coincidePrecio && coincideCategoria && coincideStock;
    });

    // Actualizar paginación
    state.paginacion.totalPaginas = Math.ceil(productosFiltrados.length / state.paginacion.productosPorPagina);
    if (state.paginacion.paginaActual > state.paginacion.totalPaginas) {
        state.paginacion.paginaActual = 1;
    }

    // Paginar resultados
    const inicio = (state.paginacion.paginaActual - 1) * state.paginacion.productosPorPagina;
    const fin = inicio + state.paginacion.productosPorPagina;
    const productosPaginados = productosFiltrados.slice(inicio, fin);

    // Mostrar productos
    mostrarProductos(productosPaginados);

    // Actualizar paginación
    actualizarPaginacion();
}

// Mostrar productos en la interfaz
function mostrarProductos(productos) {
    // Limpiar contenedor
    contenedorProductos.innerHTML = '';

    if (productos.length === 0) {
        contenedorProductos.innerHTML = `
            <div class="col-span-full text-center py-8">
                <p class="text-gray-500">No se encontraron productos que coincidan con los filtros seleccionados.</p>
            </div>
        `;
        return;
    }

    // Crear tarjetas de productos
    productos.forEach(producto => {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-xl shadow-lg overflow-hidden transform hover:scale-105 transition-all duration-300';
        card.setAttribute('data-aos', 'fade-up');
        
        card.innerHTML = `
            <div class="relative pb-48 overflow-hidden">
                <img class="absolute inset-0 h-full w-full object-cover transform hover:scale-110 transition-all duration-500" 
                     src="${producto.imagen}" 
                     alt="${producto.nombre}">
            </div>
            <div class="p-4">
                <h3 class="text-lg font-semibold text-gray-800 mb-2">${producto.nombre}</h3>
                <p class="text-gray-600 text-sm mb-2">${producto.descripcion || ''}</p>
                <div class="flex items-center justify-between">
                    <span class="text-blue-600 font-bold">$${formatearPrecio(producto.precio)}</span>
                    <span class="text-sm text-gray-500">${producto.stock > 0 ? 'En stock' : 'Agotado'}</span>
                </div>
                <a href="/productos/${producto.nombre.toLowerCase().replace(/\s+/g, '-')}" class="mt-3 block w-full text-center bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors duration-300">
                    Ver detalles
                </a>
            </div>
        `;
        
        contenedorProductos.appendChild(card);
    });
}

// Actualizar controles de paginación
function actualizarPaginacion() {
    const paginacionDiv = document.querySelector('.mt-12.flex.justify-center .flex.gap-2');
    if (!paginacionDiv) return;

    paginacionDiv.innerHTML = '';

    // No mostrar paginación si hay una sola página
    if (state.paginacion.totalPaginas <= 1) return;

    // Determinar qué páginas mostrar
    let paginas = [];
    const paginaActual = state.paginacion.paginaActual;
    const totalPaginas = state.paginacion.totalPaginas;

    if (totalPaginas <= 5) {
        // Mostrar todas las páginas si son 5 o menos
        paginas = Array.from({length: totalPaginas}, (_, i) => i + 1);
    } else {
        // Siempre incluir primera página
        paginas.push(1);

        // Determinar páginas intermedias
        if (paginaActual <= 3) {
            paginas.push(2, 3, 4, '...');
        } else if (paginaActual >= totalPaginas - 2) {
            paginas.push('...', totalPaginas - 3, totalPaginas - 2, totalPaginas - 1);
        } else {
            paginas.push('...', paginaActual - 1, paginaActual, paginaActual + 1, '...');
        }

        // Siempre incluir última página
        paginas.push(totalPaginas);
    }

    // Crear botones de paginación
    paginas.forEach(pagina => {
        if (pagina === '...') {
            const span = document.createElement('span');
            span.className = 'px-4 py-2';
            span.textContent = '...';
            paginacionDiv.appendChild(span);
        } else {
            const button = document.createElement('button');
            button.className = pagina === paginaActual 
                ? 'px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200'
                : 'px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-200';
            button.textContent = pagina;
            button.addEventListener('click', () => cambiarPagina(pagina));
            paginacionDiv.appendChild(button);
        }
    });

    // Configurar botones de anterior y siguiente
    const btnAnterior = document.querySelector('.mt-12.flex.justify-center button:first-child');
    const btnSiguiente = document.querySelector('.mt-12.flex.justify-center button:last-child');

    btnAnterior.disabled = paginaActual === 1;
    btnAnterior.style.opacity = paginaActual === 1 ? '0.5' : '1';
    btnAnterior.addEventListener('click', () => cambiarPagina(paginaActual - 1));

    btnSiguiente.disabled = paginaActual === totalPaginas;
    btnSiguiente.style.opacity = paginaActual === totalPaginas ? '0.5' : '1';
    btnSiguiente.addEventListener('click', () => cambiarPagina(paginaActual + 1));
}

// Cambiar a una página específica
function cambiarPagina(pagina) {
    if (pagina < 1 || pagina > state.paginacion.totalPaginas) return;
    
    state.paginacion.paginaActual = pagina;
    aplicarFiltros();
    
    // Scroll hacia arriba
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Mostrar indicador de carga
function mostrarCargando() {
    contenedorProductos.innerHTML = `
        <div class="col-span-full text-center py-8">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
            <p class="text-gray-500 mt-4">Cargando productos...</p>
        </div>
    `;
}

// Mostrar mensaje de error
function mostrarError(mensaje) {
    contenedorProductos.innerHTML = `
        <div class="col-span-full text-center py-8">
            <p class="text-red-500">${mensaje}</p>
        </div>
    `;
}