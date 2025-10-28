#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wrapper para compatibilidad: ejecuta backend/migrate_sqlite_to_postgres.py
Permite que builds antiguos que llaman scripts/migrate_sqlite_to_postgres.py
funcionen aunque el script se haya movido a la raíz de backend.
"""

import os
import sys

# Añadir la raíz de backend al path
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

try:
    from migrate_sqlite_to_postgres import main
except Exception as e:
    print(f"❌ No se pudo importar migrate_sqlite_to_postgres desde {BACKEND_ROOT}: {e}")
    raise

if __name__ == '__main__':
    main()