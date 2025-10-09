import sqlite3

conn = sqlite3.connect('ferreteria.db')
cursor = conn.cursor()

print("Actualizando producto ID 1...")

# Actualizar el producto con todos los campos requeridos
cursor.execute('''
    UPDATE productos 
    SET descripcion = 'Martillo de carpintero profesional, ideal para trabajos de construcción y carpintería',
        imagen_url = 'https://via.placeholder.com/300x300?text=Martillo',
        caracteristicas = 'Mango ergonómico;Cabeza de acero forjado;Peso: 450g;Longitud: 32cm'
    WHERE id_producto = 1
''')

conn.commit()

# Verificar la actualización
cursor.execute('''
    SELECT id_producto, nombre, descripcion, imagen_url, marca, caracteristicas, en_catalogo, estado 
    FROM productos WHERE id_producto = 1
''')
result = cursor.fetchone()

if result:
    print("Producto actualizado:")
    print(f"  ID: {result[0]}")
    print(f"  Nombre: {result[1]}")
    print(f"  Descripción: {result[2]}")
    print(f"  Imagen URL: {result[3]}")
    print(f"  Marca: {result[4]}")
    print(f"  Características: {result[5]}")
    print(f"  En catálogo: {result[6]}")
    print(f"  Estado: {result[7]}")
    
    # Verificar que todos los campos requeridos estén llenos
    campos_ok = all([
        result[7] == 'activo',  # estado
        result[6] == 1,         # en_catalogo
        result[2] and result[2].strip(),  # descripcion
        result[3] and result[3].strip(),  # imagen_url
        result[4] and result[4].strip(),  # marca
        result[5] and result[5].strip()   # caracteristicas
    ])
    
    if campos_ok:
        print("\n✅ ¡Producto listo para el catálogo!")
    else:
        print("\n❌ Aún faltan campos por completar")

conn.close()