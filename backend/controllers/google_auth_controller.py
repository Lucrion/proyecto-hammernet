import os
import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.usuario import Usuario
from controllers.usuario_controller import UsuarioController
from core.auth import crear_token
from datetime import datetime
import secrets
import string

class GoogleAuthController:
    def __init__(self):
        self.client_id = os.environ.get("GOOGLE_CLIENT_ID")
        self.client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI")
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Google OAuth credentials not properly configured")
    
    def get_google_auth_url(self):
        """Genera la URL de autorización de Google"""
        auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope=openid email profile&"
            f"response_type=code&"
            f"access_type=offline"
        )
        return auth_url
    
    async def handle_google_callback(self, code: str, db: Session):
        """Maneja el callback de Google y crea/autentica usuario"""
        try:
            # Intercambiar código por token
            token_data = await self._exchange_code_for_token(code)
            
            # Obtener información del usuario de Google
            user_info = await self._get_user_info(token_data["access_token"])
            
            # Buscar o crear usuario
            usuario = await self._find_or_create_user(user_info, db)
            
            # Crear token JWT usando RUT si existe, si no usar email
            sub_value = usuario.rut if getattr(usuario, "rut", None) else usuario.email
            token = crear_token(data={"sub": sub_value})
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": getattr(usuario, "id", getattr(usuario, "id_usuario", None)),
                    "rut": getattr(usuario, "rut", None),
                    "nombre": usuario.nombre,
                    "email": usuario.email,
                    "role": usuario.role
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error en autenticación con Google: {str(e)}")
    
    async def _exchange_code_for_token(self, code: str):
        """Intercambia el código de autorización por un token de acceso"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Error al obtener token de Google")
            
            return response.json()
    
    async def _get_user_info(self, access_token: str):
        """Obtiene la información del usuario desde Google"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Error al obtener información del usuario")
            
            return response.json()
    
    async def _find_or_create_user(self, user_info: dict, db: Session):
        """Busca un usuario existente o crea uno nuevo"""
        email = user_info.get("email")
        nombre = user_info.get("name", "Usuario Google")
        
        # Buscar usuario existente por email
        usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()
        
        if usuario_existente:
            return usuario_existente
        
        # Crear nuevo usuario
        # En este flujo no exigimos RUT; se puede completar luego
        rut = None
        password_temporal = self._generate_random_password()
        
        usuario_controller = UsuarioController()
        nuevo_usuario = await usuario_controller.crear_usuario_google(
            nombre=nombre,
            rut=rut,
            email=email,
            password=password_temporal,
            role="cliente",
            db=db
        )
        
        return nuevo_usuario
    
    # Eliminado: generación de username ya no es necesaria al usar RUT/email
    
    def _generate_random_password(self) -> str:
        """Genera una contraseña aleatoria para usuarios de Google"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(16))