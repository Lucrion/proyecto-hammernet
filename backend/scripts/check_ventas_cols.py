#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import text
from config.database import engine
import os

def main():
    d = engine.dialect.name
    with engine.begin() as conn:
        if d == 'sqlite':
            cols = [row[1] for row in conn.execute(text("PRAGMA table_info(ventas)")).fetchall()]
        else:
            cols = [r[0] for r in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='ventas' ORDER BY ordinal_position"))]
    out = f"dialect={d}\nventas_columns={','.join(cols)}\n"
    print(out)
    try:
        path = os.path.join(os.path.dirname(__file__), '..', 'check_ventas_cols.out')
        path = os.path.abspath(path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(out)
    except Exception:
        pass

if __name__ == '__main__':
    main()
