"""Convertir usuarios.rut a INTEGER y asegurar unicidad

Revision ID: 20251109_rut_integer_unique
Revises: 
Create Date: 2025-11-09
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251109_rut_integer_unique'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    dialect = conn.dialect.name

    if dialect == 'postgresql':
        # Convertir columna rut de VARCHAR a INTEGER, normalizando datos existentes
        op.execute(
            """
            ALTER TABLE usuarios
            ALTER COLUMN rut TYPE INTEGER USING regexp_replace(rut, '\\D', '', 'g')::integer;
            """
        )
        # Crear índice único (si no existe) para asegurar unicidad y rendimiento
        op.execute(
            """
            DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes WHERE tablename = 'usuarios' AND indexname = 'ux_usuarios_rut'
            ) THEN
                CREATE UNIQUE INDEX ux_usuarios_rut ON usuarios (rut);
            END IF;
            END $$;
            """
        )

    elif dialect == 'sqlite':
        # SQLite no soporta ALTER TYPE directamente; se debe recrear la tabla.
        # Sugerencia (ejecutar manualmente si se requiere en dev):
        # 1) Crear tabla temporal con esquema deseado (rut INTEGER UNIQUE)
        # 2) Copiar datos normalizando rut: INSERT INTO usuarios_new (..., rut) SELECT ..., CAST(REPLACE(REPLACE(REPLACE(rut,'-',''),'.',''),' ','') AS INTEGER) FROM usuarios;
        # 3) Renombrar tablas: DROP usuarios; ALTER TABLE usuarios_new RENAME TO usuarios;
        # Aquí no se implementa automáticamente para evitar pérdida accidental de datos.
        pass


def downgrade():
    conn = op.get_bind()
    dialect = conn.dialect.name

    if dialect == 'postgresql':
        # Revertir a VARCHAR(20) y eliminar índice único
        op.execute(
            """
            ALTER TABLE usuarios
            ALTER COLUMN rut TYPE VARCHAR(20);
            """
        )
        op.execute(
            """
            DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_indexes WHERE tablename = 'usuarios' AND indexname = 'ux_usuarios_rut'
            ) THEN
                DROP INDEX ux_usuarios_rut;
            END IF;
            END $$;
            """
        )
    elif dialect == 'sqlite':
        pass