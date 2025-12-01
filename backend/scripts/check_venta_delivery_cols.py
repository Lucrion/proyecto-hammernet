#!/usr/bin/env python
import sys
import os
from sqlalchemy import text
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.database import engine

def main():
    try:
        with engine.begin() as conn:
            rows = conn.execute(text("PRAGMA table_info(ventas)")).fetchall()
            cols = [row[1] for row in rows]
            print("VENTAS_COLUMNS=" + ",".join(cols))
    except Exception as e:
        print("ERROR=" + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
