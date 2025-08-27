// Funciones para el manejo del formulario de contacto
import { API_URL } from './config.js';

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contactForm');
    const charCount = document.getElementById('charCount');
    const mensajeTextarea = document.getElementById('mensaje');
    
    // Actualizar contador de caracteres
    if (mensajeTextarea && charCount) {
        mensajeTextarea.addEventListener('input', function() {
            const currentLength = mensajeTextarea.value.length;
            charCount.textContent = `${currentLength}/500`;
        });
    }
    
    // Manejar envío del formulario
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Mostrar indicador de carga
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Enviando...';
            
            try {
                // Recopilar datos del formulario
                const formData = {
                    nombre: document.getElementById('nombre').value,
                    apellido: document.getElementById('apellido').value,
                    email: document.getElementById('email').value,
                    asunto: document.getElementById('asunto').value,
                    mensaje: document.getElementById('mensaje').value
                };
                
                // Enviar datos a la API
                const response = await fetch(`${API_URL}/mensajes`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || errorData.message || 'Error al enviar el mensaje');
                }
                
                // Mostrar mensaje de éxito
                alert('¡Gracias por tu mensaje! Te contactaremos pronto.');
                
                // Resetear formulario
                form.reset();
                if (charCount) charCount.textContent = '0/500';
                
            } catch (error) {
                console.error('Error al enviar mensaje:', error);
                alert(`Error al enviar el mensaje: ${error.message}. Por favor, intenta nuevamente.`);
            } finally {
                // Restaurar botón
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText;
            }
        });
    }
});