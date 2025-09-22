from database import SessionLocal, engine
from models import UsuarioDB
from auth import hash_contraseña
from datetime import datetime

# Crear un usuario administrador
def crear_usuario_admin():
    db = SessionLocal()
    try:
        # Verificar si ya existe un usuario admin
        admin = db.query(UsuarioDB).filter(UsuarioDB.username == "admin").first()
        
        if admin:
            print(f"El usuario admin ya existe (ID: {admin.id})")
            return
        
        # Crear usuario admin
        hashed_password = hash_contraseña("admin")
        nuevo_admin = UsuarioDB(
            nombre="Administrador",
            username="admin",
            password=hashed_password,
            role="admin",
            fecha_creacion=datetime.now()
        )
        
        db.add(nuevo_admin)
        db.commit()
        db.refresh(nuevo_admin)
        
        print(f"Usuario admin creado exitosamente (ID: {nuevo_admin.id})")
    
    except Exception as e:
        print(f"Error al crear usuario admin: {e}")
    finally:
        db.close()

# Listar todos los usuarios
def listar_usuarios():
    db = SessionLocal()
    try:
        usuarios = db.query(UsuarioDB).all()
        
        if not usuarios:
            print("No hay usuarios en la base de datos")
            return
        
        print("\nUsuarios en la base de datos:")
        for u in usuarios:
            print(f"ID: {u.id}, Nombre: {u.nombre}, Username: {u.username}, Role: {u.role}")
    
    except Exception as e:
        print(f"Error al listar usuarios: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creando usuario administrador...")
    crear_usuario_admin()
    
    print("\nListando usuarios...")
    listar_usuarios()