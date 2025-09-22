import sqlite3

# Verificar tablas en ferreteria.db
try:
    conn = sqlite3.connect('ferreteria.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Tablas en ferreteria.db:')
    for table in tables:
        print(f"  - {table[0]}")
    
    # Verificar si hay usuarios
    if any('usuario' in table[0].lower() for table in tables):
        for table in tables:
            if 'usuario' in table[0].lower():
                cursor.execute(f"SELECT * FROM {table[0]}")
                users = cursor.fetchall()
                print(f"\nUsuarios en tabla {table[0]}:")
                for user in users:
                    print(f"  {user}")
    else:
        print("\nNo se encontraron tablas de usuarios")
    
    conn.close()
except Exception as e:
    print(f"Error con ferreteria.db: {e}")