# HammerNet Backend - API FastAPI

API REST completa para el sistema de gestión de ferretería HammerNet.

## Estructura del Backend

```
backend/
├── controllers/              # Lógica de negocio
│   ├── auth_controller.py   # Autenticación y autorización
│   ├── categoria_controller.py # Gestión de categorías
│   ├── inventario_controller.py # Control de inventario
│   ├── mensaje_controller.py # Sistema de mensajes
│   ├── producto_controller.py # Gestión de productos
│   ├── proveedor_controller.py # Gestión de proveedores
│   └── usuario_controller.py # Gestión de usuarios
├── models/                   # Modelos de base de datos
│   ├── base.py              # Modelo base
│   ├── categoria.py         # Modelo de categorías
│   ├── inventario.py        # Modelo de inventario
│   ├── mensaje.py           # Modelo de mensajes
│   ├── producto.py          # Modelo de productos
│   ├── proveedor.py         # Modelo de proveedores
│   └── usuario.py           # Modelo de usuarios
├── views/                    # Rutas y endpoints
│   ├── auth_routes.py       # Endpoints de autenticación
│   ├── categoria_routes.py  # Endpoints de categorías
│   ├── inventario_routes.py # Endpoints de inventario
│   ├── mensaje_routes.py    # Endpoints de mensajes
│   ├── producto_routes.py   # Endpoints de productos
│   ├── proveedor_routes.py  # Endpoints de proveedores
│   └── usuario_routes.py    # Endpoints de usuarios
├── scripts/                  # Scripts de utilidades y migración
│   ├── check_db_schema.py   # Verificación de esquema DB
│   ├── check_productos_schema.py # Verificación productos
│   └── migrate_database.py  # Migración de base de datos
├── tests/                    # Tests automatizados
│   └── test_all_endpoints.py # Tests completos de endpoints
├── sql/                      # Esquemas SQL
│   └── unified_schema.sql   # Esquema unificado actual
├── db/                       # Archivos de base de datos
├── main.py                   # Punto de entrada
├── database.py               # Configuración de DB
└── auth.py                   # Sistema de autenticación
```

## Endpoints Principales

### Autenticación
- `POST /auth/register` - Registro de usuarios
- `POST /auth/login` - Inicio de sesión
- `GET /auth/me` - Información del usuario actual

### Productos
- `GET /productos/` - Listar productos
- `GET /productos/{id}` - Obtener producto por ID
- `POST /productos/` - Crear producto
- `PUT /productos/{id}` - Actualizar producto
- `DELETE /productos/{id}` - Eliminar producto

### Categorías
- `GET /categorias/` - Listar categorías
- `POST /categorias/` - Crear categoría
- `PUT /categorias/{id}` - Actualizar categoría
- `DELETE /categorias/{id}` - Eliminar categoría
  
### Usuarios (Admin)
- `GET /usuarios/` - Listar usuarios
- `POST /usuarios/` - Crear usuario
- `PUT /usuarios/{id}` - Actualizar usuario
- `DELETE /usuarios/{id}` - Eliminar usuario

### Mensajes (Admin)
- `GET /mensajes/` - Listar mensajes
- `GET /mensajes/estadisticas` - Estadísticas de mensajes
- `PUT /mensajes/{id}/leido` - Marcar como leído
- `DELETE /mensajes/{id}` - Eliminar mensaje

## Instalación

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Inicializar base de datos:**
```bash
python scripts/init_db.py
```

4. **Ejecutar la aplicación:**
```bash
python main.py
```

La API estará disponible en `http://localhost:8000`

## Documentación de la API

Una vez ejecutando la aplicación, puedes acceder a:
- **Swagger UI**: `http://localhost:8000/docs`

## Autenticación

El sistema utiliza JWT (JSON Web Tokens) para la autenticación:

## Permisos

- **Público**: Ver productos
- **Admin**: Acceso completo al sistema
- **otro**: Gestión de ventas o inventario

## Base de Datos

- **Desarrollo**: SQLite (`db/ferreteria.db`)
- **Producción**: PostgreSQL (configurado en Render)

## Deployment

El proyecto está configurado para deployment en Render:
- Archivo `render.yaml` incluido
- Variables de entorno configuradas
- Base de datos PostgreSQL