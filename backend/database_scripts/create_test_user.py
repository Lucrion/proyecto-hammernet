import sqlite3
from passlib.context import CryptContext
from datetime import datetime

# Configurar el contexto de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Crear usuario de prueba
conn = sqlite3.connect('ferreteria.db')
cursor = conn.cursor()

# Verificar si ya existe el usuario test
cursor.execute("SELECT * FROM usuarios WHERE username = ?", ("test",))
existing_user = cursor.fetchone()

if existing_user:
    print("Usuario 'test' ya existe")
else:
    # Crear nuevo usuario
    hashed_password = hash_password("test123")
    fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute(
        "INSERT INTO usuarios (nombre, username, password, role, fecha_creacion) VALUES (?, ?, ?, ?, ?)",
        ("Usuario Test", "test", hashed_password, "administrador", fecha_creacion)
    )
    
    conn.commit()
    print("Usuario 'test' creado exitosamente")
    print("Username: test")
    print("Password: test123")

conn.close()