#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import text
from backend.config.database import engine

def main():
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT estado_envio, COUNT(*) FROM ventas GROUP BY estado_envio ORDER BY estado_envio"))
        out = { (r[0] or 'None'): int(r[1] or 0) for r in rows }
        print("SQL_ESTADOS_ENVIO_COUNTS=", out)

if __name__ == "__main__":
    main()

