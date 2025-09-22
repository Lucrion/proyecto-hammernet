import requests
import json

try:
    response = requests.get('http://localhost:8000/productos')
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Response type: {type(data)}')
        
        if isinstance(data, list):
            productos = data
        elif isinstance(data, dict) and 'productos' in data:
            productos = data['productos']
        else:
            print('Formato de datos desconocido')
            print(f'Keys: {list(data.keys()) if isinstance(data, dict) else "No es dict"}')
            productos = []
        
        print(f'Total productos: {len(productos)}')
        
        if productos:
            print('\nPrimeros 5 productos y sus slugs:')
            for i, p in enumerate(productos[:5]):
                nombre = p.get('nombre', 'N/A')
                slug = nombre.lower().replace(' ', '-')
                print(f'{i+1}. {nombre} -> {slug}')
    else:
        print(f'Error: {response.status_code} - {response.text}')
        
except Exception as e:
    print(f'Error: {e}')