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

# Modo estricto: detener ante errores y variables no definidas
set -Eeuo pipefail

log_step() {
  echo "\n=== $1 ==="
}

log_step "Iniciando proceso de construcción para HammerNet"

# Verificar variables de entorno críticas
log_step "Verificando variables de entorno"
if [ -z "${DATABASE_URL:-}" ]; then
  echo "❌ ERROR: Variable DATABASE_URL no configurada"; exit 1
fi
if [ -z "${JWT_SECRET_KEY:-}" ]; then
  echo "❌ ERROR: Variable JWT_SECRET_KEY no configurada"; exit 1
fi

# Sugerencia: debe ser Postgres en producción
case "$DATABASE_URL" in
  *postgres*) echo "✅ DATABASE_URL apunta a PostgreSQL" ;;
  *) echo "⚠️ Aviso: DATABASE_URL no parece PostgreSQL (valor: $DATABASE_URL)" ;;
esac

echo "✅ Variables de entorno críticas presentes"

log_step "Instalando dependencias Python"
python -m pip install --upgrade pip wheel
python -m pip install -r requirements.txt

log_step "Creando estructura de directorios"
mkdir -p data  # Almacenamiento de datos JSON (fallback)
mkdir -p logs  # Logs de la aplicación

log_step "Configurando base de datos en PostgreSQL"
# Ejecutar setup desde raíz de backend
if [ -f "setup_postgres.py" ]; then
  python setup_postgres.py
else
  echo "❌ ERROR: no se encontró backend/setup_postgres.py"; exit 1
fi

# Migración automática de SQLite a PostgreSQL si hay archivo local
if [[ "$DATABASE_URL" == *"postgres"* ]]; then
  SQLITE_PATH="${SQLITE_PATH:-$(pwd)/ferreteria.db}"
  MIGRATION_SCRIPT="migrate_sqlite_to_postgres.py"
  if [ -f "$SQLITE_PATH" ] && [ -f "$MIGRATION_SCRIPT" ]; then
    log_step "Migrando datos desde SQLite a PostgreSQL (automático)"
    echo "Usando SQLITE_PATH=$SQLITE_PATH"
    # La migración es idempotente: omite tablas con datos
    if ! DATABASE_URL="$DATABASE_URL" SQLITE_PATH="$SQLITE_PATH" python "$MIGRATION_SCRIPT"; then
      echo "⚠️ Migración falló o no necesaria (se continuará con el despliegue)"
    fi
  else
    echo "ℹ️ No se encontró archivo SQLite en $SQLITE_PATH o script $MIGRATION_SCRIPT; se omite migración"
  fi
fi

# Diagnóstico básico del directorio para logs de Render
log_step "Contenido de backend tras build"
pwd
ls -la

log_step "Construcción completada exitosamente"
echo "🚀 Aplicación HammerNet lista para producción"