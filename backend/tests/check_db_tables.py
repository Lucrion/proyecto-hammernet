import sqlite3

def check_tables():
    try:
        conn = sqlite3.connect('ferreteria.db')
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Tablas existentes en la base de datos:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Obtener estructura de cada tabla
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            print(f"  Columnas:")
            for col in columns:
                print(f"    {col[1]} ({col[2]})")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_tables()