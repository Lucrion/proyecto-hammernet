#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.config.database import engine

def main():
    db_path = engine.url.database
    print("DB_PATH=", db_path)
    print("EXISTS=", os.path.exists(db_path) if db_path else None)
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db_path.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write((db_path or '') + "\n")

if __name__ == "__main__":
    main()
