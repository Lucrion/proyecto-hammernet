// Estado global
const state = {
    token: localStorage.getItem('token'),
    user: JSON.parse(localStorage.getItem('user')),
    carrito: JSON.parse(localStorage.getItem('carrito')) || [],
    productos: []
};

// Configuración de la API usando la misma lógica que config.js
const isDevelopment = typeof window !== 'undefined' 
    ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    : false;

// Obtener variables de entorno de Astro (disponibles como import.meta.env en el cliente)
const getEnvVar = (name) => {
    // En el contexto del navegador, las variables están disponibles como window.__ENV__ si se configuran
    if (typeof window !== 'undefined' && window.__ENV__) {
        return window.__ENV__[name];
    }
    return undefined;
};

const API_URL = isDevelopment 
    ? getEnvVar('PUBLIC_API_URL')
    : getEnvVar('PUBLIC_API_URL_PRODUCTION');

const API_TIMEOUT = parseInt(getEnvVar('PUBLIC_API_TIMEOUT'));

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
async function cargarProductosDestacados() {
    try {
        // Verificar si hay token de autenticación
        const token = localStorage.getItem('token');
        if (!token) {
            console.warn('No hay token de autenticación, redirigiendo al login');
            window.location.href = '/login';
            return;
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);
        
        // Cargar datos de productos, categorías e inventario por separado con autenticación
        const [productosResponse, categoriasResponse, inventarioResponse] = await Promise.all([
            fetch(`${API_URL}/productos/`, {
                signal: controller.signal,
                method: 'GET',
                headers: { 
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            }),
            fetch(`${API_URL}/categorias/`, {
                signal: controller.signal,
                method: 'GET',
                headers: { 
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            }),
            fetch(`${API_URL}/productos/inventario`, {
                signal: controller.signal,
                method: 'GET',
                headers: { 
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            })
        ]);
        
        clearTimeout(timeoutId);
        
        // Verificar si alguna respuesta indica token expirado
        if (productosResponse.status === 401 || categoriasResponse.status === 401 || inventarioResponse.status === 401) {
            console.warn('Token expirado, redirigiendo al login');
            localStorage.removeItem('token');
            window.location.href = '/login';
            return;
        }
        
        if (!productosResponse.ok || !categoriasResponse.ok || !inventarioResponse.ok) {
            throw new Error('Error al cargar datos');
        }
        
        const productos = await productosResponse.json();
        const categorias = await categoriasResponse.json();
        const inventario = await inventarioResponse.json();
        
        // Combinar datos para crear productos completos
        const productosCompletos = productos.map(producto => {
            const categoria = categorias.find(c => c.id_categoria === producto.id_categoria);
            const stock = inventario.find(i => i.id_producto === producto.id_producto);
            
            return {
                id: producto.id_producto,
                nombre: producto.nombre,
                descripcion: producto.descripcion,
                imagen: '/logo.webp', // Imagen por defecto
                precio: stock ? stock.precio : 0,
                stock: stock ? stock.cantidad_disponible : 0,
                categoria: categoria ? categoria.nombre : 'Sin categoría'
            };
        }).filter(p => p.stock > 0); // Solo productos con stock
        
        // Guardar productos en el estado global
        state.productos = productosCompletos;
        
        const contenedor = document.getElementById('productos-destacados');
        if (!contenedor) {
            console.error('Elemento productos-destacados no encontrado');
            return;
        }
        
        contenedor.innerHTML = '';
        
        // Limitar a solo 4 productos destacados
        const productosDestacados = productosCompletos.slice(0, 4);
        
        if (productosDestacados.length === 0) {
            contenedor.innerHTML = `
                <div class="col-span-full text-center py-8">
                    <p class="text-gray-500">No hay productos disponibles en este momento.</p>
                </div>
            `;
            return;
        }
        
        productosDestacados.forEach(producto => {
            const card = document.createElement('div');
            card.className = 'bg-white rounded-xl shadow-lg overflow-hidden transform hover:scale-105 transition-all duration-300';
            card.setAttribute('data-aos', 'fade-up');
            
            card.innerHTML = `
                <div class="relative h-48 overflow-hidden bg-gray-100 flex items-center justify-center">
                    <img class="max-h-full max-w-full object-contain transform hover:scale-110 transition-all duration-500" 
                         src="${producto.imagen}" 
                         alt="${producto.nombre}"
                         onerror="this.src='/logo.webp'; this.onerror=null;">
                </div>
                <div class="p-4">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">${producto.nombre}</h3>
                    <p class="text-gray-600 text-sm mb-2">${producto.descripcion || ''}</p>
                    <div class="flex items-center justify-between">
                        <span class="text-blue-600 font-bold">$${formatearPrecio(producto.precio)}</span>
                        <span class="text-sm ${producto.stock > 0 ? 'text-green-600' : 'text-red-600'}">
                            ${producto.stock > 0 ? 'En stock' : 'Agotado'}
                        </span>
                    </div>
                </div>
            `;
            
            // Hacer la tarjeta clickeable
            card.style.cursor = 'pointer';
            card.addEventListener('click', () => {
                const slug = producto.nombre.toLowerCase().replace(/\s+/g, '-');
                window.location.href = `/productos/${slug}`;
            });
            
            contenedor.appendChild(card);
        });
    } catch (error) {
        console.error('Error al cargar productos destacados:', error);
        const contenedor = document.getElementById('productos-destacados');
        if (contenedor) {
            let errorMessage = 'Error al cargar los productos destacados.';
            
            if (error.name === 'AbortError') {
                errorMessage = 'Tiempo de espera agotado al cargar productos.';
            } else if (error.message.includes('Failed to fetch')) {
                errorMessage = 'No se pudo conectar con el servidor.';
            }
            
            contenedor.innerHTML = `
                <div class="col-span-full text-center py-8">
                    <p class="text-red-500">${errorMessage}</p>
                    <button onclick="cargarProductosDestacados()" class="mt-2 text-blue-600 hover:text-blue-800 underline">
                        Intentar de nuevo
                    </button>
                </div>
            `;
        }
    }
}

// Función para enviar mensaje de contacto
async function enviarMensaje(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);
        
        const response = await fetch(`${API_URL}/mensajes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nombre: formData.get('nombre'),
                apellido: formData.get('apellido'),
                email: formData.get('email'),
                asunto: formData.get('asunto'),
                mensaje: formData.get('mensaje')
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            form.reset();
            mostrarNotificacion('Mensaje enviado correctamente');
        } else {
            throw new Error('Error al enviar el mensaje');
        }
    } catch (error) {
        console.error('Error:', error);
        let errorMessage = 'Error al enviar el mensaje';
        
        if (error.name === 'AbortError') {
            errorMessage = 'Tiempo de espera agotado';
        }
        
        mostrarNotificacion(errorMessage, 'error');
    }
}

// Función para iniciar sesión
async function login(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);
        
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: formData.get('username'),
                password: formData.get('password')
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        const data = await response.json();
        
        if (response.ok) {
            // Guardar token y datos del usuario
            state.token = data.access_token;
            state.user = {
                id: data.id,
                nombre: data.nombre,
                username: data.username,
                role: data.role
            };
            
            localStorage.setItem('token', state.token);
            localStorage.setItem('user', JSON.stringify(state.user));
            
            // Actualizar UI
            actualizarUI();
            mostrarNotificacion('Sesión iniciada correctamente');
        } else {
            throw new Error(data.detail || 'Error al iniciar sesión');
        }
    } catch (error) {
        console.error('Error:', error);
        let errorMessage = 'Error al iniciar sesión';
        
        if (error.name === 'AbortError') {
            errorMessage = 'Tiempo de espera agotado';
        }
        
        mostrarNotificacion(errorMessage, 'error');
    }
}

// Función para cerrar sesión
function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    actualizarUI();
    mostrarNotificacion('Sesión cerrada correctamente');
    // Redirigir a la página de inicio
    window.location.href = '/';
}

// Función para actualizar la UI según el estado de autenticación
function actualizarUI() {
    const userSection = document.getElementById('user-section');
    const adminSection = document.getElementById('admin-section');
    
    // Ocultar secciones de usuario y admin en todas las páginas excepto login
    if (window.location.pathname !== '/login') {
        if (userSection) userSection.classList.add('hidden');
        if (adminSection) adminSection.classList.add('hidden');
        return;
    }
    
    // Solo mostrar elementos de autenticación en la página de login
    if (state.user && window.location.pathname === '/login') {
        // Usuario autenticado
        if (userSection) {
            userSection.classList.remove('hidden');
            const userName = document.getElementById('user-name');
            if (userName) userName.textContent = state.user.nombre;
        }
        
        // Mostrar panel de admin si el rol es admin
        if (adminSection && state.user.role === 'admin') {
            adminSection.classList.remove('hidden');
        }
    } else {
        // Usuario no autenticado
        if (userSection) userSection.classList.add('hidden');
        if (adminSection) adminSection.classList.add('hidden');
    }
}

// Función para actualizar el contador del carrito (deshabilitada)
function actualizarContadorCarrito() {
    const contador = document.getElementById('carrito-contador');
    if (contador) {
        // Ocultar el contador del carrito
        contador.classList.add('hidden');
    }
    
    // Ocultar cualquier elemento relacionado con el carrito
    const elementosCarrito = document.querySelectorAll('.carrito-elemento');
    elementosCarrito.forEach(elemento => {
        elemento.classList.add('hidden');
    });
}

// Función para mostrar notificaciones
function mostrarNotificacion(mensaje, tipo = 'success') {
    const notificacion = document.createElement('div');
    notificacion.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50 ${tipo === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white`;
    notificacion.textContent = mensaje;
    
    document.body.appendChild(notificacion);
    
    setTimeout(() => {
        notificacion.classList.add('opacity-0', 'transition-opacity', 'duration-500');
        setTimeout(() => {
            if (document.body.contains(notificacion)) {
                document.body.removeChild(notificacion);
            }
        }, 500);
    }, 3000);
}

// Exponer funciones al objeto window para acceso desde scripts inline
window.enviarMensaje = enviarMensaje;
window.cargarProductosDestacados = cargarProductosDestacados;
window.login = login;
window.logout = logout;
window.actualizarUI = actualizarUI;
window.mostrarNotificacion = mostrarNotificacion;

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Cargar productos destacados si estamos en la página principal
        if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
            cargarProductosDestacados();
        }
        
        // Actualizar UI de autenticación
        actualizarUI();
    });
} else {
    // El DOM ya está cargado
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        cargarProductosDestacados();
    }
    actualizarUI();
}
