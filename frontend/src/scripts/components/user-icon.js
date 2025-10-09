// Script para manejar la animación optimizada del icono de usuario con deslizamiento horizontal
document.addEventListener('DOMContentLoaded', function() {
    const userIconBtn = document.getElementById('userIconBtn');
    const userIconContainer = document.getElementById('userIconContainer');
    const loginButtonContainer = document.getElementById('loginButtonContainer');
    
    let isAnimating = false;
    let isLoginVisible = false;
    
    if (userIconBtn && loginButtonContainer && userIconContainer) {
        // Agregar estilos CSS para animaciones más fluidas
        const style = document.createElement('style');
        style.textContent = `
            #userIconContainer, #loginButtonContainer {
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }
            #userIconBtn {
                transition: transform 0.2s ease-in-out;
            }
            #userIconBtn:hover {
                transform: scale(1.1);
            }
            #loginButtonContainer a {
                transition: all 0.3s ease-in-out;
            }
            #loginButtonContainer a:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            }
        `;
        document.head.appendChild(style);
        
        // Función para mostrar/ocultar el botón de login con animación optimizada
        userIconBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // Evitar que el clic se propague al documento
            
            if (isAnimating) return; // Evitar múltiples clics durante la animación
            isAnimating = true;
            
            // Agregar efecto de rebote al icono
            userIconBtn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                userIconBtn.style.transform = '';
            }, 150);
            
            if (!isLoginVisible) {
                // Deslizar el icono hacia la izquierda con fade out
                userIconContainer.style.transform = 'translateX(-100%) scale(0.8)';
                userIconContainer.style.opacity = '0';
                
                setTimeout(() => {
                    userIconContainer.style.display = 'none';
                    
                    // Mostrar el botón de login desde la derecha
                    loginButtonContainer.style.display = 'block';
                    loginButtonContainer.style.transform = 'translateX(100%) scale(0.8)';
                    loginButtonContainer.style.opacity = '0';
                    
                    // Forzar reflow
                    loginButtonContainer.offsetHeight;
                    
                    // Animar entrada
                    loginButtonContainer.style.transform = 'translateX(0) scale(1)';
                    loginButtonContainer.style.opacity = '1';
                    
                    isLoginVisible = true;
                    isAnimating = false;
                }, 200);
            } else {
                // Deslizar el botón de login hacia la derecha con fade out
                loginButtonContainer.style.transform = 'translateX(100%) scale(0.8)';
                loginButtonContainer.style.opacity = '0';
                
                setTimeout(() => {
                    loginButtonContainer.style.display = 'none';
                    
                    // Mostrar el icono desde la izquierda
                    userIconContainer.style.display = 'block';
                    userIconContainer.style.transform = 'translateX(-100%) scale(0.8)';
                    userIconContainer.style.opacity = '0';
                    
                    // Forzar reflow
                    userIconContainer.offsetHeight;
                    
                    // Animar entrada
                    userIconContainer.style.transform = 'translateX(0) scale(1)';
                    userIconContainer.style.opacity = '1';
                    
                    isLoginVisible = false;
                    isAnimating = false;
                }, 200);
            }
        });
        
        // Cerrar al hacer clic fuera (solo si el botón de login está visible)
        document.addEventListener('click', function(e) {
            if (isLoginVisible && !loginButtonContainer.contains(e.target) && !userIconBtn.contains(e.target)) {
                if (!isAnimating) {
                    userIconBtn.click(); // Simular clic para cerrar
                }
            }
        });
        
        // Manejar tecla Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isLoginVisible && !isAnimating) {
                userIconBtn.click(); // Simular clic para cerrar
            }
        });
        
        // Inicializar estado
        loginButtonContainer.style.display = 'none';
        userIconContainer.style.display = 'block';
        userIconContainer.style.transform = 'translateX(0) scale(1)';
        userIconContainer.style.opacity = '1';
    }
});

// Exportar funciones si se necesitan en otros módulos
export function toggleUserIcon() {
    const userIconBtn = document.getElementById('userIconBtn');
    if (userIconBtn) {
        userIconBtn.click();
    }
}

export function hideLoginButton() {
    const userIconBtn = document.getElementById('userIconBtn');
    const loginButtonContainer = document.getElementById('loginButtonContainer');
    
    if (loginButtonContainer && loginButtonContainer.style.display !== 'none') {
        userIconBtn.click();
    }
}