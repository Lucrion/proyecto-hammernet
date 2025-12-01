import sys, os, json
sys.path.append('backend')
from config.database import SessionLocal
from seed_data import ensure_admin_if_missing

s = SessionLocal()
res = ensure_admin_if_missing(s, rut='203477937', password_plain='123')
s.close()
out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'admin_apply.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(json.dumps(res))

