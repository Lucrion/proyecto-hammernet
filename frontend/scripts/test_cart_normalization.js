function normalize(cart){
  const base = Array.isArray(cart) ? cart : [];
  const norm = base.map(it => ({...it, id: Number(it.id ?? it.id_producto) || it.id}));
  const dedup = norm.reduce((acc, it) => {
    const key = String(it.id);
    const idx = acc.findIndex(x => String(x.id) === key);
    if (idx >= 0) {
      acc[idx].cantidad = Number(acc[idx].cantidad||0) + Number(it.cantidad||0);
      return acc;
    }
    acc.push(it);
    return acc;
  }, []);
  return dedup;
}

const input = [
  { id: 10, cantidad: 1, nombre: 'Taladro', precio_venta: 10000 },
  { id_producto: 10, cantidad: 2, nombre: 'Taladro', precio_venta: 10000 },
  { id: 11, cantidad: 1, nombre: 'Martillo', precio_venta: 5000 }
];
const out = normalize(input);
const fs = require('fs');
fs.writeFileSync('frontend/scripts/out_cart_test.json', JSON.stringify(out), { encoding: 'utf-8' });
