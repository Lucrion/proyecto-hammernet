import sys, os, json
sys.path.append('backend')
from config.database import engine

info = {
    "dialect": engine.dialect.name,
    "url": str(engine.url)
}
out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db_info.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(json.dumps(info))
print(json.dumps(info))

