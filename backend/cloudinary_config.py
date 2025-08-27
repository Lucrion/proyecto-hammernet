import cloudinary
import cloudinary.uploader
import os

def configure_cloudinary():
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        secure=True  # Usar HTTPS para todas las URLs
    )

async def upload_image(image_data, public_id=None):
    """Sube una imagen a Cloudinary y devuelve la URL segura.
    
    Esta función maneja la subida de imágenes a Cloudinary con opciones
    predeterminadas para el proyecto. Puede recibir datos de imagen en
    diferentes formatos (ruta de archivo, bytes, URL, etc.).
    
    Args:
        image_data: Datos de la imagen a subir (archivo, bytes, URL, etc.)
        public_id: Identificador público personalizado (opcional)
        
    Returns:
        str: URL segura (HTTPS) de la imagen subida, o None si hay error
    """
    try:
        # Configurar opciones de carga
        upload_options = {
            "folder": "productos",  # Carpeta donde se guardarán las imágenes
            "resource_type": "auto",  # Detectar automáticamente el tipo de recurso
            "overwrite": True,  # Sobrescribir si existe una imagen con el mismo ID
            "unique_filename": True,  # Generar nombre único si no se proporciona public_id
        }
        
        # Si se proporciona un public_id personalizado, usarlo
        if public_id:
            upload_options["public_id"] = public_id
        
        # Procesar el objeto UploadFile si es necesario
        upload_data = image_data
        if hasattr(image_data, 'file'):
            # Es un objeto UploadFile de FastAPI
            print(f"Procesando objeto UploadFile: {image_data.filename}")
            # Leer el contenido del archivo
            contents = await image_data.read()
            upload_data = contents
            print(f"Contenido leído: {len(contents)} bytes")
        
        # Subir la imagen a Cloudinary
        print("Iniciando subida a Cloudinary...")
        # Cloudinary.uploader.upload no es una función asíncrona, así que la ejecutamos directamente
        result = cloudinary.uploader.upload(upload_data, **upload_options)
        print(f"Imagen subida exitosamente. URL: {result.get('secure_url')}")
        
        # Devolver la URL segura (HTTPS) de la imagen
        return result["secure_url"]
    except Exception as e:
        # Manejo de errores con información detallada para depuración
        print(f"Error al subir imagen a Cloudinary: {e}")
        import traceback
        traceback.print_exc()
        return None

def delete_image(public_id):
    """Elimina una imagen de Cloudinary por su identificador público.
    
    Args:
        public_id: Identificador público de la imagen a eliminar
        
    Returns:
        bool: True si la eliminación fue exitosa, False en caso contrario
    """
    try:
        # Intentar eliminar la imagen de Cloudinary
        result = cloudinary.uploader.destroy(public_id)
        return result["result"] == "ok"  # Cloudinary devuelve "ok" si la eliminación fue exitosa
    except Exception as e:
        # Manejo de errores
        print(f"Error al eliminar imagen de Cloudinary: {e}")
        return False

def get_public_id_from_url(url):
    """Extrae el public_id de una URL de Cloudinary.
    
    Esta función analiza una URL de Cloudinary y extrae el public_id,
    que es necesario para operaciones como eliminar la imagen.
    
    Args:
        url: URL de Cloudinary de la imagen
        
    Returns:
        str: El public_id extraído, o None si no se pudo extraer
    """
    try:
        # Verificar que sea una URL de Cloudinary
        if not url or "cloudinary.com" not in url:
            return None
            
        # Extraer el public_id de la URL
        # Formato típico: https://res.cloudinary.com/cloud_name/image/upload/v1234567890/folder/public_id.ext
        parts = url.split("/")
        if "upload" in parts:
            # Encontrar el índice de 'upload'
            upload_index = parts.index("upload")
            # El public_id está después de la versión (v1234567890)
            if upload_index + 1 < len(parts) and parts[upload_index + 1].startswith("v"):
                # Unir todas las partes después de la versión, excluyendo la extensión del último elemento
                public_id_parts = parts[upload_index + 2:]
                if public_id_parts:
                    last_part = public_id_parts[-1]
                    # Eliminar la extensión del último elemento
                    if "." in last_part:
                        public_id_parts[-1] = last_part.split(".")[0]
                    return "/".join(public_id_parts)
        return None
    except Exception as e:
        print(f"Error al extraer public_id de URL: {e}")
        return None