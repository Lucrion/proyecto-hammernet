import sqlite3

conn = sqlite3.connect('ferreteria.db')
cursor = conn.cursor()

print("=== ACTUALIZANDO PRODUCTO PARA CATÁLOGO ===")

# Primero verificar el estado actual
cursor.execute('''
    SELECT id_producto, nombre, descripcion, imagen_url, marca, caracteristicas, en_catalogo, estado 
    FROM productos WHERE id_producto = 1
''')
result = cursor.fetchone()

if result:
    print(f"Estado actual del producto ID 1:")
    print(f"  Nombre: {result[1]}")
    print(f"  Descripción: {result[2] if result[2] else 'VACÍO'}")
    print(f"  Imagen URL: {result[3] if result[3] else 'VACÍO'}")
    print(f"  Marca: {result[4] if result[4] else 'VACÍO'}")
    print(f"  Características: {result[5] if result[5] else 'VACÍO'}")
    print(f"  En catálogo: {result[6]}")
    print(f"  Estado: {result[7]}")
    
    # Actualizar los campos faltantes
    cursor.execute('''
        UPDATE productos 
        SET descripcion = COALESCE(descripcion, 'Martillo de carpintero profesional, ideal para trabajos de construcción y carpintería'),
            imagen_url = COALESCE(imagen_url, 'https://via.placeholder.com/300x300?text=Martillo'),
            marca = COALESCE(marca, 'Stanley'),
            caracteristicas = COALESCE(caracteristicas, 'Mango ergonómico;Cabeza de acero forjado;Peso: 450g;Longitud: 32cm'),
            estado = 'activo'
        WHERE id_producto = 1
    ''')
    
    conn.commit()
    print("\n✅ Producto actualizado con campos faltantes")
    
    # Verificar el resultado
    cursor.execute('''
        SELECT id_producto, nombre, descripcion, imagen_url, marca, caracteristicas, en_catalogo, estado 
        FROM productos WHERE id_producto = 1
    ''')
    result_updated = cursor.fetchone()
    
    print(f"\nEstado después de la actualización:")
    print(f"  Nombre: {result_updated[1]}")
    print(f"  Descripción: {result_updated[2]}")
    print(f"  Imagen URL: {result_updated[3]}")
    print(f"  Marca: {result_updated[4]}")
    print(f"  Características: {result_updated[5]}")
    print(f"  En catálogo: {result_updated[6]}")
    print(f"  Estado: {result_updated[7]}")

conn.close()
print("\n🎉 ¡Producto listo para aparecer en el catálogo!")