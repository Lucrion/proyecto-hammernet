// Funciones para la página de detalle de producto
import { API_URL, checkServerAvailability, handleApiError } from '../scripts/utils/config.js';
import { getData } from '../scripts/utils/api.js';

// Función para formatear precios con puntos como separador de miles (formato chileno)
function formatearPrecio(precio) {
    return precio.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

// Calcular precio final considerando oferta vigente
function calcularPrecioFinal(p) {
    const base = Number(p.precio_venta ?? p.precio ?? 0);
    const inicio = p.fecha_inicio_oferta ? new Date(p.fecha_inicio_oferta) : null;
    const fin = p.fecha_fin_oferta ? new Date(p.fecha_fin_oferta) : null;
    const ahora = new Date();
    const vigente = !!p.oferta_activa && (!inicio || ahora >= inicio) && (!fin || ahora <= fin);
    if (!vigente || !p.tipo_oferta || Number(p.valor_oferta) <= 0) return { precio_final: base, tiene_oferta: false };
    let final = base;
    if (p.tipo_oferta === 'porcentaje') {
        const desc = Math.min(100, Math.max(0, Number(p.valor_oferta)));
        final = Math.max(0, base * (1 - desc / 100));
    } else if (p.tipo_oferta === 'fijo') {
        final = Math.max(0, base - Number(p.valor_oferta));
    }
    return { precio_final: final, tiene_oferta: true };
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
export async function cargarDetalleProducto() {
    try {
        // Verificar disponibilidad del servidor
        const serverStatus = await checkServerAvailability();
        if (!serverStatus.available) {
            mostrarError('El servidor no está disponible. Por favor, intenta más tarde.');
            return;
        }

        // Obtener el ID del producto desde la URL
        const pathParts = window.location.pathname.split('/');
        const productoId = pathParts[pathParts.length - 1];
        
        if (!productoId || isNaN(productoId)) {
            mostrarError('ID de producto inválido');
            return;
        }

        // Cargar datos del producto
        const producto = await getData(`/api/productos/${productoId}`);
        const { precio_final, tiene_oferta } = calcularPrecioFinal(producto);
        producto.precio_final = precio_final;
        producto.tiene_oferta = tiene_oferta;
        producto.precio_original = tiene_oferta ? (producto.precio_venta ?? producto.precio) : null;
        state.producto = producto;
        
        // Mostrar detalles del producto
        mostrarDetalleProducto(producto);
        
        // Actualizar breadcrumb
        if (breadcrumbProducto) {
            breadcrumbProducto.textContent = producto.nombre;
        }
        
        // Cargar productos similares
        await cargarProductosSimilares(producto.categoria_id);
        
    } catch (error) {
        console.error('Error al cargar detalle del producto:', error);
        handleApiError(error, 'cargar detalle del producto');
        mostrarError('Error al cargar los detalles del producto');
    }
}

// Función para cargar productos similares
async function cargarProductosSimilares(categoriaId) {
    try {
        if (!categoriaId) return;
        
        const productos = await getData(`/api/productos?categoria_id=${categoriaId}`);
        // Filtrar el producto actual y tomar solo 4 productos similares
        const productosSimilares = (Array.isArray(productos) ? productos : [])
            .filter(p => p.id !== state.producto.id && p.activo !== false)
            .slice(0, 4);
        
        state.productosSimilares = productosSimilares;
        mostrarProductosSimilares(productosSimilares);
    } catch (error) {
        console.error('Error al cargar productos similares:', error);
        // No mostrar error para productos similares, es opcional
    }
}

// Función para mostrar los detalles del producto
function mostrarDetalleProducto(producto) {
    if (!contenedorProducto) return;
    
    const stockStatus = producto.stock > 0 ? 
        `<span class="text-green-600 font-medium">En stock (${producto.stock} disponibles)</span>` :
        `<span class="text-red-600 font-medium">Sin stock</span>`;
    
    contenedorProducto.innerHTML = `
        <!-- Imagen del producto -->
        <div class="space-y-4">
            <div class="aspect-w-1 aspect-h-1 bg-gray-200 rounded-lg overflow-hidden">
                <img src="${producto.imagen || '/images/placeholder-product.jpg'}" 
                     alt="${producto.nombre}" 
                     class="w-full h-full object-cover">
            </div>
        </div>
        
        <!-- Información del producto -->
        <div class="space-y-6">
            <div>
                <h1 class="text-3xl font-bold text-gray-900">${producto.nombre}</h1>
                <p class="text-sm text-gray-500 mt-2">${producto.categoria_nombre || 'Sin categoría'}</p>
            </div>
            
            <div class="flex items-center space-x-3">
                <span class="text-3xl font-bold text-black">$${formatearPrecio(Math.round(producto.precio_final))}</span>
                ${producto.tiene_oferta ? `
                <span class="text-xl text-gray-500 line-through">$${formatearPrecio(Math.round(producto.precio_original))}</span>
                <span class="text-sm px-2 py-1 bg-red-100 text-red-700 rounded">Oferta</span>
                ` : ''}
            </div>
            
            <div class="space-y-4">
                <div>
                    <h3 class="text-lg font-medium text-gray-900">Descripción</h3>
                    <p class="mt-2 text-gray-600">${producto.descripcion || 'Sin descripción disponible'}</p>
                </div>
                
                <div>
                    <h3 class="text-lg font-medium text-gray-900">Disponibilidad</h3>
                    <p class="mt-2">${stockStatus}</p>
                </div>
                
                ${producto.proveedor_nombre ? `
                <div>
                    <h3 class="text-lg font-medium text-gray-900">Proveedor</h3>
                    <p class="mt-2 text-gray-600">${producto.proveedor_nombre}</p>
                </div>
                ` : ''}
            </div>
            
            <div class="space-y-4">
                <button ${producto.stock <= 0 ? 'disabled' : ''} 
                        onclick="agregarAlCarrito(${producto.id})"
                        class="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors ${producto.stock <= 0 ? 'opacity-50 cursor-not-allowed' : ''}">
                    ${producto.stock > 0 ? 'Agregar al carrito' : 'Sin stock'}
                </button>
                
                <button onclick="window.history.back()" 
                        class="w-full bg-gray-200 text-gray-800 py-3 px-6 rounded-lg font-medium hover:bg-gray-300 transition-colors">
                    Volver
                </button>
            </div>
        </div>
    `;
}

// Función para mostrar productos similares
function mostrarProductosSimilares(productos) {
    if (!contenedorSimilares || productos.length === 0) {
        // Ocultar la sección si no hay productos similares
        const seccionSimilares = document.querySelector('section.mt-16');
        if (seccionSimilares) {
            seccionSimilares.style.display = 'none';
        }
        return;
    }
    
    contenedorSimilares.innerHTML = productos.map(p => {
        const { precio_final, tiene_oferta } = calcularPrecioFinal(p);
        const precioBase = Number(p.precio_venta ?? p.precio ?? 0);
        const final = Number(precio_final ?? precioBase);
        const id = p.id_producto ?? p.id;
        const imagen = p.imagen_url || p.imagen || '/images/placeholder-product.jpg';
        return `
        <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
            <div class="aspect-w-1 aspect-h-1 relative">
                ${tiene_oferta ? '<span class="absolute top-2 left-2 text-[10px] px-2 py-1 bg-red-100 text-red-700 rounded">Oferta</span>' : ''}
                <img src="${imagen}" 
                     alt="${p.nombre}" 
                     class="w-full h-48 object-cover">
            </div>
            <div class="p-4">
                <h3 class="text-lg font-semibold text-gray-800 mb-2">${p.nombre}</h3>
                <p class="text-gray-600 text-sm mb-3 line-clamp-2">${p.descripcion || 'Sin descripción'}</p>
                <div class="flex justify-between items-center">
                    <div class="flex items-center gap-2">
                        ${tiene_oferta ? '<span class="text-sm line-through text-gray-500">$' + formatearPrecio(precioBase) + '</span>' : ''}
                        <span class="text-xl font-bold text-black">$${formatearPrecio(final)}</span>
                    </div>
                    <button onclick="verProducto(${id})" 
                            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">
                        Ver más
                    </button>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

// Función para mostrar errores
function mostrarError(mensaje) {
    if (contenedorProducto) {
        contenedorProducto.innerHTML = `
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
}

// Funciones globales para compatibilidad
window.verProducto = function(id) {
    window.location.href = `/productos/${id}`;
};

window.agregarAlCarrito = function(productoId) {
    // Implementar lógica del carrito aquí
    console.log('Agregar al carrito:', productoId);
    // Por ahora solo mostrar una notificación
    if (typeof mostrarNotificacion === 'function') {
        mostrarNotificacion('Producto agregado al carrito', 'success');
    } else {
        alert('Producto agregado al carrito');
    }
};

// Exportar función principal
window.cargarDetalleProducto = cargarDetalleProducto;
