import asyncio
import json
import os, sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.config.database import SessionLocal
from backend.controllers.producto_controller import ProductoController

def run_seed():
    db = SessionLocal()
    try:
        result = asyncio.run(ProductoController.seed_ejemplos(db))
        print(json.dumps(result))
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
