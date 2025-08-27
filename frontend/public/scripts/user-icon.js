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
                
                // Deslizar el botón de login desde la derecha con fade in
                setTimeout(() => {
                    loginButtonContainer.style.transform = 'translateX(0) scale(1)';
                    loginButtonContainer.style.opacity = '1';
                }, 100);
                
                isLoginVisible = true;
            } else {
                // Deslizar el botón de login hacia la derecha con fade out
                loginButtonContainer.style.transform = 'translateX(100%) scale(0.8)';
                loginButtonContainer.style.opacity = '0';
                
                // Deslizar el icono de vuelta a su posición con fade in
                setTimeout(() => {
                    userIconContainer.style.transform = 'translateX(0) scale(1)';
                    userIconContainer.style.opacity = '1';
                }, 100);
                
                isLoginVisible = false;
            }
            
            // Permitir nuevas animaciones después de que termine la actual
            setTimeout(() => {
                isAnimating = false;
            }, 400); // Tiempo ajustado para la nueva duración
        });
        
        // Cerrar el menú cuando se hace clic fuera de él con animación optimizada
        document.addEventListener('click', function(e) {
            if (isLoginVisible && !userIconBtn.contains(e.target) && 
                !loginButtonContainer.contains(e.target) && 
                !userIconContainer.contains(e.target)) {
                
                if (isAnimating) return;
                isAnimating = true;
                
                // Deslizar el botón de login hacia la derecha con fade out
                loginButtonContainer.style.transform = 'translateX(100%) scale(0.8)';
                loginButtonContainer.style.opacity = '0';
                
                // Deslizar el icono de vuelta a su posición con fade in
                setTimeout(() => {
                    userIconContainer.style.transform = 'translateX(0) scale(1)';
                    userIconContainer.style.opacity = '1';
                }, 100);
                
                isLoginVisible = false;
                
                setTimeout(() => {
                    isAnimating = false;
                }, 400);
            }
        });
        
        // Agregar efecto de hover mejorado al icono de usuario
        userIconBtn.addEventListener('mouseenter', function() {
            if (!isAnimating && !isLoginVisible) {
                this.style.transform = 'scale(1.1) rotate(5deg)';
            }
        });
        
        userIconBtn.addEventListener('mouseleave', function() {
            if (!isAnimating && !isLoginVisible) {
                this.style.transform = 'scale(1) rotate(0deg)';
            }
        });
    }
});