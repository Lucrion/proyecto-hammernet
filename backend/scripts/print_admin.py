import sys, os
sys.path.append('backend')
from config.database import SessionLocal
from models.usuario import UsuarioDB
from models.rol import RolDB

s = SessionLocal()
a = s.query(UsuarioDB).filter(UsuarioDB.email == 'admin@localhost').first()
r = s.query(RolDB).filter(RolDB.id_rol == getattr(a, 'id_rol', None)).first() if a else None
line = f"admin_present={bool(a)} rut={getattr(a,'rut',None)} rol={getattr(r,'nombre',None)}"
print(line)
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_path = os.path.join(backend_root, 'admin_state.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(line + "\n")
s.close()
