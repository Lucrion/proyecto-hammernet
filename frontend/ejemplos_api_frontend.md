# Ejemplos de Consumo de API desde el Frontend

Este documento muestra ejemplos prácticos de cómo consumir la API de la ferretería desde el frontend usando JavaScript.

## 1. Configuración Base

### Configuración de API (config.js)
```javascript
// Detección automática del entorno
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// URL base de la API
export const API_URL = isDevelopment 
    ? 'http://localhost:8000/api' 
    : 'https://tu-dominio.com/api';

// Configuración CORS
export const corsConfig = {
    mode: 'cors',
    credentials: 'omit'
};

// Timeout para requests
export const API_TIMEOUT = 10000;
```

### Funciones de Utilidad (api.js)
```javascript
// Función para hacer requests autenticados
export async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('token');
    
    const config = {
        ...corsConfig,
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_URL}${url}`, config);
        
        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
            return null;
        }
        
        return response;
    } catch (error) {
        console.error('Error en request:', error);
        throw error;
    }
}
```

## 2. Autenticación

### Login de Usuario
```javascript
async function login(email, password) {
    try {
        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                username: email,
                password: password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            window.location.href = '/admin';
        } else {
            const error = await response.json();
            alert('Error de login: ' + error.detail);
        }
    } catch (error) {
        console.error('Error en login:', error);
        alert('Error de conexión');
    }
}

// Uso del login
document.getElementById('loginForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    login(email, password);
});
```

### Verificación de Autenticación
```javascript
function verificarAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Verificar en cada página protegida
document.addEventListener('DOMContentLoaded', () => {
    if (!verificarAuth()) return;
    // Continuar con la lógica de la página
});
```

## 3. Operaciones CRUD - Productos

### Obtener Lista de Productos
```javascript
async function cargarProductos(filtros = {}) {
    try {
        // Construir URL con parámetros
        let url = '/productos?';
        const params = new URLSearchParams();
        
        if (filtros.skip) params.append('skip', filtros.skip);
        if (filtros.limit) params.append('limit', filtros.limit);
        if (filtros.categoria_id) params.append('categoria_id', filtros.categoria_id);
        if (filtros.proveedor_id) params.append('proveedor_id', filtros.proveedor_id);
        
        url += params.toString();
        
        const response = await fetchWithAuth(url);
        
        if (response && response.ok) {
            const productos = await response.json();
            mostrarProductos(productos);
            return productos;
        }
    } catch (error) {
        console.error('Error al cargar productos:', error);
        alert('Error al cargar productos');
    }
}

// Ejemplo de uso con filtros
cargarProductos({
    skip: 0,
    limit: 10,
    categoria_id: 1
});
```

### Crear Nuevo Producto
```javascript
async function crearProducto(datosProducto) {
    try {
        const producto = {
            nombre: datosProducto.nombre,
            descripcion: datosProducto.descripcion,
            precio: parseInt(datosProducto.precio),
            stock: parseInt(datosProducto.stock) || 0,
            id_categoria: parseInt(datosProducto.id_categoria) || null,
            stock_minimo: parseInt(datosProducto.stock_minimo) || 5
        };
        
        const response = await fetchWithAuth('/productos', {
            method: 'POST',
            body: JSON.stringify(producto)
        });
        
        if (response && response.ok) {
            const nuevoProducto = await response.json();
            alert('Producto creado exitosamente');
            return nuevoProducto;
        } else {
            const error = await response.json();
            alert('Error al crear producto: ' + error.detail);
        }
    } catch (error) {
        console.error('Error al crear producto:', error);
        alert('Error de conexión al crear producto');
    }
}

// Ejemplo de uso desde un formulario
document.getElementById('formProducto').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    const datosProducto = {
        nombre: formData.get('nombre'),
        descripcion: formData.get('descripcion'),
        precio: formData.get('precio'),
        stock: formData.get('stock'),
        id_categoria: formData.get('id_categoria'),
        stock_minimo: formData.get('stock_minimo')
    };
    
    await crearProducto(datosProducto);
});
```

### Actualizar Producto
```javascript
async function actualizarProducto(id, datosProducto) {
    try {
        const response = await fetchWithAuth(`/productos/${id}`, {
            method: 'PUT',
            body: JSON.stringify(datosProducto)
        });
        
        if (response && response.ok) {
            const productoActualizado = await response.json();
            alert('Producto actualizado exitosamente');
            return productoActualizado;
        } else {
            const error = await response.json();
            alert('Error al actualizar producto: ' + error.detail);
        }
    } catch (error) {
        console.error('Error al actualizar producto:', error);
        alert('Error de conexión al actualizar producto');
    }
}
```

### Eliminar Producto
```javascript
async function eliminarProducto(id) {
    if (!confirm('¿Estás seguro de que quieres eliminar este producto?')) {
        return;
    }
    
    try {
        const response = await fetchWithAuth(`/productos/${id}`, {
            method: 'DELETE'
        });
        
        if (response && response.ok) {
            alert('Producto eliminado exitosamente');
            // Recargar la lista
            cargarProductos();
        } else {
            const error = await response.json();
            alert('Error al eliminar producto: ' + error.detail);
        }
    } catch (error) {
        console.error('Error al eliminar producto:', error);
        alert('Error de conexión al eliminar producto');
    }
}
```

## 4. Operaciones con Categorías

### Cargar Categorías para Select
```javascript
async function cargarCategorias() {
    try {
        const response = await fetchWithAuth('/categorias');
        
        if (response && response.ok) {
            const categorias = await response.json();
            
            // Llenar select de categorías
            const selectCategoria = document.getElementById('id_categoria');
            selectCategoria.innerHTML = '<option value="">Seleccionar categoría</option>';
            
            categorias.forEach(categoria => {
                const option = new Option(categoria.nombre, categoria.id_categoria);
                selectCategoria.add(option);
            });
            
            return categorias;
        }
    } catch (error) {
        console.error('Error al cargar categorías:', error);
    }
}
```

### Crear Nueva Categoría
```javascript
async function crearCategoria(nombre, descripcion = '') {
    try {
        const categoria = {
            nombre: nombre,
            descripcion: descripcion
        };
        
        const response = await fetchWithAuth('/categorias', {
            method: 'POST',
            body: JSON.stringify(categoria)
        });
        
        if (response && response.ok) {
            const nuevaCategoria = await response.json();
            alert('Categoría creada exitosamente');
            // Recargar categorías
            cargarCategorias();
            return nuevaCategoria;
        } else {
            const error = await response.json();
            alert('Error al crear categoría: ' + error.detail);
        }
    } catch (error) {
        console.error('Error al crear categoría:', error);
        alert('Error de conexión al crear categoría');
    }
}
```

## 5. Gestión de Inventario

### Obtener Inventario
```javascript
async function cargarInventario() {
    try {
        const response = await fetchWithAuth('/inventario');
        
        if (response && response.ok) {
            const inventario = await response.json();
            mostrarInventario(inventario);
            return inventario;
        }
    } catch (error) {
        console.error('Error al cargar inventario:', error);
        alert('Error al cargar inventario');
    }
}

function mostrarInventario(inventario) {
    const tabla = document.getElementById('tablaInventario');
    tabla.innerHTML = '';
    
    inventario.forEach(item => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td>${item.id_producto}</td>
            <td>${item.nombre_producto || 'N/A'}</td>
            <td>${item.cantidad_actual}</td>
            <td>${item.stock_minimo}</td>
            <td class="${item.cantidad_actual <= item.stock_minimo ? 'text-red-600' : 'text-green-600'}">
                ${item.cantidad_actual <= item.stock_minimo ? 'Stock Bajo' : 'OK'}
            </td>
            <td>
                <button onclick="actualizarStock(${item.id_producto})" class="btn-primary">
                    Actualizar Stock
                </button>
            </td>
        `;
        tabla.appendChild(fila);
    });
}
```

### Actualizar Stock
```javascript
async function actualizarStock(idProducto) {
    const nuevaCantidad = prompt('Ingresa la nueva cantidad:');
    if (!nuevaCantidad || isNaN(nuevaCantidad)) return;
    
    try {
        const datosInventario = {
            id_producto: idProducto,
            cantidad_actual: parseInt(nuevaCantidad),
            stock_minimo: 5 // valor por defecto
        };
        
        const response = await fetchWithAuth('/inventario', {
            method: 'POST',
            body: JSON.stringify(datosInventario)
        });
        
        if (response && response.ok) {
            alert('Stock actualizado exitosamente');
            cargarInventario(); // Recargar
        } else {
            const error = await response.json();
            alert('Error al actualizar stock: ' + error.detail);
        }
    } catch (error) {
        console.error('Error al actualizar stock:', error);
        alert('Error de conexión al actualizar stock');
    }
}
```

## 6. Sistema de Mensajes

### Obtener Mensajes
```javascript
async function cargarMensajes() {
    try {
        const response = await fetchWithAuth('/mensajes');
        
        if (response && response.ok) {
            const mensajes = await response.json();
            mostrarMensajes(mensajes);
            return mensajes;
        }
    } catch (error) {
        console.error('Error al cargar mensajes:', error);
        alert('Error al cargar mensajes');
    }
}

function mostrarMensajes(mensajes) {
    const contenedor = document.getElementById('listaMensajes');
    contenedor.innerHTML = '';
    
    mensajes.forEach(mensaje => {
        const div = document.createElement('div');
        div.className = `mensaje ${mensaje.leido ? 'leido' : 'no-leido'}`;
        div.innerHTML = `
            <div class="mensaje-header">
                <strong>${mensaje.nombre}</strong>
                <span class="email">${mensaje.email}</span>
                <span class="fecha">${new Date(mensaje.fecha_envio).toLocaleDateString()}</span>
            </div>
            <div class="mensaje-asunto">
                <strong>Asunto:</strong> ${mensaje.asunto}
            </div>
            <div class="mensaje-contenido">
                ${mensaje.mensaje}
            </div>
            <div class="mensaje-acciones">
                ${!mensaje.leido ? `<button onclick="marcarComoLeido(${mensaje.id_mensaje})">Marcar como leído</button>` : ''}
                <button onclick="eliminarMensaje(${mensaje.id_mensaje})">Eliminar</button>
            </div>
        `;
        contenedor.appendChild(div);
    });
}
```

### Marcar Mensaje como Leído
```javascript
async function marcarComoLeido(idMensaje) {
    try {
        const response = await fetchWithAuth(`/mensajes/${idMensaje}`, {
            method: 'PUT',
            body: JSON.stringify({ leido: true })
        });
        
        if (response && response.ok) {
            cargarMensajes(); // Recargar mensajes
        } else {
            const error = await response.json();
            alert('Error al marcar mensaje: ' + error.detail);
        }
    } catch (error) {
        console.error('Error al marcar mensaje:', error);
        alert('Error de conexión');
    }
}
```

## 7. Manejo de Errores Avanzado

### Función de Manejo de Errores
```javascript
export function handleApiError(error, context = '') {
    console.error(`Error en ${context}:`, error);
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        return 'Error de conexión. Verifica tu conexión a internet.';
    }
    
    if (error.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
        return 'Sesión expirada. Redirigiendo al login...';
    }
    
    if (error.status === 403) {
        return 'No tienes permisos para realizar esta acción.';
    }
    
    if (error.status === 404) {
        return 'Recurso no encontrado.';
    }
    
    if (error.status >= 500) {
        return 'Error del servidor. Intenta más tarde.';
    }
    
    return error.message || 'Error desconocido';
}
```

### Uso del Manejo de Errores
```javascript
async function operacionConManejodeErrores() {
    try {
        const response = await fetchWithAuth('/productos');
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error en la operación');
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        const mensaje = handleApiError(error, 'cargar productos');
        alert(mensaje);
        return null;
    }
}
```

## 8. Paginación y Filtros

### Sistema de Paginación
```javascript
class PaginadorProductos {
    constructor() {
        this.paginaActual = 0;
        this.productosPorPagina = 10;
        this.totalProductos = 0;
    }
    
    async cargarPagina(filtros = {}) {
        const params = {
            skip: this.paginaActual * this.productosPorPagina,
            limit: this.productosPorPagina,
            ...filtros
        };
        
        const productos = await cargarProductos(params);
        this.actualizarControles();
        return productos;
    }
    
    siguientePagina() {
        this.paginaActual++;
        this.cargarPagina();
    }
    
    paginaAnterior() {
        if (this.paginaActual > 0) {
            this.paginaActual--;
            this.cargarPagina();
        }
    }
    
    actualizarControles() {
        const desde = this.paginaActual * this.productosPorPagina + 1;
        const hasta = Math.min(desde + this.productosPorPagina - 1, this.totalProductos);
        
        document.getElementById('mostrandoDesde').textContent = desde;
        document.getElementById('mostrandoHasta').textContent = hasta;
        document.getElementById('totalProductos').textContent = this.totalProductos;
        
        document.getElementById('btnAnterior').disabled = this.paginaActual === 0;
        document.getElementById('btnSiguiente').disabled = hasta >= this.totalProductos;
    }
}

// Uso del paginador
const paginador = new PaginadorProductos();
document.getElementById('btnSiguiente').addEventListener('click', () => paginador.siguientePagina());
document.getElementById('btnAnterior').addEventListener('click', () => paginador.paginaAnterior());
```

## 9. Validaciones del Frontend

### Validación de Formularios
```javascript
function validarProducto(datos) {
    const errores = [];
    
    if (!datos.nombre || datos.nombre.trim().length < 2) {
        errores.push('El nombre debe tener al menos 2 caracteres');
    }
    
    if (!datos.precio || isNaN(datos.precio) || datos.precio <= 0) {
        errores.push('El precio debe ser un número mayor a 0');
    }
    
    if (datos.stock && (isNaN(datos.stock) || datos.stock < 0)) {
        errores.push('El stock debe ser un número mayor o igual a 0');
    }
    
    return errores;
}

// Uso en el formulario
document.getElementById('formProducto').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const datos = {
        nombre: formData.get('nombre'),
        precio: formData.get('precio'),
        stock: formData.get('stock')
    };
    
    const errores = validarProducto(datos);
    
    if (errores.length > 0) {
        alert('Errores de validación:\n' + errores.join('\n'));
        return;
    }
    
    // Continuar con el envío
    crearProducto(datos);
});
```

## 10. Inicialización de Página

### Patrón de Inicialización Completo
```javascript
class AdminProductos {
    constructor() {
        this.categorias = [];
        this.proveedores = [];
        this.paginador = new PaginadorProductos();
    }
    
    async inicializar() {
        // Verificar autenticación
        if (!verificarAuth()) return;
        
        try {
            // Cargar datos iniciales en paralelo
            await Promise.all([
                this.cargarCategorias(),
                this.cargarProveedores(),
                this.paginador.cargarPagina()
            ]);
            
            // Configurar event listeners
            this.configurarEventListeners();
            
            console.log('Página inicializada correctamente');
        } catch (error) {
            console.error('Error al inicializar página:', error);
            alert('Error al cargar la página');
        }
    }
    
    configurarEventListeners() {
        // Botones principales
        document.getElementById('btnNuevoProducto').addEventListener('click', () => this.abrirModalNuevo());
        document.getElementById('btnFiltrar').addEventListener('click', () => this.aplicarFiltros());
        
        // Formularios
        document.getElementById('formProducto').addEventListener('submit', (e) => this.guardarProducto(e));
        
        // Modales
        this.configurarModales();
    }
    
    // ... resto de métodos
}

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    const admin = new AdminProductos();
    admin.inicializar();
});
```

Estos ejemplos muestran patrones completos y reutilizables para consumir la API de la ferretería desde el frontend, incluyendo manejo de errores, validaciones, paginación y buenas prácticas de JavaScript moderno.