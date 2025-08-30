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

// Estado global
const state = {
    producto: null,
    productosSimilares: [],
    productoSlug: typeof window !== 'undefined' ? window.location.pathname.split('/').pop() : ''
};

// Elementos del DOM
let breadcrumbProducto;
let contenedorProducto;
let contenedorSimilares;

// Inicializar la aplicación cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', () => {
    // Obtener referencias a elementos del DOM
    breadcrumbProducto = document.querySelector('nav.text-sm ol li:last-child');
    contenedorProducto = document.querySelector('.grid.grid-cols-1.md\\:grid-cols-2.gap-8');
    contenedorSimilares = document.querySelector('section.mt-16 .grid');

    // Cargar detalles del producto
    cargarDetalleProducto();
});

// Función para cargar los detalles del producto
async function cargarDetalleProducto() {
    try {
        // Debug: Mostrar información del slug
        console.log('🔍 Iniciando carga de detalle del producto');
        console.log('📍 Slug del producto:', state.productoSlug);
        console.log('🌐 API URL:', API_URL);
        
        // Verificar que API_URL esté definida
        if (!API_URL) {
            console.error('❌ API_URL no está definida');
            console.log('Variables de entorno disponibles:', window.__ENV__);
            mostrarError('Error de configuración: URL de la API no definida');
            return;
        }
        
        // Obtener todos los productos
        console.log('📡 Obteniendo productos desde:', `${API_URL}/productos`);
        const response = await fetch(`${API_URL}/productos`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const productos = await response.json();
        console.log('✅ Productos obtenidos:', productos.length);
        
        // Debug: Mostrar todos los slugs disponibles
        console.log('🏷️ Slugs disponibles:');
        productos.forEach((p, index) => {
            const slug = p.nombre.toLowerCase().replace(/\s+/g, '-');
            console.log(`  ${index + 1}. "${p.nombre}" -> "${slug}"`);
        });
        
        // Encontrar el producto actual por su slug
        const productoActual = productos.find(p => {
            const slugProducto = p.nombre.toLowerCase().replace(/\s+/g, '-');
            return slugProducto === state.productoSlug;
        });
        
        console.log('🎯 Producto encontrado:', productoActual ? productoActual.nombre : 'No encontrado');
        
        if (!productoActual) {
            console.error('❌ Producto no encontrado:', state.productoSlug);
            mostrarError(`Producto no encontrado: "${state.productoSlug}"`);
            return;
        }
        
        // Guardar el producto en el estado
        state.producto = productoActual;
        
        // Actualizar el breadcrumb
        if (breadcrumbProducto) {
            breadcrumbProducto.textContent = productoActual.nombre;
        }
        
        // Mostrar los detalles del producto
        mostrarDetalleProducto(productoActual);
        
        // Encontrar productos similares (misma categoría)
        const productosSimilares = productos
            .filter(p => p.categoria === productoActual.categoria && p.id !== productoActual.id)
            .slice(0, 4);
        
        // Guardar productos similares en el estado
        state.productosSimilares = productosSimilares;
        
        // Mostrar productos similares
        mostrarProductosSimilares(productosSimilares);
        
        console.log('✅ Detalle del producto cargado exitosamente');
    } catch (error) {
        console.error('❌ Error al cargar detalles del producto:', error);
        console.error('Stack trace:', error.stack);
        mostrarError(`Error al cargar los detalles del producto: ${error.message}`);
    }
}

// Función para mostrar los detalles del producto
function mostrarDetalleProducto(producto) {
    if (!contenedorProducto) return;
    
    contenedorProducto.innerHTML = `
        <div class="bg-white rounded-xl shadow-lg overflow-hidden">
            <div class="relative pb-96">
                <img class="absolute inset-0 h-full w-full object-cover" 
                     src="${producto.imagen}" 
                     alt="${producto.nombre}">
            </div>
        </div>
        
        <div class="bg-white rounded-xl shadow-lg p-6">
            <h1 class="text-3xl font-bold text-gray-800 mb-4">${producto.nombre}</h1>
            
            <div class="flex items-center justify-between mb-6">
                <span class="text-2xl font-bold text-blue-600">$${formatearPrecio(producto.precio)}</span>
                <span class="px-3 py-1 ${producto.stock > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'} rounded-full text-sm font-medium">
                    ${producto.stock > 0 ? 'En stock' : 'Agotado'}
                </span>
            </div>
            
            <div class="mb-6">
                <h2 class="text-lg font-semibold text-gray-800 mb-2">Descripción</h2>
                <p class="text-gray-600">${producto.descripcion || 'No hay descripción disponible'}</p>
            </div>
            
            <div class="mb-6">
                <h2 class="text-lg font-semibold text-gray-800 mb-2">Características</h2>
                <p class="text-gray-600">${producto.caracteristicas || 'No hay características disponibles'}</p>
            </div>
            
            <div class="mb-6">
                <h2 class="text-lg font-semibold text-gray-800 mb-2">Categoría</h2>
                <p class="text-gray-600">${producto.categoria || 'Sin categoría'}</p>
            </div>
        </div>
    `;
}

// Función para mostrar productos similares
function mostrarProductosSimilares(productos) {
    if (!contenedorSimilares) return;
    
    if (productos.length === 0) {
        contenedorSimilares.innerHTML = `
            <div class="col-span-full text-center py-8">
                <p class="text-gray-500">No hay productos similares disponibles.</p>
            </div>
        `;
        return;
    }
    
    contenedorSimilares.innerHTML = '';
    
    productos.forEach(producto => {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-xl shadow-lg overflow-hidden transform hover:scale-105 transition-all duration-300';
        
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
        
        contenedorSimilares.appendChild(card);
    });
}

// Función para mostrar error
function mostrarError(mensaje) {
    if (!contenedorProducto) return;
    
    contenedorProducto.innerHTML = `
        <div class="col-span-full text-center py-8">
            <p class="text-red-500">${mensaje}</p>
        </div>
    `;
}