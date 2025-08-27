from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from security import encrypt_data, decrypt_data, get_encryption_key
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# URL de la base de datos desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el motor de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crear la clase base para los modelos declarativos
Base = declarative_base()

# Definir el modelo MensajeContactoDB
class MensajeContactoDB(Base):
    __tablename__ = "mensajes_contacto"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    asunto = Column(String(200), nullable=False)
    mensaje = Column(String(1000), nullable=False)
    fecha_envio = Column(DateTime)
    leido = Column(Boolean, default=False)

def reencrypt_messages():
    db = Session(engine)
    try:
        # Obtener todos los mensajes
        mensajes = db.query(MensajeContactoDB).all()
        
        # Reencriptar cada mensaje
        for mensaje in mensajes:
            try:
                # Intentar desencriptar con la nueva clave
                email_decrypted = decrypt_data(mensaje.email)
                mensaje_decrypted = decrypt_data(mensaje.mensaje)
                
                # Si la desencriptación fue exitosa, reencriptar
                mensaje.email = encrypt_data(email_decrypted)
                mensaje.mensaje = encrypt_data(mensaje_decrypted)
                
                print(f"Mensaje {mensaje.id} reencriptado exitosamente")
            except Exception as e:
                print(f"Error al reencriptar mensaje {mensaje.id}: {str(e)}")
                continue
        
        # Guardar cambios en la base de datos
        db.commit()
        print("Proceso de reencriptación completado")
        
    except Exception as e:
        print(f"Error durante la reencriptación: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reencrypt_messages()