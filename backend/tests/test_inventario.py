import requests
import json

def test_inventario():
    try:
        # Login para obtener token
        login_response = requests.post('http://localhost:8000/login', data={
            'username': 'admin',
            'password': '123'
        })
        
        if login_response.status_code != 200:
            print(f'Error en login: {login_response.status_code}')
            return
            
        token = login_response.json()['access_token']
        print(f'✅ Login exitoso, token obtenido')
        
        # Obtener datos de inventario
        headers = {'Authorization': f'Bearer {token}'}
        
        # Obtener productos, categorías e inventario por separado
        productos_response = requests.get('http://localhost:8000/productos', headers=headers)
        inventario_response = requests.get('http://localhost:8000/inventario', headers=headers)
        categorias_response = requests.get('http://localhost:8000/categorias', headers=headers)
        
        print(f'Status productos: {productos_response.status_code}')
        print(f'Status inventario: {inventario_response.status_code}')
        print(f'Status categorías: {categorias_response.status_code}')
        
        if productos_response.status_code == 200 and inventario_response.status_code == 200:
            productos = productos_response.json()
            inventario = inventario_response.json()
            categorias = categorias_response.json()
            
            print(f'Total productos: {len(productos)}')
            print(f'Total inventario: {len(inventario)}')
            print(f'Total categorías: {len(categorias)}')
            
            # Mostrar algunos productos de ejemplo con su inventario
            for i, producto in enumerate(productos[:3]):
                stock_info = next((inv for inv in inventario if inv['id_producto'] == producto['id_producto']), None)
                stock = stock_info['cantidad'] if stock_info else 0
                precio = stock_info['precio'] if stock_info else 0
                print(f'Producto {i+1}: {producto["nombre"]} - Stock: {stock} - Precio: {precio}')
                
        else:
            print(f'Error: {response.text}')
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_inventario()