#!/usr/bin/env bash

#############################################################################
# Script de construcción para despliegue en Render.com
#
# Este script se ejecuta automáticamente durante el proceso de despliegue
# en la plataforma Render.com. Realiza las siguientes tareas:
#
# 1. Instala todas las dependencias Python especificadas en requirements.txt
# 2. Crea la estructura de directorios necesaria para la aplicación
# 3. Verifica las variables de entorno críticas
# 4. Configura la base de datos PostgreSQL para producción
#
# El script está configurado para detenerse inmediatamente si cualquier
# comando falla (set -o errexit), lo que ayuda a identificar problemas
# durante el despliegue.
#############################################################################

# Detener la ejecución si cualquier comando falla
set -o errexit

echo "=== Iniciando proceso de construcción para Hammernet ==="

# Verificar variables de entorno críticas
echo "Verificando variables de entorno..."
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: Variable DATABASE_URL no configurada"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "❌ ERROR: Variable JWT_SECRET_KEY no configurada"
    exit 1
fi

echo "✅ Variables de entorno verificadas correctamente"

echo "Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creando estructura de directorios necesaria..."
mkdir -p data  # Directorio para almacenamiento de datos JSON (fallback)
mkdir -p logs  # Directorio para logs de la aplicación

echo "Configurando base de datos PostgreSQL para producción..."
python scripts/setup_postgres.py

echo "Verificando instalación..."
python -c "import fastapi, uvicorn, sqlalchemy, passlib, jose; print('✅ Todas las dependencias principales instaladas correctamente')"

echo "=== Construcción completada exitosamente ==="
echo "🚀 Aplicación Hammernet lista para producción"