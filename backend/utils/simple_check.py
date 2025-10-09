import sqlite3

try:
    conn = sqlite3.connect('ferreteria.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id_producto, nombre, descripcion, imagen_url, marca, caracteristicas, en_catalogo, estado FROM productos WHERE id_producto = 1')
    result = cursor.fetchone()
    
    if result:
        print("Producto ID 1:")
        print(f"Nombre: {result[1]}")
        print(f"Descripcion: '{result[2]}'")
        print(f"Imagen URL: '{result[3]}'")
        print(f"Marca: '{result[4]}'")
        print(f"Caracteristicas: '{result[5]}'")
        print(f"En catalogo: {result[6]}")
        print(f"Estado: '{result[7]}'")
        
        # Verificar si todos los campos están llenos
        campos_vacios = []
        if not result[2] or result[2].strip() == '':
            campos_vacios.append('descripcion')
        if not result[3] or result[3].strip() == '':
            campos_vacios.append('imagen_url')
        if not result[4] or result[4].strip() == '':
            campos_vacios.append('marca')
        if not result[5] or result[5].strip() == '':
            campos_vacios.append('caracteristicas')
            
        if campos_vacios:
            print(f"Campos vacios: {', '.join(campos_vacios)}")
        else:
            print("Todos los campos requeridos estan llenos")
    else:
        print("Producto no encontrado")
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")