from database import engine
from sqlalchemy import inspect, text
from models import *

# Inspeccionar la estructura de la base de datos
inspector = inspect(engine)
tables = inspector.get_table_names()

print("=== ESTRUCTURA DE LA BASE DE DATOS ===")
print(f"Tablas encontradas: {len(tables)}")
print("\nTablas:")
for table in tables:
    print(f"- {table}")

print("\n=== ESTRUCTURA DETALLADA DE CADA TABLA ===")
for table in tables:
    print(f"\n{table.upper()}:")
    columns = inspector.get_columns(table)
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        default = f" DEFAULT {col['default']}" if col['default'] else ""
        print(f"  - {col['name']}: {col['type']} {nullable}{default}")
    
    # Mostrar claves foráneas
    foreign_keys = inspector.get_foreign_keys(table)
    if foreign_keys:
        print("  Claves foráneas:")
        for fk in foreign_keys:
            print(f"    - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

print("\n=== DATOS DE EJEMPLO ===")
with engine.connect() as conn:
    for table in tables:
        print(f"\n{table.upper()} (primeros 5 registros):")
        try:
            result = conn.execute(text(f"SELECT * FROM {table} LIMIT 5"))
            rows = result.fetchall()
            if rows:
                # Obtener nombres de columnas
                columns = result.keys()
                print(f"  Columnas: {list(columns)}")
                for i, row in enumerate(rows, 1):
                    print(f"  {i}: {dict(row._mapping)}")
            else:
                print("  (Sin datos)")
        except Exception as e:
            print(f"  Error al consultar: {e}")

print("\n=== RESUMEN ===")
print(f"Total de tablas: {len(tables)}")
print("Base de datos revisada exitosamente.")