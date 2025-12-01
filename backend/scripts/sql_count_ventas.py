#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import text
from backend.config.database import engine

def main():
    with engine.begin() as conn:
        try:
            c = conn.execute(text("SELECT COUNT(*) FROM ventas")).scalar()
            print("SQL_VENTAS_COUNT=", int(c or 0))
        except Exception as e:
            print("ERROR=", str(e))

if __name__ == "__main__":
    main()

