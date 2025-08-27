import requests

response = requests.get('http://localhost:8000/productos')
productos = response.json()

# Buscar el producto que contiene 'cacacaacasda'
producto_encontrado = None
for p in productos:
    if 'cacacaacasda' in p['nombre']:
        producto_encontrado = p
        break

if producto_encontrado:
    print(f'Producto encontrado: "{producto_encontrado["nombre"]}"')
    slug = producto_encontrado['nombre'].lower().replace(' ', '-')
    print(f'Slug generado: "{slug}"')
    print(f'Longitud del nombre: {len(producto_encontrado["nombre"])}')
    print(f'Caracteres: {[c for c in producto_encontrado["nombre"]]}')
else:
    print('Producto no encontrado')
    print('Productos disponibles:')
    for i, p in enumerate(productos[:5]):
        print(f'{i+1}. "{p["nombre"]}"')