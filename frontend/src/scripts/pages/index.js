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

        // Verificar disponibilidad del servidor
        const serverStatus = await checkServerAvailability();
        if (!serverStatus.available) {
            mostrarError('El servidor no está disponible. Por favor, intenta más tarde.');
            return;
        }

        mostrarCargando();

        const response = await getData('/api/productos/catalogo');
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const productos = await response.json();
        
        if (!Array.isArray(productos)) {
            throw new Error('La respuesta no es un array válido');
        }

        // Filtrar productos destacados (primeros 8)
        const productosDestacados = productos.slice(0, 8);
        state.productos = productosDestacados;
        
        mostrarProductosDestacados(productosDestacados);
        
    } catch (error) {
        console.error('Error al cargar productos destacados:', error);
        handleApiError(error, 'cargar productos destacados');
        mostrarError('Error al cargar los productos destacados');
    }
}

// Función para mostrar productos destacados
function mostrarProductosDestacados(productos) {
    const contenedor = document.getElementById('productos-destacados');
    if (!contenedor) return;

    contenedor.innerHTML = '';

    productos.forEach(producto => {
        const productoHTML = `
            <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300" data-aos="fade-up">
                <div class="aspect-w-1 aspect-h-1">
                    <img src="${producto.imagen || '/images/placeholder-product.jpg'}" 
                         alt="${producto.nombre}" 
                         class="w-full h-48 object-cover">
                </div>
                <div class="p-4">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">${producto.nombre}</h3>
                    <p class="text-gray-600 text-sm mb-3 line-clamp-2">${producto.descripcion || 'Sin descripción'}</p>
                    <div class="flex justify-between items-center">
                        <span class="text-xl font-bold text-blue-600">$${formatearPrecio(producto.precio)}</span>
                        <button onclick="verProducto(${producto.id})" 
                                class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">
                            Ver más
                        </button>
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

// Función para enviar mensaje de contacto
export async function enviarMensaje(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    const mensaje = {
        nombre: formData.get('nombre'),
        email: formData.get('email'),
        asunto: formData.get('asunto'),
        mensaje: formData.get('mensaje')
    };

    try {
        const response = await postData('/api/mensajes', mensaje);
        
        if (response.ok) {
            mostrarNotificacion('Mensaje enviado correctamente', 'success');
            form.reset();
        } else {
            throw new Error('Error al enviar el mensaje');
        }
    } catch (error) {
        console.error('Error al enviar mensaje:', error);
        mostrarNotificacion('Error al enviar el mensaje', 'error');
    }
}

// Función para login
export async function login(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    const credentials = {
        email: formData.get('email'),
        password: formData.get('password')
    };

    try {
        const response = await postData('/api/auth/login', credentials);
        
        if (response.ok) {
            const data = await response.json();
            
            // Guardar token y datos del usuario
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            state.token = data.access_token;
            state.user = data.user;
            
            mostrarNotificacion('Login exitoso', 'success');
            actualizarUI();
            
            // Redirigir según el rol del usuario
            if (data.user.rol === 'admin') {
                window.location.href = '/admin';
            } else {
                window.location.href = '/';
            }
        } else {
            throw new Error('Credenciales inválidas');
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
    
    if (state.token && state.user) {
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

// Función para actualizar contador del carrito
export function actualizarContadorCarrito() {
    const contador = document.getElementById('carrito-contador');
    if (contador) {
        const totalItems = state.carrito.reduce((total, item) => total + item.cantidad, 0);
        contador.textContent = totalItems;
        contador.style.display = totalItems > 0 ? 'block' : 'none';
    }
}

// Función para mostrar notificaciones
export function mostrarNotificacion(mensaje, tipo = 'success') {
    const notificacion = document.createElement('div');
    notificacion.className = `fixed top-4 right-4 p-4 rounded-lg text-white z-50 ${
        tipo === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;
    notificacion.textContent = mensaje;
    
    document.body.appendChild(notificacion);
    
    setTimeout(() => {
        notificacion.remove();
    }, 3000);
}

// Función para ver producto (global para onclick)
window.verProducto = function(id) {
    window.location.href = `/productos/${id}`;
};

// Exportar funciones globales para compatibilidad
window.enviarMensaje = enviarMensaje;
window.cargarProductosDestacados = cargarProductosDestacados;
window.login = login;
window.logout = logout;
window.actualizarUI = actualizarUI;
window.mostrarNotificacion = mostrarNotificacion;

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        actualizarUI();
        // Solo cargar productos si estamos en la página principal
        if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
            cargarProductosDestacados();
        }
    });
} else {
    actualizarUI();
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        cargarProductosDestacados();
    }
}