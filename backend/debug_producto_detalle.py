import requests
import json
from urllib.parse import unquote

def debug_producto_detalle():
    try:
        # Obtener todos los productos
        response = requests.get('http://localhost:8000/productos')
        print(f'Status de /productos: {response.status_code}')
        
        if response.status_code != 200:
            print(f'Error al obtener productos: {response.text}')
            return
            
        productos = response.json()
        print(f'Total productos encontrados: {len(productos)}')
        
        if not productos:
            print('No hay productos en la base de datos')
            return
            
        print('\n=== ANÁLISIS DE SLUGS ====')
        print('Productos y sus slugs generados:')
        
        for i, producto in enumerate(productos[:10]):  # Solo los primeros 10
            nombre = producto.get('nombre', '')
            slug_generado = nombre.lower().replace(' ', '-')
            print(f'{i+1}. ID: {producto.get("id")} | Nombre: "{nombre}" | Slug: "{slug_generado}"')
            
            # Verificar caracteres especiales
            caracteres_especiales = [c for c in nombre if not c.isalnum() and c != ' ']
            if caracteres_especiales:
                print(f'   ⚠️  Caracteres especiales encontrados: {caracteres_especiales}')
                slug_limpio = ''.join(c for c in nombre if c.isalnum() or c == ' ').lower().replace(' ', '-')
                print(f'   🔧 Slug limpio sugerido: "{slug_limpio}"')
        
        # Simular búsqueda por slug
        print('\n=== SIMULACIÓN DE BÚSQUEDA POR SLUG ====')
        if productos:
            producto_test = productos[0]
            nombre_test = producto_test.get('nombre', '')
            slug_test = nombre_test.lower().replace(' ', '-')
            
            print(f'Producto de prueba: "{nombre_test}"')
            print(f'Slug generado: "{slug_test}"')
            
            # Buscar el producto usando el mismo algoritmo del frontend
            producto_encontrado = None
            for p in productos:
                slug_producto = p['nombre'].lower().replace(' ', '-')
                if slug_producto == slug_test:
                    producto_encontrado = p
                    break
            
            if producto_encontrado:
                print('✅ Producto encontrado correctamente por slug')
            else:
                print('❌ Producto NO encontrado por slug')
                print('Posibles causas:')
                print('- Caracteres especiales en el nombre')
                print('- Espacios múltiples')
                print('- Caracteres Unicode')
        
        # Verificar endpoint individual
        print('\n=== VERIFICACIÓN DE ENDPOINT INDIVIDUAL ====')
        if productos:
            producto_id = productos[0].get('id')
            response_individual = requests.get(f'http://localhost:8000/productos/{producto_id}')
            print(f'Status de /productos/{producto_id}: {response_individual.status_code}')
            
            if response_individual.status_code == 200:
                print('✅ Endpoint individual funciona correctamente')
            else:
                print(f'❌ Error en endpoint individual: {response_individual.text}')
        
        print('\n=== RECOMENDACIONES ====')
        print('1. Verificar que el frontend esté usando la URL correcta de la API')
        print('2. Verificar que no haya errores de CORS')
        print('3. Verificar que los nombres de productos no tengan caracteres especiales problemáticos')
        print('4. Considerar usar el ID del producto en lugar del slug para mayor confiabilidad')
        
    except Exception as e:
        print(f'Error durante el diagnóstico: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_producto_detalle()