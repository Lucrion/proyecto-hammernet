# HammerNet - Sistema de Gestión de Ferretería

Sistema completo de gestión para ferretería con backend FastAPI y frontend Astro.

## Estructura del Proyecto

```
proyecto/
├── backend/                    # API Backend (FastAPI)
│   ├── controllers/           # Controladores de lógica de negocio
│   ├── models/               # Modelos de base de datos (SQLAlchemy)
│   ├── views/                # Rutas y endpoints de la API
│   ├── scripts/              # Scripts de utilidades y configuración
│   │   ├── analyze_db.py     # Análisis de base de datos
│   │   ├── check_db.py       # Verificación de base de datos
│   │   ├── check_users.py    # Verificación de usuarios
│   │   ├── create_test_user.py # Creación de usuarios de prueba
│   │   ├── init_db.py        # Inicialización de base de datos
│   │   ├── migrate_to_optimized.py # Migración de esquemas
│   │   ├── setup_database.py # Configuración de base de datos
│   │   └── setup_postgres.py # Configuración de PostgreSQL
│   ├── tests/                # Tests automatizados
│   │   ├── test_all_endpoints.py
│   │   ├── test_endpoints.py
│   │   ├── test_fixed_schema.py
│   │   ├── test_login.py
│   │   ├── test_password.py
│   │   └── test_schema.py
│   ├── sql/                  # Archivos SQL y esquemas
│   │   ├── create_new_schema.sql
│   │   ├── optimized_schema.sql
│   │   └── optimized_schema_fixed.sql
│   ├── db/                   # Archivos de base de datos
│   │   ├── database.db
│   │   ├── ferreteria.db
│   │   ├── test_optimized.db
│   │   └── test_optimized_fixed.db
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── database.py          # Configuración de base de datos
│   ├── auth.py              # Autenticación y autorización
│   └── requirements.txt     # Dependencias de Python
│
└── frontend/                 # Frontend Web (Astro)
    ├── src/
    │   ├── components/       # Componentes reutilizables
    │   ├── layouts/          # Layouts de página
    │   ├── pages/            # Páginas de la aplicación
    │   ├── scripts/          # Scripts JavaScript
    │   └── styles/           # Estilos CSS
    ├── public/
    │   ├── images/           # Recursos de imágenes organizados
    │   │   ├── icons/        # Iconos SVG
    │   │   ├── logos/        # Logos de la empresa
    │   │   └── products/     # Imágenes de productos
    │   └── scripts/          # Scripts públicos
    ├── package.json          # Dependencias de Node.js
    └── astro.config.mjs      # Configuración de Astro
```

## Funcionalidades

### Backend (FastAPI)
- **Autenticación**: Sistema completo de login/registro con JWT
- **Gestión de Productos**: CRUD completo con categorías y proveedores
- **Inventario**: Control de stock y movimientos
- **Usuarios**: Gestión de usuarios y permisos
- **Mensajes**: Sistema de contacto y comunicación
- **API REST**: Endpoints documentados con ejemplos

### Frontend (Astro)
- **Interfaz Moderna**: UI responsive con Tailwind CSS
- **Gestión de Productos**: Catálogo y búsqueda
- **Panel de Administración**: Gestión completa del sistema
- **Formularios**: Contacto y gestión de datos
- **Optimización**: Imágenes y recursos organizados

## Instalación y Uso

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Tecnologías Utilizadas

- **Backend**: FastAPI, SQLAlchemy, SQLite/PostgreSQL, JWT
- **Frontend**: Astro, Tailwind CSS, JavaScript
- **Base de Datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Autenticación**: JWT Tokens
- **Deployment**: Render (configurado)

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request
