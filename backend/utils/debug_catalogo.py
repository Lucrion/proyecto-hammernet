import sqlite3

conn = sqlite3.connect('ferreteria.db')
cursor = conn.cursor()

print("=== DIAGNÓSTICO DEL CATÁLOGO ===")

# Verificar producto ID 1
cursor.execute('''
    SELECT id_producto, nombre, descripcion, imagen_url, marca, caracteristicas, en_catalogo, estado 
    FROM productos WHERE id_producto = 1
''')
result = cursor.fetchone()

if result:
    print(f"\nProducto ID 1:")
    print(f"  Nombre: {result[1]}")
    print(f"  Descripción: {result[2] if result[2] else 'VACÍO'}")
    print(f"  Imagen URL: {result[3] if result[3] else 'VACÍO'}")
    print(f"  Marca: {result[4] if result[4] else 'VACÍO'}")
    print(f"  Características: {result[5] if result[5] else 'VACÍO'}")
    print(f"  En catálogo: {result[6]}")
    print(f"  Estado: {result[7]}")
    
    # Verificar qué campos faltan
    campos_vacios = []
    if not result[2]: campos_vacios.append('descripcion')
    if not result[3]: campos_vacios.append('imagen_url')
    if not result[4]: campos_vacios.append('marca')
    if not result[5]: campos_vacios.append('caracteristicas')
    
    if campos_vacios:
        print(f"\n❌ CAMPOS VACÍOS: {', '.join(campos_vacios)}")
        print("Por eso el producto NO aparece en el catálogo público")
    else:
        print("\n✅ Todos los campos están completos")

conn.close()