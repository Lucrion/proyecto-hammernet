# Hammernet - Sistema de Gestión de Ferretería

Sistema completo de gestión para ferretería con backend FastAPI y frontend Astro.

## 🚀 Características

- **Backend**: FastAPI con autenticación JWT
- **Frontend**: Astro con interfaz administrativa
- **Base de datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Almacenamiento**: Cloudinary para imágenes
- **Deployment**: Configurado para Render.com

## 📋 Funcionalidades

- ✅ Gestión de productos
- ✅ Gestión de categorías
- ✅ Gestión de proveedores
- ✅ Sistema de usuarios y autenticación
- ✅ Mensajes de contacto
- ✅ Interfaz administrativa completa
- ✅ API REST documentada

## 🛠️ Tecnologías

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL/SQLite
- JWT Authentication
- Cloudinary
- Uvicorn

### Frontend
- Astro
- Tailwind CSS
- JavaScript vanilla
- Responsive design

## 🚀 Deployment en Render

### Prerrequisitos
1. Cuenta en [Render.com](https://render.com)
2. Cuenta en [Cloudinary](https://cloudinary.com) (opcional, para imágenes)
3. Repositorio en GitHub

### Pasos para el deployment

#### 1. Configurar la base de datos PostgreSQL
1. En Render, crear una nueva base de datos PostgreSQL
2. Nombre: `hammernet-db`
3. Usuario: `hammernet_user`
4. Guardar la URL de conexión

#### 2. Configurar el servicio web
1. Crear nuevo Web Service en Render
2. Conectar con tu repositorio de GitHub
3. Configuración:
   - **Name**: `hammernet-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `cd backend && chmod +x build.sh && ./build.sh`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 3. Variables de entorno
Configurar las siguientes variables en Render:

```bash
# Base de datos (automática desde la DB creada)
DATABASE_URL=postgresql://...

# JWT (generar automáticamente)
JWT_SECRET_KEY=auto-generated
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Servidor
HOST=0.0.0.0
PORT=8000

# CORS
ALLOWED_ORIGINS=https://tu-frontend.onrender.com,https://tu-backend.onrender.com

# Admin
ADMIN_PASSWORD=tu-password-seguro

# Cloudinary (opcional)
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret
```

#### 4. Deployment automático
El archivo `render.yaml` está configurado para deployment automático. Render detectará y usará esta configuración.

## 🔧 Desarrollo Local

### Backend
```bash
cd backend
pip install -r requirements.txt
python scripts/init_db.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📚 API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario

### Productos
- `GET /api/productos` - Listar productos
- `POST /api/productos` - Crear producto
- `PUT /api/productos/{id}` - Actualizar producto
- `DELETE /api/productos/{id}` - Eliminar producto

### Categorías
- `GET /api/categorias` - Listar categorías
- `POST /api/categorias` - Crear categoría
- `PUT /api/categorias/{id}` - Actualizar categoría
- `DELETE /api/categorias/{id}` - Eliminar categoría

### Proveedores
- `GET /api/proveedores` - Listar proveedores
- `POST /api/proveedores` - Crear proveedor
- `PUT /api/proveedores/{id}` - Actualizar proveedor
- `DELETE /api/proveedores/{id}` - Eliminar proveedor

## 🔐 Autenticación

El sistema usa JWT para autenticación. Usuario administrador por defecto:
- **Usuario**: `admin`
- **Contraseña**: `123` (cambiar en producción)

## 📁 Estructura del Proyecto

```
proyecto/
├── backend/
│   ├── controllers/     # Lógica de negocio
│   ├── models/         # Modelos de base de datos
│   ├── views/          # Rutas de la API
│   ├── scripts/        # Scripts de configuración
│   ├── main.py         # Aplicación principal
│   ├── database.py     # Configuración de DB
│   ├── auth.py         # Autenticación
│   ├── requirements.txt
│   ├── render.yaml     # Configuración de Render
│   └── build.sh        # Script de build
└── frontend/
    ├── src/
    │   ├── pages/      # Páginas Astro
    │   ├── layouts/    # Layouts
    │   ├── components/ # Componentes
    │   └── scripts/    # JavaScript
    ├── public/         # Archivos estáticos
    └── package.json
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para soporte, crear un issue en GitHub o contactar al equipo de desarrollo.
