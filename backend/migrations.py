from database import engine
from sqlalchemy import text

def migrate_apellido():
    try:
        with engine.connect() as connection:
            # Añadir columna apellido a mensajes_contacto
            connection.execute(text("ALTER TABLE mensajes_contacto ADD COLUMN apellido VARCHAR(50) NOT NULL DEFAULT 'Apellido'"))
            print("Columna 'apellido' añadida a mensajes_contacto exitosamente")
            
            # Eliminar columna apellido de usuarios
            connection.execute(text("ALTER TABLE usuarios DROP COLUMN apellido"))
            print("Columna 'apellido' eliminada de usuarios exitosamente")
            
    except Exception as e:
        print(f"Error en la migración: {str(e)}")

if __name__ == "__main__":
    migrate_apellido()