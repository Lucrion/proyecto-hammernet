import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
from seed_data import SessionLocal, ensure_admin_if_missing

def main():
    db = SessionLocal()
    try:
        out = ensure_admin_if_missing(db, rut='203477937', password_plain='123')
        print(out)
    finally:
        db.close()

if __name__ == '__main__':
    main()
