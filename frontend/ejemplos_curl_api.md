# Ejemplos de cURL para API de Ferretería

Este documento contiene ejemplos prácticos de comandos cURL para probar todos los endpoints de la API de ferretería.

## Configuración Base

```bash
# Variables de entorno (ajustar según tu configuración)
API_URL="http://localhost:8000/api"
TOKEN="tu_token_jwt_aqui"
```

## 1. Autenticación

### Obtener Token de Acceso
```bash
# Login con credenciales
curl -X POST "$API_URL/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@ferreteria.com&password=admin123"

# Respuesta esperada:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }
```

### Verificar Token
```bash
# Verificar que el token funciona
curl -X GET "$API_URL/usuarios/me" \
  -H "Authorization: Bearer $TOKEN"
```

## 2. Gestión de Productos

### Obtener Todos los Productos
```bash
# Listar productos (sin filtros)
curl -X GET "$API_URL/productos" \
  -H "Authorization: Bearer $TOKEN"

# Con paginación
curl -X GET "$API_URL/productos?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Con filtros
curl -X GET "$API_URL/productos?categoria_id=1&proveedor_id=2" \
  -H "Authorization: Bearer $TOKEN"
```

### Obtener Producto por ID
```bash
# Obtener producto específico
curl -X GET "$API_URL/productos/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Crear Nuevo Producto
```bash
# Crear producto básico
curl -X POST "$API_URL/productos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Martillo de Acero",
    "descripcion": "Martillo profesional de acero forjado",
    "precio": 2500,
    "stock": 15,
    "id_categoria": 1,
    "stock_minimo": 5
  }'

# Crear producto completo
curl -X POST "$API_URL/productos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Taladro Eléctrico",
    "descripcion": "Taladro eléctrico 500W con percutor",
    "precio": 8500,
    "stock": 8,
    "id_categoria": 2,
    "stock_minimo": 3,
    "costo_bruto": 6000,
    "costo_neto": 5500,
    "porcentaje_utilidad": 54.5,
    "utilidad_pesos": 3000
  }'
```

### Actualizar Producto
```bash
# Actualizar producto existente
curl -X PUT "$API_URL/productos/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Martillo de Acero Premium",
    "descripcion": "Martillo profesional de acero forjado con mango ergonómico",
    "precio": 2800,
    "stock": 12,
    "id_categoria": 1,
    "stock_minimo": 5
  }'

# Actualizar solo el precio
curl -X PUT "$API_URL/productos/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "precio": 3000
  }'
```

### Eliminar Producto
```bash
# Eliminar producto
curl -X DELETE "$API_URL/productos/1" \
  -H "Authorization: Bearer $TOKEN"
```

## 3. Gestión de Categorías

### Obtener Categorías
```bash
# Listar todas las categorías
curl -X GET "$API_URL/categorias" \
  -H "Authorization: Bearer $TOKEN"

# Obtener categoría específica
curl -X GET "$API_URL/categorias/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Crear Categoría
```bash
# Crear nueva categoría
curl -X POST "$API_URL/categorias" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Herramientas Eléctricas",
    "descripcion": "Taladros, sierras, lijadoras y otras herramientas eléctricas"
  }'

# Crear categoría simple
curl -X POST "$API_URL/categorias" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Tornillería"
  }'
```

### Actualizar Categoría
```bash
# Actualizar categoría
curl -X PUT "$API_URL/categorias/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Herramientas Manuales",
    "descripcion": "Martillos, destornilladores, llaves y herramientas manuales"
  }'
```

### Eliminar Categoría
```bash
# Eliminar categoría
curl -X DELETE "$API_URL/categorias/1" \
  -H "Authorization: Bearer $TOKEN"
```

## 4. Gestión de Proveedores

### Obtener Proveedores
```bash
# Listar todos los proveedores
curl -X GET "$API_URL/proveedores" \
  -H "Authorization: Bearer $TOKEN"

# Obtener proveedor específico
curl -X GET "$API_URL/proveedores/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Crear Proveedor
```bash
# Crear nuevo proveedor
curl -X POST "$API_URL/proveedores" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Distribuidora Herramientas SA",
    "contacto": "Juan Pérez",
    "telefono": "+56912345678",
    "email": "ventas@herramientas.cl",
    "direccion": "Av. Industrial 1234, Santiago"
  }'

# Crear proveedor básico
curl -X POST "$API_URL/proveedores" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Ferretería Central",
    "contacto": "María González",
    "telefono": "+56987654321"
  }'
```

### Actualizar Proveedor
```bash
# Actualizar proveedor
curl -X PUT "$API_URL/proveedores/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Distribuidora Herramientas Premium SA",
    "contacto": "Juan Pérez Silva",
    "telefono": "+56912345678",
    "email": "ventas@herramientaspremium.cl",
    "direccion": "Av. Industrial 1234, Oficina 501, Santiago"
  }'
```

### Eliminar Proveedor
```bash
# Eliminar proveedor
curl -X DELETE "$API_URL/proveedores/1" \
  -H "Authorization: Bearer $TOKEN"
```

## 5. Gestión de Inventario

### Obtener Inventario
```bash
# Listar todo el inventario
curl -X GET "$API_URL/inventario" \
  -H "Authorization: Bearer $TOKEN"

# Obtener inventario de producto específico
curl -X GET "$API_URL/inventario/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Actualizar Stock
```bash
# Crear/actualizar entrada de inventario
curl -X POST "$API_URL/inventario" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_producto": 1,
    "cantidad_actual": 25,
    "stock_minimo": 5
  }'

# Actualizar stock existente
curl -X PUT "$API_URL/inventario/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cantidad_actual": 30,
    "stock_minimo": 8
  }'
```

### Eliminar Entrada de Inventario
```bash
# Eliminar entrada de inventario
curl -X DELETE "$API_URL/inventario/1" \
  -H "Authorization: Bearer $TOKEN"
```

## 6. Sistema de Mensajes

### Obtener Mensajes
```bash
# Listar todos los mensajes
curl -X GET "$API_URL/mensajes" \
  -H "Authorization: Bearer $TOKEN"

# Obtener mensaje específico
curl -X GET "$API_URL/mensajes/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Crear Mensaje (Contacto)
```bash
# Enviar mensaje de contacto (sin autenticación)
curl -X POST "$API_URL/mensajes" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Carlos Rodríguez",
    "email": "carlos@email.com",
    "asunto": "Consulta sobre productos",
    "mensaje": "Hola, me gustaría saber si tienen disponibilidad de taladros eléctricos y cuáles son los precios. Gracias."
  }'

# Mensaje con más detalles
curl -X POST "$API_URL/mensajes" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Ana Martínez",
    "email": "ana.martinez@empresa.com",
    "asunto": "Cotización para proyecto",
    "mensaje": "Buenos días, necesito cotizar los siguientes productos para un proyecto de construcción: 50 martillos, 20 taladros, tornillos varios. ¿Podrían enviarme una cotización detallada? Saludos."
  }'
```

### Marcar Mensaje como Leído
```bash
# Marcar mensaje como leído
curl -X PUT "$API_URL/mensajes/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "leido": true
  }'
```

### Eliminar Mensaje
```bash
# Eliminar mensaje
curl -X DELETE "$API_URL/mensajes/1" \
  -H "Authorization: Bearer $TOKEN"
```

## 7. Endpoints Especiales

### Documentación de la API
```bash
# Obtener documentación Swagger/OpenAPI
curl -X GET "http://localhost:8000/docs"

# Obtener esquema OpenAPI en JSON
curl -X GET "http://localhost:8000/openapi.json"
```

### Health Check
```bash
# Verificar estado del servidor
curl -X GET "http://localhost:8000/"

# Respuesta esperada:
# {"message": "API de Ferretería funcionando correctamente"}
```

## 8. Scripts de Prueba Automatizada

### Script Bash para Pruebas Completas
```bash
#!/bin/bash

# Configuración
API_URL="http://localhost:8000/api"
EMAIL="admin@ferreteria.com"
PASSWORD="admin123"

echo "=== INICIANDO PRUEBAS DE API ==="

# 1. Obtener token
echo "1. Obteniendo token de acceso..."
TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD")

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Error: No se pudo obtener el token"
    exit 1
fi

echo "✅ Token obtenido exitosamente"

# 2. Probar endpoints GET
echo "\n2. Probando endpoints GET..."

endpoints=("productos" "categorias" "proveedores" "inventario" "mensajes")

for endpoint in "${endpoints[@]}"; do
    echo "   Probando GET /$endpoint..."
    response=$(curl -s -w "%{http_code}" -X GET "$API_URL/$endpoint" \
        -H "Authorization: Bearer $TOKEN")
    
    http_code="${response: -3}"
    if [ "$http_code" = "200" ]; then
        echo "   ✅ GET /$endpoint: OK"
    else
        echo "   ❌ GET /$endpoint: Error $http_code"
    fi
done

# 3. Crear datos de prueba
echo "\n3. Creando datos de prueba..."

# Crear categoría
echo "   Creando categoría..."
cat_response=$(curl -s -X POST "$API_URL/categorias" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "nombre": "Herramientas Test",
        "descripcion": "Categoría de prueba"
    }')

echo "   ✅ Categoría creada"

# Crear proveedor
echo "   Creando proveedor..."
prov_response=$(curl -s -X POST "$API_URL/proveedores" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "nombre": "Proveedor Test",
        "contacto": "Test Contact",
        "telefono": "+56912345678"
    }')

echo "   ✅ Proveedor creado"

# Crear producto
echo "   Creando producto..."
prod_response=$(curl -s -X POST "$API_URL/productos" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "nombre": "Producto Test",
        "descripcion": "Producto de prueba",
        "precio": 1500,
        "stock": 10,
        "id_categoria": 1,
        "stock_minimo": 3
    }')

echo "   ✅ Producto creado"

# Crear mensaje
echo "   Creando mensaje..."
msg_response=$(curl -s -X POST "$API_URL/mensajes" \
    -H "Content-Type: application/json" \
    -d '{
        "nombre": "Usuario Test",
        "email": "test@test.com",
        "asunto": "Mensaje de prueba",
        "mensaje": "Este es un mensaje de prueba automatizada"
    }')

echo "   ✅ Mensaje creado"

echo "\n=== PRUEBAS COMPLETADAS EXITOSAMENTE ==="
```

### Script PowerShell para Windows
```powershell
# Script de pruebas para Windows PowerShell

$API_URL = "http://localhost:8000/api"
$EMAIL = "admin@ferreteria.com"
$PASSWORD = "admin123"

Write-Host "=== INICIANDO PRUEBAS DE API ===" -ForegroundColor Green

# 1. Obtener token
Write-Host "1. Obteniendo token de acceso..." -ForegroundColor Yellow

$tokenBody = @{
    username = $EMAIL
    password = $PASSWORD
}

try {
    $tokenResponse = Invoke-RestMethod -Uri "$API_URL/token" -Method Post -Body $tokenBody -ContentType "application/x-www-form-urlencoded"
    $token = $tokenResponse.access_token
    Write-Host "✅ Token obtenido exitosamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: No se pudo obtener el token" -ForegroundColor Red
    exit 1
}

# 2. Configurar headers
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# 3. Probar endpoints GET
Write-Host "`n2. Probando endpoints GET..." -ForegroundColor Yellow

$endpoints = @("productos", "categorias", "proveedores", "inventario", "mensajes")

foreach ($endpoint in $endpoints) {
    Write-Host "   Probando GET /$endpoint..." -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$API_URL/$endpoint" -Method Get -Headers $headers
        Write-Host "   ✅ GET /$endpoint: OK" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ GET /$endpoint: Error $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

# 4. Crear datos de prueba
Write-Host "`n3. Creando datos de prueba..." -ForegroundColor Yellow

# Crear categoría
Write-Host "   Creando categoría..." -ForegroundColor Cyan
$categoriaData = @{
    nombre = "Herramientas Test PS"
    descripcion = "Categoría de prueba desde PowerShell"
} | ConvertTo-Json

try {
    $catResponse = Invoke-RestMethod -Uri "$API_URL/categorias" -Method Post -Body $categoriaData -Headers $headers
    Write-Host "   ✅ Categoría creada" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error al crear categoría" -ForegroundColor Red
}

# Crear producto
Write-Host "   Creando producto..." -ForegroundColor Cyan
$productoData = @{
    nombre = "Producto Test PS"
    descripcion = "Producto de prueba desde PowerShell"
    precio = 2500
    stock = 15
    id_categoria = 1
    stock_minimo = 5
} | ConvertTo-Json

try {
    $prodResponse = Invoke-RestMethod -Uri "$API_URL/productos" -Method Post -Body $productoData -Headers $headers
    Write-Host "   ✅ Producto creado" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error al crear producto" -ForegroundColor Red
}

Write-Host "`n=== PRUEBAS COMPLETADAS ==="  -ForegroundColor Green
```

## 9. Casos de Uso Comunes

### Flujo Completo: Crear Producto con Inventario
```bash
# 1. Crear categoría
CATEGORIA_ID=$(curl -s -X POST "$API_URL/categorias" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Herramientas Nuevas"}' | \
  grep -o '"id_categoria":[0-9]*' | cut -d':' -f2)

# 2. Crear producto
PRODUCTO_ID=$(curl -s -X POST "$API_URL/productos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"nombre\": \"Sierra Eléctrica\",
    \"precio\": 12000,
    \"id_categoria\": $CATEGORIA_ID,
    \"stock_minimo\": 3
  }" | \
  grep -o '"id":[0-9]*' | cut -d':' -f2)

# 3. Agregar al inventario
curl -X POST "$API_URL/inventario" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"id_producto\": $PRODUCTO_ID,
    \"cantidad_actual\": 20,
    \"stock_minimo\": 3
  }"

echo "Producto creado con ID: $PRODUCTO_ID en categoría: $CATEGORIA_ID"
```

### Búsqueda y Filtrado Avanzado
```bash
# Buscar productos por categoría y rango de precios
curl -X GET "$API_URL/productos?categoria_id=1" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.[] | select(.precio >= 1000 and .precio <= 5000)'

# Obtener productos con stock bajo
curl -X GET "$API_URL/inventario" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.[] | select(.cantidad_actual <= .stock_minimo)'

# Listar mensajes no leídos
curl -X GET "$API_URL/mensajes" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.[] | select(.leido == false)'
```

### Actualización Masiva
```bash
# Script para actualizar precios con aumento del 10%
PRODUCTOS=$(curl -s -X GET "$API_URL/productos" -H "Authorization: Bearer $TOKEN")

echo "$PRODUCTOS" | jq -r '.[] | @base64' | while read producto; do
    _jq() {
        echo ${producto} | base64 --decode | jq -r ${1}
    }
    
    id=$(_jq '.id')
    precio_actual=$(_jq '.precio')
    nuevo_precio=$(echo "$precio_actual * 1.1" | bc -l | cut -d'.' -f1)
    
    echo "Actualizando producto $id: $precio_actual -> $nuevo_precio"
    
    curl -s -X PUT "$API_URL/productos/$id" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"precio\": $nuevo_precio}" > /dev/null
done

echo "Actualización masiva completada"
```

Estos ejemplos de cURL cubren todos los aspectos de la API y proporcionan una base sólida para pruebas, automatización y integración con otros sistemas.