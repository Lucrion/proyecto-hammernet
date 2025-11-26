// Funciones para la página de productos (sin imports para evitar problemas de análisis)

// Utilidades locales mínimas
const env = (typeof window !== 'undefined' ? (window.__ENV__ || {}) : {});
const API_BASE = env.PUBLIC_API_URL || env.PUBLIC_API_URL_PRODUCTION || '/api';

async function getJson(endpoint) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
}

async function checkServerAvailability() {
    try {
        await fetch(`${API_BASE}/health`);
    } catch (e) {
        // No bloquear si falla
        console.warn('Servidor no disponible (healthcheck falló)');
    }
}

// Función para formatear precios con puntos como separador de miles (formato chileno)
function formatearPrecio(precio) {
    return precio.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

// Normalización de URLs de imagen relativas al backend
function getApiHost() {
    try {
        const env = window.__ENV__ || {};
        const api = env.PUBLIC_API_URL || env.PUBLIC_API_URL_PRODUCTION || '/api';
        return api.replace(/\/api$/, '');
    } catch {
        return '';
    }
}

function normalizeImageUrl(u) {
    if (!u) return null;
    const s = String(u);
    if (/^(https?:\/\/|data:)/i.test(s)) return s;
    const host = getApiHost();
    if (s.startsWith('/')) return host + s;
    return host + '/' + s;
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
        categoriaSeleccionadaId: null,
        categoriaSeleccionadaNombre: '',
        subcategoriasIds: [],
        enStock: false
    },
    paginacion: {
        paginaActual: 1,
        productosPorPagina: 12,
        totalPaginas: 1
    }
};

// Límite alto para traer suficientes productos del catálogo en una sola petición
const CATALOGO_FETCH_LIMIT = 1000;

// Elementos del DOM
let contenedorProductos;
let contenedorCategorias;
let contenedorSubcategorias;
let inputBusqueda;
let rangoPrecio;
let checkboxesSubcategorias;
let toggleCategoriasBtn;
let iconCategorias;
let toggleSubcategoriasBtn;
let iconSubcategorias;
// Eliminado: botón y contenedor de "Cargar más"

// Inicializar la aplicación cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', () => {
    // Obtener referencias a elementos del DOM
    contenedorProductos = document.getElementById('productos-grid');
    contenedorCategorias = document.getElementById('categorias-lista');
    contenedorSubcategorias = document.getElementById('subcategorias-lista');
    inputBusqueda = document.getElementById('busqueda');
    rangoPrecio = document.getElementById('precio-rango');
    // Referencias del desplegable de categorías
    toggleCategoriasBtn = document.getElementById('toggle-categorias');
    iconCategorias = document.getElementById('icon-categorias');
    // Referencias del desplegable de subcategorías
    toggleSubcategoriasBtn = document.getElementById('toggle-subcategorias');
    iconSubcategorias = document.getElementById('icon-subcategorias');
    // Las categorías se cargarán dinámicamente cuando se despliegue
    
    // Configurar eventos (excepto categorías, que se asignan tras cargarlas)
    configurarEventos();
    
    // Las categorías se cargarán al abrir el desplegable por primera vez
    
    // Cargar productos iniciales
    cargarProductos();

    // Sin botón "Cargar más"
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
    
    // Desplegable de categorías
    if (toggleCategoriasBtn && contenedorCategorias) {
        toggleCategoriasBtn.addEventListener('click', async () => {
            const estabaOculto = contenedorCategorias.classList.contains('hidden');
            contenedorCategorias.classList.toggle('hidden');
            if (iconCategorias) {
                iconCategorias.classList.toggle('rotate-180');
            }
            // Cargar categorías al primer despliegue si aún no están
            if (estabaOculto && (!contenedorCategorias.innerHTML || contenedorCategorias.innerHTML.trim().length === 0)) {
                try {
                    await cargarCategorias();
                    configurarEventosCategorias();
                } catch (err) {
                    console.error('Error al cargar categorías:', err);
                }
            }
        });
    }

    // Desplegable de subcategorías
    if (toggleSubcategoriasBtn && contenedorSubcategorias) {
        toggleSubcategoriasBtn.addEventListener('click', async () => {
            if (!state.filtros.categoriaSeleccionadaId) return;
            const estabaOculto = contenedorSubcategorias.classList.contains('hidden');
            contenedorSubcategorias.classList.toggle('hidden');
            if (iconSubcategorias) {
                iconSubcategorias.classList.toggle('rotate-180');
            }
            // Cargar subcategorías al primer despliegue si aún no están o si cambió la categoría
            const needsLoad = (!contenedorSubcategorias.dataset.loadedFor || Number(contenedorSubcategorias.dataset.loadedFor) !== Number(state.filtros.categoriaSeleccionadaId));
            if (estabaOculto && needsLoad) {
                try {
                    await cargarSubcategoriasParaCategoria(state.filtros.categoriaSeleccionadaId);
                    configurarEventosSubcategorias();
                    contenedorSubcategorias.dataset.loadedFor = String(state.filtros.categoriaSeleccionadaId);
                } catch (err) {
                    console.error('Error al cargar subcategorías:', err);
                }
            }
        });
    }

    // Los eventos de categorías se asignan después de renderizar dinámicamente
    
    // Filtro de stock eliminado del UI
}

// Cargar categorías y renderizarlas como radios (selección única)
async function cargarCategorias() {
    if (!contenedorCategorias) return;
    try {
        const categorias = await getJson('/categorias');
        const listaCat = Array.isArray(categorias) ? categorias : [];
        contenedorCategorias.innerHTML = listaCat.map(c => `
            <label class="flex items-center hover:bg-gray-50 p-2 rounded-lg transition-colors duration-200 cursor-pointer group">
                <input type="radio" name="categoria" value="${c.id_categoria}" data-nombre="${c.nombre}" class="form-radio h-5 w-5 text-blue-600 transition duration-150 ease-in-out">
                <span class="ml-3 text-gray-700 group-hover:text-blue-600 transition-colors duration-200">${c.nombre}</span>
            </label>
        `).join('');
        // Limpiar selecciones previas
        state.filtros.categoriaSeleccionadaId = null;
        state.filtros.categoriaSeleccionadaNombre = '';
        state.filtros.subcategoriasIds = [];
        if (toggleSubcategoriasBtn) {
            toggleSubcategoriasBtn.disabled = true;
        }
    } catch (error) {
        console.error('Error al obtener categorías:', error);
    }
}

// Asignar eventos a los radios de categorías renderizados dinámicamente
function configurarEventosCategorias() {
    const radiosCategorias = document.querySelectorAll('input[name="categoria"]');
    radiosCategorias.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const id = Number(e.target.value);
            const nombre = e.target.getAttribute('data-nombre') || '';
            // Actualizar estado
            state.filtros.categoriaSeleccionadaId = id;
            state.filtros.categoriaSeleccionadaNombre = nombre;
            // Habilitar el toggle de subcategorías
            if (toggleSubcategoriasBtn) {
                toggleSubcategoriasBtn.disabled = false;
            }
            // Limpiar lista de subcategorías y su contenedor
            state.filtros.subcategoriasIds = [];
            if (contenedorSubcategorias) {
                contenedorSubcategorias.innerHTML = '';
                contenedorSubcategorias.classList.add('hidden');
                if (iconSubcategorias) iconSubcategorias.classList.remove('rotate-180');
                contenedorSubcategorias.dataset.loadedFor = '';
            }
            // Aplicar filtros por categoría seleccionada
            state.paginacion.paginaActual = 1;
            aplicarFiltros();
        });
    });
}

// Cargar subcategorías para la categoría seleccionada y renderizarlas como checkboxes
async function cargarSubcategoriasParaCategoria(idCategoria) {
    if (!contenedorSubcategorias || !idCategoria) return;
    try {
        const subs = await getJson(`/subcategorias?categoria_id=${idCategoria}`);
        const listaSub = Array.isArray(subs) ? subs : [];
        contenedorSubcategorias.innerHTML = listaSub.map(s => `
            <label class="flex items-center hover:bg-gray-50 p-2 rounded-lg transition-colors duration-200 cursor-pointer group">
                <input type="checkbox" name="subcategoria" value="${s.id_subcategoria}" data-nombre="${s.nombre}" class="form-checkbox h-5 w-5 text-blue-600 rounded transition duration-150 ease-in-out">
                <span class="ml-3 text-gray-700 group-hover:text-blue-600 transition-colors duration-200">${s.nombre}</span>
            </label>
        `).join('');
        checkboxesSubcategorias = document.querySelectorAll('input[name="subcategoria"]');
        state.filtros.subcategoriasIds = [];
    } catch (error) {
        console.error('Error al obtener subcategorías:', error);
    }
}

// Asignar eventos a los checkboxes de subcategorías renderizados dinámicamente
function configurarEventosSubcategorias() {
    if (!checkboxesSubcategorias) return;
    checkboxesSubcategorias.forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const subcatId = Number(e.target.value);
            if (e.target.checked) {
                state.filtros.subcategoriasIds.push(subcatId);
            } else {
                state.filtros.subcategoriasIds = state.filtros.subcategoriasIds.filter(sid => sid !== subcatId);
            }
            state.paginacion.paginaActual = 1;
            aplicarFiltros();
        });
    });
}

// Cargar productos desde la API
async function cargarProductos() {
    try {
        mostrarCargando();
        
        // Verificar disponibilidad del servidor (no bloquear si falla)
        try {
            await checkServerAvailability();
        } catch (error) {
            console.warn('Advertencia: No se pudo verificar la disponibilidad del servidor:', error);
        }

        // Obtener productos del catálogo (pidiendo más que el límite por defecto 10)
        const productos = await getJson(`/productos/catalogo?skip=0&limit=${CATALOGO_FETCH_LIMIT}`);
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
function aplicarFiltros() {
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
        const precio = Number(producto.precio_final ?? producto.precio_venta ?? producto.precio ?? 0);
        return precio >= state.filtros.precioMin && precio <= state.filtros.precioMax;
    });
    
    // Filtro por categoría seleccionada (si existe)
    if (state.filtros.categoriaSeleccionadaId) {
        productosFiltrados = productosFiltrados.filter(producto => {
            const idCat = Number(producto.id_categoria ?? 0);
            return idCat === Number(state.filtros.categoriaSeleccionadaId);
        });
    }

    // Filtro de subcategorías
    if (state.filtros.subcategoriasIds.length > 0) {
        productosFiltrados = productosFiltrados.filter(producto => {
            const idSub = Number(producto.id_subcategoria ?? -1);
            return state.filtros.subcategoriasIds.includes(idSub);
        });
    }
    
    // Filtro de stock removido
    
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

    // Sin botón "Cargar más"
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
    
    contenedorProductos.innerHTML = productos.map(producto => {
        const img = normalizeImageUrl(producto.imagen_url);
        return `
        <div class="bg-white rounded-xl border border-gray-100 shadow hover:shadow-lg transition-all duration-300 cursor-pointer flex flex-col" onclick="verProducto(${producto.id_producto})">
            <div class="relative w-full h-40 flex items-center justify-center bg-white">
                ${producto.oferta_activa ? '<span class=\'absolute top-2 left-2 text-[10px] px-2 py-1 bg-red-100 text-red-700 rounded\'>Oferta</span>' : ''}
                <img src="${img || '/images/placeholder-product.jpg'}" 
                     alt="${producto.nombre}" 
                     class="h-32 w-auto object-contain">
            </div>
            <div class="p-4 flex-1 flex flex-col">
                <h3 class="text-sm font-semibold text-gray-900 mb-1 text-center">${producto.nombre}</h3>
                <p class="text-gray-600 text-xs mb-3 line-clamp-2 text-center">${producto.descripcion || 'Sin descripción'}</p>
                <div class="mt-auto flex items-center justify-center gap-2">
                    ${producto.oferta_activa ? '<span class="text-xs line-through text-gray-500">$' + formatearPrecio(producto.precio_venta ?? producto.precio ?? 0) + '</span>' : ''}
                    <span class="px-4 py-2 bg-black text-white rounded text-lg font-bold">$${formatearPrecio(producto.precio_final ?? producto.precio_venta ?? producto.precio ?? 0)}</span>
                </div>
            </div>
        </div>
    `}).join('');
}

// Eliminado: append de productos para "Cargar más"

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
        <p class="text-sm text-gray-500">Mostrando ${inicio} a ${fin} de ${state.totalProductos} resultados</p>
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
                <button class="px-3 py-1 bg-black text-white rounded-full hover:bg-gray-900 transition-colors duration-200 text-sm">
                    ${i}
                </button>
            `;
        } else {
            paginacionHTML += `
                <button onclick="cambiarPagina(${i})" 
                        class="px-3 py-1 text-gray-700 hover:bg-gray-100 rounded-full transition-colors duration-200 text-sm">
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
function cambiarPagina(pagina) {
    if (pagina >= 1 && pagina <= state.paginacion.totalPaginas) {
        state.paginacion.paginaActual = pagina;
        aplicarFiltros();
        
        // Scroll hacia arriba
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
// Eliminado: función "Cargar más"
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
