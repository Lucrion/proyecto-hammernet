#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

def check_database():
    conn = sqlite3.connect('ferreteria.db')
    cursor = conn.cursor()
    
    # Verificar producto específico con todos los campos del catálogo
    cursor.execute('''
        SELECT id_producto, nombre, descripcion, imagen_url, marca, caracteristicas, en_catalogo, estado 
        FROM productos WHERE id_producto = 1
    ''')
    result = cursor.fetchone()
    print(f'Producto ID 1 completo: {result}')
    
    # Verificar qué campos están vacíos
    if result:
        campos = ['id_producto', 'nombre', 'descripcion', 'imagen_url', 'marca', 'caracteristicas', 'en_catalogo', 'estado']
        for i, campo in enumerate(campos):
            valor = result[i]
            if valor is None or valor == '':
                print(f'  ❌ Campo {campo}: VACÍO')
            else:
                print(f'  ✅ Campo {campo}: {valor}')
    
    # Verificar todos los productos en catálogo
    cursor.execute('SELECT id_producto, nombre, en_catalogo FROM productos WHERE en_catalogo = 1')
    results = cursor.fetchall()
    print(f'\nProductos marcados como en_catalogo=1: {len(results)}')
    for r in results:
        print(f'  - ID {r[0]}: {r[1]}')
    
    # Verificar productos que cumplen TODOS los requisitos del catálogo
    cursor.execute('''
        SELECT id_producto, nombre 
        FROM productos 
        WHERE en_catalogo = 1 
        AND estado = 'activo' 
        AND descripcion IS NOT NULL 
        AND descripcion != ''
        AND imagen_url IS NOT NULL 
        AND imagen_url != ''
        AND marca IS NOT NULL 
        AND marca != ''
        AND caracteristicas IS NOT NULL 
        AND caracteristicas != ''
    ''')
    results_completos = cursor.fetchall()
    print(f'\nProductos que cumplen TODOS los requisitos del catálogo: {len(results_completos)}')
    for r in results_completos:
        print(f'  - ID {r[0]}: {r[1]}')
    
    conn.close()

if __name__ == "__main__":
    check_database()