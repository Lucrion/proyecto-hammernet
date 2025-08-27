// Importar AOS para animaciones al hacer scroll
import AOS from 'aos';
import 'aos/dist/aos.css';

// Inicializar AOS
AOS.init({
    duration: 1000,
    once: true
});

// Función para cargar productos destacados
async function cargarProductosDestacados() {
    try {
        const response = await fetch('http://localhost:8000/api/productos/destacados');
        const productos = await response.json();
        
        const contenedor = document.getElementById('productos-destacados');
        contenedor.innerHTML = '';
        
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
                    <p class="text-gray-600 text-sm mb-2">${producto.descripcion}</p>
                    <div class="flex items-center justify-between">
                        <span class="text-blue-600 font-bold">$${producto.precio}</span>
                        <button onclick="agregarAlCarrito(${producto.id})" 
                                class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-300">
                            Agregar
                        </button>
                    </div>
                </div>
            `;
            
            contenedor.appendChild(card);
        });
    } catch (error) {
        console.error('Error al cargar productos destacados:', error);
        const contenedor = document.getElementById('productos-destacados');
        contenedor.innerHTML = `
            <div class="col-span-full text-center py-8">
                <p class="text-red-500">Error al cargar los productos destacados. Por favor, intente más tarde.</p>
            </div>
        `;
    }
}

// Función para agregar al carrito
function agregarAlCarrito(productoId) {
    // Animación del botón
    const btn = event.target;
    btn.classList.add('animate-pulse');
    
    setTimeout(() => {
        btn.classList.remove('animate-pulse');
        // Aquí iría la lógica para agregar al carrito
        console.log('Producto agregado:', productoId);
    }, 500);
}

// Cargar productos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    cargarProductosDestacados();
});

// Animación suave para el scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});