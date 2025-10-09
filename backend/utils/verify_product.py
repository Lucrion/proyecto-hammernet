import sqlite3

conn = sqlite3.connect('ferreteria.db')
cursor = conn.cursor()

print("=== VERIFICANDO PRODUCTO DESPUÉS DE ACTUALIZACIÓN ===")

# Verificar el estado actual del producto
cursor.execute('''
    SELECT id_producto, nombre, descripcion, imagen_url, marca, caracteristicas, en_catalogo, estado 
    FROM productos WHERE id_producto = 1
''')
result = cursor.fetchone()

if result:
    print(f"Producto ID 1:")
    print(f"  Nombre: {result[1]}")
    print(f"  Descripción: {result[2]}")
    print(f"  Imagen URL: {result[3]}")
    print(f"  Marca: {result[4]}")
    print(f"  Características: {result[5]}")
    print(f"  En catálogo: {result[6]}")
    print(f"  Estado: {result[7]}")
    
    # Verificar si cumple con los requisitos del catálogo
    print("\n=== VERIFICACIÓN DE REQUISITOS ===")
    
    # Requisitos según obtener_catalogo_publico:
    # 1. estado == 'activo'
    # 2. en_catalogo == True (1)
    # 3. descripcion no vacía
    # 4. imagen_url no vacía
    # 5. marca no vacía
    # 6. caracteristicas no vacías
    
    requisitos_cumplidos = []
    requisitos_faltantes = []
    
    if result[7] == 'activo':
        requisitos_cumplidos.append("✅ Estado: activo")
    else:
        requisitos_faltantes.append(f"❌ Estado: {result[7]} (debe ser 'activo')")
    
    if result[6] == 1:
        requisitos_cumplidos.append("✅ En catálogo: True")
    else:
        requisitos_faltantes.append(f"❌ En catálogo: {result[6]} (debe ser 1)")
    
    if result[2] and result[2].strip():
        requisitos_cumplidos.append("✅ Descripción: presente")
    else:
        requisitos_faltantes.append("❌ Descripción: vacía o nula")
    
    if result[3] and result[3].strip():
        requisitos_cumplidos.append("✅ Imagen URL: presente")
    else:
        requisitos_faltantes.append("❌ Imagen URL: vacía o nula")
    
    if result[4] and result[4].strip():
        requisitos_cumplidos.append("✅ Marca: presente")
    else:
        requisitos_faltantes.append("❌ Marca: vacía o nula")
    
    if result[5] and result[5].strip():
        requisitos_cumplidos.append("✅ Características: presente")
    else:
        requisitos_faltantes.append("❌ Características: vacías o nulas")
    
    print("Requisitos cumplidos:")
    for req in requisitos_cumplidos:
        print(f"  {req}")
    
    if requisitos_faltantes:
        print("\nRequisitos faltantes:")
        for req in requisitos_faltantes:
            print(f"  {req}")
    else:
        print("\n🎉 ¡Todos los requisitos están cumplidos!")
        print("El producto debería aparecer en el catálogo público.")

else:
    print("❌ Producto ID 1 no encontrado")

# Verificar todos los productos que cumplen los requisitos
print("\n=== PRODUCTOS QUE CUMPLEN REQUISITOS PARA CATÁLOGO ===")
cursor.execute('''
    SELECT id_producto, nombre, estado, en_catalogo,
           CASE WHEN descripcion IS NOT NULL AND descripcion != '' THEN 'Sí' ELSE 'No' END as tiene_desc,
           CASE WHEN imagen_url IS NOT NULL AND imagen_url != '' THEN 'Sí' ELSE 'No' END as tiene_img,
           CASE WHEN marca IS NOT NULL AND marca != '' THEN 'Sí' ELSE 'No' END as tiene_marca,
           CASE WHEN caracteristicas IS NOT NULL AND caracteristicas != '' THEN 'Sí' ELSE 'No' END as tiene_caract
    FROM productos 
    WHERE estado = 'activo' 
    AND en_catalogo = 1
    AND descripcion IS NOT NULL AND descripcion != ''
    AND imagen_url IS NOT NULL AND imagen_url != ''
    AND marca IS NOT NULL AND marca != ''
    AND caracteristicas IS NOT NULL AND caracteristicas != ''
''')

productos_validos = cursor.fetchall()
if productos_validos:
    print(f"Productos válidos para catálogo: {len(productos_validos)}")
    for prod in productos_validos:
        print(f"  ID {prod[0]}: {prod[1]}")
else:
    print("❌ No hay productos que cumplan todos los requisitos para el catálogo")

conn.close()