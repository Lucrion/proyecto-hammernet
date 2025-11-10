// Funciones para la página principal
import { API_URL, checkServerAvailability, handleApiError } from '../utils/config.js';
import { getData, postData } from '../utils/api.js';

// Estado global
const state = {
    token: localStorage.getItem('token'),
    user: JSON.parse(localStorage.getItem('user')),
    carrito: JSON.parse(localStorage.getItem('carrito')) || [],
    productos: []
};

// Función para formatear precios con puntos como separador
function formatearPrecio(precio) {
    return precio.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

// Inicializar animacion si esta disponible
if (typeof AOS !== 'undefined') {
    AOS.init({
        duration: 1000,
        once: true
    });
}

// Función para cargar productos destacados
export async function cargarProductosDestacados() {
    try {
        // Verificar si hay token de autenticación
        const token = localStorage.getItem('token');
        if (!token) {
            console.warn('No hay token de autenticación, mostrando productos públicos');
            // No redirigir, permitir que la página funcione sin autenticación
            // return;
        }

        // Verificar disponibilidad del servidor (opcional, no bloquear si falla)
        try {
            await checkServerAvailability();
        } catch (error) {
            console.warn('No se pudo verificar la disponibilidad del servidor, continuando...');
        }

        mostrarCargando();

        const productos = await getData('/api/productos/catalogo');
        
        if (!productos || !Array.isArray(productos)) {
            throw new Error('La respuesta no es un array válido');
        }

        // Filtrar productos destacados (primeros 4)
        const productosDestacados = productos.slice(0, 4);
        state.productos = productosDestacados;
        
        mostrarProductosDestacados(productosDestacados);
        
    } catch (error) {
        console.error('Error al cargar productos destacados:', error);
        mostrarError('Error al cargar los productos destacados');
    }
}

// Función para cargar productos generales (inicio)
export async function cargarProductosInicio() {
    try {
        // Verificar disponibilidad del servidor (opcional)
        try {
            await checkServerAvailability();
        } catch (error) {
            console.warn('No se pudo verificar la disponibilidad del servidor, continuando...');
        }

        mostrarCargandoGenerales();

        const productos = await getData('/api/productos/catalogo');

        if (!productos || !Array.isArray(productos)) {
            throw new Error('La respuesta no es un array válido');
        }

        // Mostrar los primeros 4 productos generales
        const productosGenerales = productos.slice(0, 4);
        mostrarProductosGenerales(productosGenerales);
    } catch (error) {
        console.error('Error al cargar productos:', error);
        mostrarErrorGenerales('Error al cargar los productos');
    }
}

// Mostrar estado de carga para productos generales
function mostrarCargandoGenerales() {
    const contenedor = document.getElementById('productos-inicio');
    if (!contenedor) return;
    contenedor.innerHTML = `
        <div class="col-span-full flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <span class="ml-3 text-gray-600">Cargando productos...</span>
        </div>
    `;
}

// Mostrar error para productos generales
function mostrarErrorGenerales(mensaje) {
    const contenedor = document.getElementById('productos-inicio');
    if (!contenedor) return;
    contenedor.innerHTML = `
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

// Función para mostrar productos generales
function mostrarProductosGenerales(productos) {
    const contenedor = document.getElementById('productos-inicio');
    if (!contenedor) return;

    contenedor.innerHTML = '';

    productos.forEach(producto => {
        const imagen = producto.imagen_url || '/images/placeholder-product.jpg';
        const precioBase = Number(producto.precio_venta ?? producto.precio ?? 0);
        const precio = Number(producto.precio_final ?? precioBase);
        const tieneOferta = precioBase > 0 && precio < precioBase;
        const id = producto.id_producto ?? producto.id;
        const descripcionCorta = (() => { const d=(producto.descripcion||'').trim(); const dc=d.length>100?d.slice(0,100)+'...':d; return dc; })();
        const productoHTML = `
            <div class="bg-white rounded-xl border border-gray-100 shadow hover:shadow-lg transition-all duration-300 cursor-pointer flex flex-col overflow-hidden" data-aos="fade-up" onclick="verProducto(${id})">
                <div class="relative w-full aspect-square bg-white">
                    ${tieneOferta ? '<span class=\'absolute top-2 left-2 z-10 text-[10px] px-2 py-1 bg-red-100 text-red-700 rounded\'>Oferta</span>' : ''}
                    <div class="absolute inset-2 border border-gray-200 rounded-lg overflow-hidden">
                        <img src="${imagen}" alt="${producto.nombre}" class="w-full h-full object-cover" />
                    </div>
                </div>
                <div class="p-4 flex-1 flex flex-col">
                    <h3 class="text-sm font-semibold text-gray-900 mb-1 text-center">${producto.nombre}</h3>
                    ${descripcionCorta ? `<p class="text-gray-600 text-xs mb-3 line-clamp-2 text-center">${descripcionCorta}</p>` : ''}
                    <div class="mt-auto flex items-center justify-center gap-2">
                        ${tieneOferta ? '<span class="text-xs line-through text-gray-500">$' + formatearPrecio(precioBase) + '</span>' : ''}
                        <span class="px-4 py-2 bg-black text-white rounded text-lg font-bold">$${formatearPrecio(precio)}</span>
                    </div>
                </div>
            </div>
        `;
        contenedor.innerHTML += productoHTML;
    });
}
// Función para mostrar productos destacados
function mostrarProductosDestacados(productos) {
    const contenedor = document.getElementById('productos-destacados');
    if (!contenedor) return;

    contenedor.innerHTML = '';

    productos.forEach(producto => {
        const imagen = producto.imagen_url || '/images/placeholder-product.jpg';
        const precioBase = Number(producto.precio_venta ?? producto.precio ?? 0);
        const precio = Number(producto.precio_final ?? precioBase);
        const tieneOferta = precioBase > 0 && precio < precioBase;
        const id = producto.id_producto ?? producto.id;
        const descripcionCorta = (() => { const d=(producto.descripcion||'').trim(); const dc=d.length>100?d.slice(0,100)+'...':d; return dc; })();
        const productoHTML = `
            <div class="bg-white rounded-xl border border-gray-100 shadow hover:shadow-lg transition-all duration-300 cursor-pointer flex flex-col overflow-hidden" data-aos="fade-up" onclick="verProducto(${id})">
                <div class="relative w-full aspect-square bg-white">
                    ${tieneOferta ? '<span class=\'absolute top-2 left-2 z-10 text-[10px] px-2 py-1 bg-red-100 text-red-700 rounded\'>Oferta</span>' : ''}
                    <div class="absolute inset-2 border border-gray-200 rounded-lg overflow-hidden">
                        <img src="${imagen}" alt="${producto.nombre}" class="w-full h-full object-cover" />
                    </div>
                </div>
                <div class="p-4 flex-1 flex flex-col">
                    <h3 class="text-sm font-semibold text-gray-900 mb-1 text-center">${producto.nombre}</h3>
                    ${descripcionCorta ? `<p class="text-gray-600 text-xs mb-3 line-clamp-2 text-center">${descripcionCorta}</p>` : ''}
                    <div class="mt-auto flex items-center justify-center gap-2">
                        ${tieneOferta ? '<span class="text-xs line-through text-gray-500">$' + formatearPrecio(precioBase) + '</span>' : ''}
                        <span class="px-4 py-2 bg-black text-white rounded text-lg font-bold">$${formatearPrecio(precio)}</span>
                    </div>
                </div>
            </div>
        `;
        contenedor.innerHTML += productoHTML;
    });
}

// Función para mostrar estado de carga
function mostrarCargando() {
    const contenedor = document.getElementById('productos-destacados');
    if (!contenedor) return;
    
    contenedor.innerHTML = `
        <div class="col-span-full flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <span class="ml-3 text-gray-600">Cargando productos...</span>
        </div>
    `;
}

// Función para mostrar errores
function mostrarError(mensaje) {
    const contenedor = document.getElementById('productos-destacados');
    if (!contenedor) return;
    
    contenedor.innerHTML = `
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

// Enviar mensaje de contacto
export async function enviarMensaje(event) {
    event.preventDefault();
    const form = event.target;

    const formData = new FormData(form);
    try {
        const result = await postData('/api/mensajes', {
            nombre: formData.get('nombre'),
            email: formData.get('email'),
            asunto: formData.get('asunto'),
            mensaje: formData.get('mensaje')
        });

        if (result) {
            mostrarNotificacion('Mensaje enviado', 'success');
            form.reset();
        } else {
            mostrarNotificacion('Error al enviar mensaje', 'error');
        }
    } catch (error) {
        console.error('Error al enviar mensaje:', error);
        mostrarNotificacion('Error de conexión', 'error');
    }
}

// Función para login
export async function login(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const formEncoded = new URLSearchParams();
        formEncoded.append('username', formData.get('email'));
        formEncoded.append('password', formData.get('password'));

        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            body: formEncoded
        });

        if (!response.ok) {
            throw new Error('Credenciales inválidas');
        }

        const data = await response.json();
        
        // Guardar token y datos del usuario
        localStorage.setItem('token', data.access_token);
        if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user));
            state.user = data.user;
        }
        state.token = data.access_token;

        mostrarNotificacion('Login exitoso', 'success');
        actualizarUI();
        
        // Redirigir según el rol del usuario
        if (data.user && data.user.rol === 'admin') {
            window.location.href = '/admin';
        } else {
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Error en login:', error);
        mostrarNotificacion('Error en el login', 'error');
    }
}

// Función para logout
export function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    state.token = null;
    state.user = null;
    actualizarUI();
}

// Función para actualizar la UI según el estado de autenticación
export function actualizarUI() {
    const loginBtn = document.getElementById('login-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const userInfo = document.getElementById('user-info');
    
    const isAdmin = state.user && (state.user.rol === 'admin' || state.user.role === 'admin' || state.user.rol === 'administrador' || state.user.role === 'administrador');
    if (state.token && state.user && !isAdmin) {
        if (loginBtn) loginBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'block';
        if (userInfo) {
            userInfo.style.display = 'block';
            userInfo.textContent = `Hola, ${state.user.nombre}`;
        }
    } else {
        if (loginBtn) loginBtn.style.display = 'block';
        if (logoutBtn) logoutBtn.style.display = 'none';
        if (userInfo) userInfo.style.display = 'none';
    }
    
    actualizarContadorCarrito();
}

// Función para actualizar el contador del carrito
export function actualizarContadorCarrito() {
    const contador = document.getElementById('carrito-contador');
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const totalItems = carrito.reduce((acc, item) => acc + item.cantidad, 0);
    if (contador) contador.textContent = totalItems;
}

// Función para mostrar notificaciones
export function mostrarNotificacion(mensaje, tipo = 'success') {
    const notificacion = document.getElementById('notificacion');
    if (!notificacion) return;

    notificacion.textContent = mensaje;
    notificacion.className = `fixed top-4 right-4 px-4 py-2 rounded shadow-lg text-white ${tipo === 'success' ? 'bg-green-600' : 'bg-red-600'}`;
    notificacion.style.display = 'block';

    setTimeout(() => {
        notificacion.style.display = 'none';
    }, 3000);
}

// Ver producto
window.verProducto = function(id) {
    window.location.href = `/productos/${id}`;
};

// Agregar al carrito (global)
window.agregarAlCarrito = async function(id) {
    try {
        const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
        const productoExistente = carrito.find(item => item.id === id);

        if (productoExistente) {
            productoExistente.cantidad += 1;
        } else {
            // Obtener detalles del producto para guardar info necesaria en el carrito
            try {
                const producto = await getData(`/api/productos/${id}`);
                const nombre = producto?.nombre || `Producto ${id}`;
    const precio_venta = Number(producto?.precio_final ?? producto?.precio_venta ?? producto?.precio ?? 0);
                const imagen_url = producto?.imagen_url || '/images/logos/herramientas.webp';
                carrito.push({ id, cantidad: 1, nombre, precio_venta, imagen_url });
            } catch (e) {
                console.warn('No se pudo obtener detalles del producto, usando datos mínimos:', e);
                carrito.push({ id, cantidad: 1 });
            }
        }

        localStorage.setItem('carrito', JSON.stringify(carrito));
        actualizarContadorCarrito();
        mostrarNotificacion('Producto agregado al carrito', 'success');
    } catch (error) {
        console.error('Error al agregar al carrito:', error);
        mostrarNotificacion('No se pudo agregar al carrito', 'error');
    }
};

// Exponer funciones necesarias
window.enviarMensaje = enviarMensaje;
window.cargarProductosDestacados = cargarProductosDestacados;
window.cargarProductosInicio = cargarProductosInicio;
window.login = login;
window.logout = logout;
window.actualizarUI = actualizarUI;
window.mostrarNotificacion = mostrarNotificacion;

// Inicialización
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        actualizarUI();
        if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
            cargarProductosDestacados();
            cargarProductosInicio();
        }
    });
} else {
    actualizarUI();
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        cargarProductosDestacados();
        cargarProductosInicio();
    }
}