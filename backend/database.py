from sqlalchemy import create_engine
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
    # Configuración para MySQL en desarrollo local
    engine = create_engine(
        DATABASE_URL or "mysql://root:@localhost/ferreteria"
    )

# Configurar la fábrica de sesiones
# - autocommit=False: Las transacciones deben confirmarse explícitamente
# - autoflush=False: Los cambios no se envían automáticamente a la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la clase base para los modelos declarativos
Base = declarative_base()

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