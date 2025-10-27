from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la base de datos
# --------------------------------
# Este módulo configura la conexión a la base de datos PostgreSQL

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Configurar la URL de la base de datos según el entorno
if DATABASE_URL and "postgres" in DATABASE_URL:
    # Configuración para PostgreSQL en producción
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800
    )
else:
    # Configuración para SQLite en desarrollo local
    # Usar la URL del .env si está disponible, sino usar ruta por defecto
    if DATABASE_URL and DATABASE_URL.startswith('sqlite:///'):
        # Usar la URL del .env tal como está configurada
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    else:
        # Fallback a la ruta por defecto en la raíz del backend
        import os
        # Usar la raíz del proyecto backend en lugar de la carpeta config
        backend_root = os.path.dirname(os.path.dirname(__file__))
        db_path = os.path.join(backend_root, 'ferreteria.db')
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False}
        )

# Configurar la fábrica de sesiones
# - autocommit=False: Las transacciones deben confirmarse explícitamente
# - autoflush=False: Los cambios no se envían automáticamente a la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Importar la clase base desde models.base para mantener consistencia
from models.base import Base

# Migración automática de columnas nuevas en SQLite
# -----------------------------------------------
# Asegura que la tabla 'usuarios' tenga columnas agregadas recientemente
# cuando se usa SQLite en desarrollo, sin requerir una herramienta de migraciones.

def _ensure_usuario_extra_columns_sqlite():
    try:
        if engine.dialect.name != 'sqlite':
            return
        with engine.begin() as conn:
            cols = [row[1] for row in conn.execute(text("PRAGMA table_info(usuarios)")).fetchall()]
            if 'apellido' not in cols:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN apellido TEXT"))
            if 'rut' not in cols:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN rut TEXT"))
            if 'email' not in cols:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN email TEXT"))
            if 'telefono' not in cols:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN telefono TEXT"))
    except Exception as e:
        # No bloquear el arranque si falla; mostrar aviso
        print(f"[DB] Aviso: migración usuarios parcialmente fallida: {e}")

# Ejecutar verificación/migración al importar el módulo
_ensure_usuario_extra_columns_sqlite()

# Gestión de dependencias y acceso a datos
# --------------------------------------

# Función para obtener una sesión de base de datos (dependency injection)
def get_db():
    """Proporciona una sesión de base de datos para las rutas de FastAPI.
    
    Esta función actúa como una dependencia inyectable en FastAPI.
    Crea y devuelve una sesión de base de datos, asegurándose de
    cerrarla después de su uso.
    
    Yields:
        Session: Una sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db  # Devolver la sesión para que FastAPI la use
    finally:
        db.close()  # Asegurar que la sesión se cierre al terminar