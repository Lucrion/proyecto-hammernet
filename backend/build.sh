#!/usr/bin/env bash

#############################################################################
# Script de construcción para despliegue en Render.com
#
# Este script se ejecuta automáticamente durante el proceso de despliegue
# en la plataforma Render.com. Realiza las siguientes tareas:
#
# 1. Instala todas las dependencias Python especificadas en requirements.txt
# 2. Crea la estructura de directorios necesaria para la aplicación
#
# El script está configurado para detenerse inmediatamente si cualquier
# comando falla (set -o errexit), lo que ayuda a identificar problemas
# durante el despliegue.
#############################################################################

# Detener la ejecución si cualquier comando falla
set -o errexit

echo "=== Iniciando proceso de construcción ==="

echo "Instalando dependencias Python..."
pip install -r requirements.txt

echo "Creando estructura de directorios necesaria..."
mkdir -p data  # Directorio para almacenamiento de datos JSON (fallback)

echo "Configurando base de datos PostgreSQL para producción..."
python setup_postgres.py

echo "=== Construcción completada con éxito ==="