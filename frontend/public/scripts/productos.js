// Configuración de la API usando variables de entorno
const isDevelopment = typeof window !== 'undefined' 
    ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    : false;

// Obtener variables de entorno
const getEnvVar = (name) => {
    if (typeof window !== 'undefined' && window.__ENV__) {
        return window.__ENV__[name];
    }
    return undefined;
};

const API_URL = isDevelopment 
    ? getEnvVar('PUBLIC_API_URL')
    : getEnvVar('PUBLIC_API_URL_PRODUCTION');

const API_TIMEOUT = parseInt(getEnvVar('PUBLIC_API_TIMEOUT'));

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
        productosPorPagina: 16,
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
    if (inputBusqueda) {
        inputBusqueda.addEventListener('input', (e) => {
            state.filtros.busqueda = e.target.value.toLowerCase().trim();
            aplicarFiltros();
        });
    }

    // Evento de rango de precio
    if (rangoPrecio) {
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
    }

    // Eventos de categorías
    if (checkboxesCategorias && checkboxesCategorias.length > 0) {
        checkboxesCategorias.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                // Mapear nombres de interfaz a valores de API
                const mapeoCategoria = {
                    'Herramientas': 'herramientas',
                    'Construcción': 'construccion',
                    'Jardinería y Exteriores': 'jardineria_y_exteriores',
                    'Electricidad': 'electricidad',
                    'Plomería': 'plomeria',
                    'Seguridad': 'seguridad',
                    'Hogar y Limpieza': 'hogar_y_limpieza',
                    'Pinturas': 'pinturas',
                    'Tornillos y Clavos': 'tornillos_y_clavos'
                };
                
                // Actualizar categorías seleccionadas
                state.filtros.categorias = Array.from(checkboxesCategorias)
                    .filter(cb => cb.checked)
                    .map(cb => {
                        const textoCategoria = cb.nextElementSibling.textContent.trim();
                        return mapeoCategoria[textoCategoria] || textoCategoria.toLowerCase();
                    });
                aplicarFiltros();
            });
        });
    }

    // Eventos de disponibilidad
    if (radioStock && radioStock.length > 0) {
        radioStock.forEach(radio => {
            radio.addEventListener('change', (e) => {
                const label = e.target.nextElementSibling.textContent.trim();
                state.filtros.enStock = label === 'En stock';
                aplicarFiltros();
            });
        });
    }
}

// Cargar productos desde la API
async function cargarProductos() {
    try {
        // Mostrar indicador de carga
        mostrarCargando();

        // Obtener datos de las nuevas tablas
        const [responseProductos, responseCategorias, responseInventario] = await Promise.all([
            fetch(`${API_URL}/productos`),
            fetch(`${API_URL}/categorias`),
            fetch(`${API_URL}/inventario`)
        ]);

        if (!responseProductos.ok) {
            throw new Error(`Error al obtener productos: ${responseProductos.status}`);
        }
        if (!responseCategorias.ok) {
            throw new Error(`Error al obtener categorías: ${responseCategorias.status}`);
        }
        if (!responseInventario.ok) {
            throw new Error(`Error al obtener inventario: ${responseInventario.status}`);
        }

        const productos = await responseProductos.json();
        const categorias = await responseCategorias.json();
        const inventario = await responseInventario.json();

        // Combinar datos de productos con categorías e inventario
        const productosCompletos = productos
            .filter(producto => producto.precio && producto.precio > 0 && producto.imagen) // Solo productos catalogados
            .map(producto => {
                // Obtener información de categoría
                const categoria = categorias.find(c => c.id_categoria === producto.id_categoria);
                const nombreCategoria = categoria ? categoria.nombre : 'Sin categoría';
                
                // Obtener stock del inventario
                const itemInventario = inventario.find(i => i.id_producto === producto.id_producto);
                const stock = itemInventario ? itemInventario.stock_actual : 0;
                
                return {
                    id: producto.id_producto,
                    nombre: producto.nombre,
                    descripcion: producto.descripcion || '',
                    precio: producto.precio,
                    imagen: producto.imagen,
                    categoria: nombreCategoria,
                    caracteristicas: producto.caracteristicas || '',
                    stock: stock,
                    origen: 'catalogo'
                };
            })
            .filter(producto => producto.stock > 0); // Solo productos en stock

        state.productos = productosCompletos;

        // Calcular total de páginas
        state.paginacion.totalPaginas = Math.ceil(productosCompletos.length / state.paginacion.productosPorPagina);

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
    // Verificar que el contenedor existe
    if (!contenedorProductos) return;
    
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
        card.className = 'bg-white rounded-xl shadow-lg overflow-hidden transform hover:scale-105 transition-all duration-300 h-80';
        card.setAttribute('data-aos', 'fade-up');
        
        card.innerHTML = `
            <div class="relative h-48 overflow-hidden bg-gray-100 flex items-center justify-center">
                <img class="max-h-full max-w-full object-contain transform hover:scale-110 transition-all duration-500" 
                     src="${producto.imagen}" 
                     alt="${producto.nombre}">
            </div>
            <div class="p-4 flex flex-col h-32">
                <div class="space-y-1">
                    <h3 class="text-base font-semibold text-gray-800 break-words leading-tight">${producto.nombre}</h3>
                    <div class="flex items-center justify-between gap-2">
                        <span class="text-lg font-bold text-blue-600 flex-shrink-0">$${formatearPrecio(producto.precio)}</span>
                        <span class="text-xs px-2 py-1 rounded-full font-medium whitespace-nowrap ${producto.stock > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">${producto.stock > 0 ? 'En stock' : 'Agotado'}</span>
                    </div>
                </div>
            </div>
        `;
        
        // Hacer la tarjeta clickeable
        card.style.cursor = 'pointer';
        card.addEventListener('click', () => {
            if (producto.origen === 'inventario') {
                // Para productos del inventario, mostrar información básica o redirigir a una página genérica
                alert(`Producto: ${producto.nombre}\nPrecio: $${formatearPrecio(producto.precio)}\nStock: ${producto.stock} unidades\n\nEste producto está disponible desde nuestro inventario.`);
            } else {
                // Para productos del catálogo, ir a la página de detalle
                window.location.href = `/productos/${producto.nombre.toLowerCase().replace(/\s+/g, '-')}`;
            }
        });
        
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

    if (btnAnterior) {
        btnAnterior.disabled = paginaActual === 1;
        btnAnterior.style.opacity = paginaActual === 1 ? '0.5' : '1';
        btnAnterior.addEventListener('click', () => cambiarPagina(paginaActual - 1));
    }

    if (btnSiguiente) {
        btnSiguiente.disabled = paginaActual === totalPaginas;
        btnSiguiente.style.opacity = paginaActual === totalPaginas ? '0.5' : '1';
        btnSiguiente.addEventListener('click', () => cambiarPagina(paginaActual + 1));
    }
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
    if (!contenedorProductos) return;
    
    contenedorProductos.innerHTML = `
        <div class="col-span-full text-center py-8">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
            <p class="text-gray-500 mt-4">Cargando productos...</p>
        </div>
    `;
}

// Mostrar mensaje de error
function mostrarError(mensaje) {
    if (!contenedorProductos) return;
    
    contenedorProductos.innerHTML = `
        <div class="col-span-full text-center py-8">
            <p class="text-red-500">${mensaje}</p>
        </div>
    `;
}

// Exponer funciones al objeto window
window.cargarProductos = cargarProductos;
window.aplicarFiltros = aplicarFiltros;
window.cambiarPagina = cambiarPagina;