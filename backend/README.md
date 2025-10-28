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

- **Desarrollo**: SQLite (`config/ferreteria.db`)
- **Producción**: PostgreSQL (configurado en Render)

El sistema está configurado para usar únicamente SQLite en desarrollo local y PostgreSQL en producción. No se utilizan otras bases de datos como MySQL, MongoDB, Redis, etc.

## Deployment

El proyecto está configurado para deployment en Render:
- Archivo `render.yaml` incluido
- Variables de entorno configuradas
- Base de datos PostgreSQL

## Migración a PostgreSQL (Render)

Sigue estos pasos para exportar los datos desde SQLite y migrarlos a PostgreSQL en Render.

1) Configurar variables de entorno
- `DATABASE_URL`: cadena de conexión de Postgres (Render)
- `SQLITE_PATH` (opcional): ruta al archivo SQLite local si no usas el `ferreteria.db` del backend

Ejemplo en Windows PowerShell:
```
set SQLITE_PATH=c:\Users\darky\Desktop\proyecto\backend\ferreteria.db
set DATABASE_URL=postgresql://usuario:password@host:port/dbname
```

2) Crear tablas en Postgres
Si tu instancia de Postgres está vacía, crea las tablas:
```
# Ruta estándar:
python backend/scripts/setup_postgres.py
# Si moviste el script a backend/:
python backend/setup_postgres.py
```

3) Migrar datos desde SQLite a Postgres
Ejecuta el script de migración (preserva IDs y ajusta secuencias):
```
# Ruta estándar:
python backend/scripts/migrate_sqlite_to_postgres.py
# Si moviste el script a backend/:
python backend/migrate_sqlite_to_postgres.py
```

4) Verificar esquema y conteos
Opcionalmente, verifica el estado de tablas y registros:
```
python backend/utils/check_table_structure.py
python backend/utils/test_sale_creation.py  # imprime conteos de ventas/detalles
```

5) Configurar producción en Render
- Define `DATABASE_URL` en Render (dashboard o `render.yaml`)
- No uses `.env` en producción; Render inyecta variables del servicio

Notas:
- Haz un respaldo de `ferreteria.db` antes de migrar.
- Si cambiaste columnas en SQLite recientemente, el backend ya incluye ajustes ligeros automáticos para desarrollo.
- La migración también corre automáticamente durante el build en Render si `DATABASE_URL` apunta a Postgres y existe `backend/ferreteria.db`. Es idempotente: si una tabla ya tiene datos en Postgres, se omite.