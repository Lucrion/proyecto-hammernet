#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wrapper para compatibilidad: ejecuta backend/setup_postgres.py
Cuando el build en Render llama a scripts/setup_postgres.py,
redirigimos a la implementación real en la raíz de backend.
"""

import os
import sys

# Añadir la raíz de backend al path
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

try:
    from setup_postgres import main
except Exception as e:
    print(f"❌ No se pudo importar setup_postgres desde {BACKEND_ROOT}: {e}")
    raise

if __name__ == '__main__':
    main()