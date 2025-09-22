-- Script para crear el nuevo esquema de base de datos
-- Basado en la plantilla proporcionada

-- Tabla de Categorías
CREATE TABLE categorias (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

-- Tabla de Proveedores
CREATE TABLE proveedores (
    id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(150) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(50),
    direccion VARCHAR(200)
);

-- Tabla de Productos
CREATE TABLE productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    codigo_barras VARCHAR(50) UNIQUE,
    imagen_url VARCHAR(500),
    id_categoria INTEGER,
    id_proveedor INTEGER,
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

-- Tabla de Inventario (precio y stock dinámicos)
CREATE TABLE inventario (
    id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    precio INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- Historial de movimientos de inventario (entradas/salidas)
CREATE TABLE movimientos_inventario (
    id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('entrada', 'salida', 'ajuste')),
    cantidad INTEGER NOT NULL,
    precio_unitario INTEGER,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- Insertar categorías de ejemplo (incluyendo las actuales)
INSERT INTO categorias (nombre, descripcion) VALUES
('Electrónica', 'Productos electrónicos y tecnológicos'),
('Oficina', 'Suministros y equipos de oficina');

-- Insertar proveedores de ejemplo
INSERT INTO proveedores (nombre, contacto, telefono, direccion) VALUES
('Oficina Total', 'Carmen Jiménez', '+1-555-0108', 'Centro Empresarial 147, Torre B');