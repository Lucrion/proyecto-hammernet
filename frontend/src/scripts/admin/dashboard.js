import { getData } from '../../scripts/utils/api.js';

function formatCurrency(value) {
  try {
    return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(value || 0);
  } catch {
    return `$${(value || 0).toFixed(0)}`;
  }
}

function formatDate(value) {
  try {
    const d = new Date(value);
    return d.toLocaleString('es-CL');
  } catch {
    return String(value);
  }
}

function renderActividadItem(evt) {
  const iconColor = 'text-blue-600';
  const bgColor = 'bg-blue-100';
  const entidad = evt.entidad_tipo || 'Evento';
  const detalle = evt.detalle || '';
  const fecha = formatDate(evt.fecha_evento);
  const titulo = `${entidad}: ${evt.accion || ''}`;
  return `
    <div class="flex items-start">
      <div class="${bgColor} p-2 rounded-full mr-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ${iconColor}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
      </div>
      <div>
        <p class="text-gray-800">${titulo}${detalle ? ` — <span class="font-medium">${detalle}</span>` : ''}</p>
        <p class="text-sm text-gray-500">${fecha}</p>
      </div>
    </div>
  `;
}

async function cargarDashboard() {
  try {
    let metrics = await getData('/api/dashboard/metrics');


    // Productos
    const productosTotal = metrics?.productos?.total_productos ?? 0;
    const productosBajo = metrics?.productos?.productos_bajo_stock ?? 0;
    const productosSin = metrics?.productos?.productos_sin_stock ?? 0;
    document.getElementById('dashboardProductosTotal')?.replaceChildren(document.createTextNode(String(productosTotal)));
    document.getElementById('dashboardProductosBajo')?.replaceChildren(document.createTextNode(String(productosBajo)));
    document.getElementById('dashboardProductosSin')?.replaceChildren(document.createTextNode(String(productosSin)));

    // Usuarios
    const usuariosActivos = metrics?.usuarios?.activos ?? 0;
    const usuariosInactivos = metrics?.usuarios?.inactivos ?? 0;
    const usuariosTotal = metrics?.usuarios?.total ?? 0;
    document.getElementById('dashboardUsuariosActivos')?.replaceChildren(document.createTextNode(String(usuariosActivos)));
    document.getElementById('dashboardUsuariosInactivos')?.replaceChildren(document.createTextNode(String(usuariosInactivos)));
    document.getElementById('dashboardUsuariosTotal')?.replaceChildren(document.createTextNode(String(usuariosTotal)));

    // Ventas
    const ingresos = metrics?.ventas?.total_ventas ?? 0;
    const cantVentas = metrics?.ventas?.cantidad_ventas ?? 0;
    const promedio = metrics?.ventas?.promedio_venta ?? 0;
    const canceladas = metrics?.ventas?.ventas_canceladas ?? 0;
    document.getElementById('dashboardVentasIngresos')?.replaceChildren(document.createTextNode(formatCurrency(ingresos)));
    document.getElementById('dashboardVentasCantidad')?.replaceChildren(document.createTextNode(String(cantVentas)));
    document.getElementById('dashboardVentasPromedio')?.replaceChildren(document.createTextNode(formatCurrency(promedio)));
    document.getElementById('dashboardVentasCanceladas')?.replaceChildren(document.createTextNode(String(canceladas)));

    // Ventas por períodos
    const vp = metrics?.ventas_periodos || {};
    const diaIng = vp?.dia?.ingresos ?? 0; const diaCant = vp?.dia?.cantidad ?? 0;
    const semIng = vp?.semana?.ingresos ?? 0; const semCant = vp?.semana?.cantidad ?? 0;
    const mesIng = vp?.mes?.ingresos ?? 0; const mesCant = vp?.mes?.cantidad ?? 0;
    document.getElementById('metricVentasDiaIngresos')?.replaceChildren(document.createTextNode(formatCurrency(diaIng)));
    document.getElementById('metricVentasDiaCantidad')?.replaceChildren(document.createTextNode(String(diaCant)));
    document.getElementById('metricVentasSemanaIngresos')?.replaceChildren(document.createTextNode(formatCurrency(semIng)));
    document.getElementById('metricVentasSemanaCantidad')?.replaceChildren(document.createTextNode(String(semCant)));
    document.getElementById('metricVentasMesIngresos')?.replaceChildren(document.createTextNode(formatCurrency(mesIng)));
    document.getElementById('metricVentasMesCantidad')?.replaceChildren(document.createTextNode(String(mesCant)));

    try {
      const inventarioValor = metrics?.productos?.valor_inventario_total ?? 0;
      const ofertaPct = metrics?.productos?.porcentaje_en_oferta ?? 0;
      document.getElementById('dashboardValorInventarioTotal')?.replaceChildren(document.createTextNode(formatCurrency(inventarioValor)));
      document.getElementById('dashboardProductosEnOfertaPct')?.replaceChildren(document.createTextNode(String(Math.round(ofertaPct)) + '%'));
    } catch {}

    // Actividad reciente
    const contenedorActividad = document.getElementById('actividadReciente');
    if (contenedorActividad) {
      const eventos = metrics?.actividad_reciente ?? [];
      if (eventos.length === 0) {
        contenedorActividad.innerHTML = '<p class="text-sm text-gray-500">Sin actividad reciente</p>';
      } else {
        contenedorActividad.innerHTML = eventos.map(renderActividadItem).join('');
      }
    }

    // (Se redistribuyen gráficos al apartado correspondiente)
  } catch (error) {
    console.error('Error al cargar dashboard:', error);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  try {
    cargarDashboard();
    cargarUltimasVentas();
    initApartadosAnalytics();
    setupResizeRedraw();
  } catch (e) {
    console.warn('Dashboard no pudo inicializar completamente:', e);
  }
});

async function ensureGoogleChartsReady() {
  return new Promise((resolve) => {
    try {
      if (window.google && window.google.visualization) {
        console.log('[Charts] Google Charts ya listo');
        return resolve();
      }
      if (!(window.google && window.google.charts)) {
        console.log('[Charts] Inyectando loader de Google Charts');
        const script = document.createElement('script');
        script.src = 'https://www.gstatic.com/charts/loader.js';
        script.async = true;
        script.onload = () => {
          try {
            window.google.charts.load('current', { packages: ['corechart', 'bar'] });
            window.google.charts.setOnLoadCallback(() => {
              console.log('[Charts] onLoadCallback disparado (inject)');
              resolve();
            });
          } catch (e) {
            console.warn('[Charts] Error tras loader inject', e);
            resolve();
          }
        };
        document.head.appendChild(script);
      } else {
        window.google.charts.load('current', { packages: ['corechart', 'bar'] });
      }
      // Reintento defensivo por si onLoadCallback no se dispara en algunos navegadores
      let tries = 0;
      const maxTries = 20;
      const interval = setInterval(() => {
        tries++;
        if (window.google && window.google.visualization) {
          clearInterval(interval);
          console.log('[Charts] Google Charts listo tras', tries, 'intentos');
          resolve();
        } else if (tries >= maxTries) {
          clearInterval(interval);
          console.warn('[Charts] No se pudo inicializar Google Charts a tiempo');
          resolve();
        }
      }, 150);
      window.google.charts.setOnLoadCallback(() => {
        console.log('[Charts] onLoadCallback disparado');
        resolve();
      });
    } catch (e) {
      console.warn('[Charts] Error inicializando loader', e);
      resolve();
    }
  });
}

async function cargarUltimasVentas() {
  try {
    const ventas = await getData('/api/ventas?limit=10');
    const cont = document.getElementById('ultimasVentasBody');
    if (!cont) return;
    if (!Array.isArray(ventas) || ventas.length === 0) {
      cont.innerHTML = '<tr><td colspan="5" class="px-4 py-3 text-center text-gray-500">Sin ventas recientes</td></tr>';
      return;
    }
    const fmtPrecio = (v) => new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(Number(v||0));
    const fmtFecha = (iso) => { try { return new Date(iso).toLocaleDateString('es-CL', { dateStyle: 'medium' }); } catch { return iso; } };
    cont.innerHTML = ventas.map(v => `
      <tr>
        <td class="px-4 py-3 text-sm text-gray-800">#${v.id_venta}</td>
        <td class="px-4 py-3 text-sm text-gray-700">${fmtFecha(v.fecha_venta)}</td>
        <td class="px-4 py-3 text-sm">${v.usuario || 'Invitado'}</td>
        <td class="px-4 py-3 text-sm font-semibold">${fmtPrecio(v.total_venta)}</td>
        <td class="px-4 py-3 text-sm">
          <span class="px-2 py-1 rounded text-white ${v.estado === 'completada' ? 'bg-green-600' : (v.estado === 'cancelada' ? 'bg-red-600' : 'bg-yellow-500')}">${v.estado}</span>
        </td>
      </tr>
    `).join('');
  } catch (e) {
    console.warn('No se pudieron cargar últimas ventas', e);
  }
}

const analyticsState = { section: 'ventas', mode: 'top', timeframe: 'dia', data: { ventasCat: [], inventarioCat: [], clientes: [], pedidos: [], pagos: [], ventasList: [] } };
const ANALYTICS_LIMIT = 10;

function sliceTop(arr, key) { const a = [...arr].sort((x,y)=>Number(y[key]||0)-Number(x[key]||0)); return a.slice(0,ANALYTICS_LIMIT); }
function sliceBottom(arr, key) { const a = [...arr].sort((x,y)=>Number(x[key]||0)-Number(y[key]||0)); return a.slice(0,ANALYTICS_LIMIT); }

async function loadAnalyticsData() {
  try {
    const ventasCat = await getData('/api/dashboard/charts/ventas_por_categoria');
    analyticsState.data.ventasCat = Array.isArray(ventasCat) ? ventasCat.map(v=>({ label: String(v.categoria||`ID ${v.id_categoria}`), ingresos: Number(v.ingresos||0), cantidad: Number(v.cantidad||0) })) : [];
  } catch { analyticsState.data.ventasCat = []; }
  try {
    const invCat = await getData('/api/dashboard/charts/inventario_por_categoria');
    analyticsState.data.inventarioCat = Array.isArray(invCat) ? invCat.map(v=>({ label: String(v.categoria||`ID ${v.id_categoria}`), valor: Number(v.valor||0), unidades: Number(v.unidades||0) })) : [];
  } catch { analyticsState.data.inventarioCat = []; }
  try {
    const topProd = await getData('/api/dashboard/charts/top_productos?limite=50');
    analyticsState.data.topProductos = Array.isArray(topProd) ? topProd.map(p=>({ label: String(p.nombre||`ID ${p.id_producto}`), unidades: Number(p.unidades||0) })) : [];
  } catch { analyticsState.data.topProductos = []; }
  try {
    const ventas = await getData('/api/ventas?limit=500');
    const arr = Array.isArray(ventas) ? ventas : [];
    analyticsState.data.ventasList = arr;
    const porUsuario = {};
    const porEstado = {};
    const porPago = [];
    arr.forEach(v=>{ const u = String(v.usuario||'Invitado'); porUsuario[u]=(porUsuario[u]||0)+1; const e = String(v.estado||'pendiente'); porEstado[e]=(porEstado[e]||0)+1; porPago.push({ label: `#${v.id_venta}`, monto: Number(v.total_venta||0) }); });
    analyticsState.data.clientes = Object.entries(porUsuario).map(([label,valor])=>({ label, valor }));
    analyticsState.data.pedidos = Object.entries(porEstado).map(([label,valor])=>({ label, valor }));
    analyticsState.data.pagos = porPago;
  } catch { analyticsState.data.clientes=[]; analyticsState.data.pedidos=[]; analyticsState.data.pagos=[]; }
  try {
    const visitas = await getData('/api/analytics/visitas?dias=30');
    analyticsState.data.visitasMes = Array.isArray(visitas) ? visitas.map(v=>({ fecha: String(v.fecha), visitas: Number(v.visitas||0) })) : [];
  } catch { analyticsState.data.visitasMes = []; }
  try {
    const usuarios = await getData('/api/usuarios/');
    analyticsState.data.clientesMes = Array.isArray(usuarios) ? usuarios.filter(u=>{
      const d = new Date(u.fecha_creacion || u.created_at || u.fecha_registro || 0);
      const now = new Date();
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
    }).length : 0;
  } catch { analyticsState.data.clientesMes = 0; }
}

function drawSectionChart() {
  const s = analyticsState.section;
  const m = analyticsState.mode;
  const elId = s==='ventas'?'chartSectVentas':s==='clientes'?'chartSectClientes':s==='inventario'?'chartSectInventario':s==='pedidos'?'chartSectPedidos':'chartSectPagos';
  const el = document.getElementById(elId);
  if (!el) return;
  const toDataTable = (cols, rows)=> window.google.visualization.arrayToDataTable([cols, ...rows]);
  let dt; let options={ legend:{position:'bottom'} };
  if (s==='ventas') {
    const rows = groupVentasByTime(analyticsState.timeframe);
    const sliced = m==='top'?sliceTop(rows,'valor'):sliceBottom(rows,'valor');
    dt = toDataTable(['Tiempo','Ingresos'], sliced.map(r=>[r.label, r.valor]));
    new window.google.visualization.LineChart(el).draw(dt, options);
  } else if (s==='clientes') {
    const src = analyticsState.data.clientes || [];
    const sliced = m==='top'?sliceTop(src,'valor'):sliceBottom(src,'valor');
    dt = toDataTable(['Cliente','Ventas'], sliced.map(r=>[r.label, r.valor]));
    new window.google.visualization.BarChart(el).draw(dt, options);
  } else if (s==='inventario') {
    const src = analyticsState.data.inventarioCat || [];
    const sliced = m==='top'?sliceTop(src,'valor'):sliceBottom(src,'valor');
    dt = toDataTable(['Categoría','Valor'], sliced.map(r=>[r.label, r.valor]));
    new window.google.visualization.PieChart(el).draw(dt, { ...options, pieHole: 0.35 });
  } else if (s==='pedidos') {
    const src = analyticsState.data.pedidos || [];
    const sliced = m==='top'?sliceTop(src,'valor'):sliceBottom(src,'valor');
    dt = toDataTable(['Estado','Cantidad'], sliced.map(r=>[r.label, r.valor]));
    new window.google.visualization.PieChart(el).draw(dt, { ...options, pieHole: 0.35 });
  } else {
    const src = analyticsState.data.pagos || [];
    const sliced = m==='top'?sliceTop(src,'monto'):sliceBottom(src,'monto');
    dt = toDataTable(['Venta','Monto'], sliced.map(r=>[r.label, r.monto]));
    new window.google.visualization.BarChart(el).draw(dt, options);
  }
}

function setSection(section) {
  analyticsState.section = section;
  const ids = ['chartSectVentas','chartSectClientes','chartSectInventario','chartSectPedidos','chartSectPagos'];
  ids.forEach(id=>{ const el = document.getElementById(id); if (!el) return; el.classList.toggle('hidden', id !== (section==='ventas'?ids[0]:section==='clientes'?ids[1]:section==='inventario'?ids[2]:section==='pedidos'?ids[3]:ids[4])); });
  drawSectionChart();
}

function setMode(mode) {
  analyticsState.mode = mode;
  const topBtn = document.getElementById('tabModeTop');
  const bottomBtn = document.getElementById('tabModeBottom');
  if (topBtn && bottomBtn) {
    if (mode==='top') { topBtn.classList.add('bg-green-600','text-white'); topBtn.classList.remove('bg-gray-200','text-gray-800'); bottomBtn.classList.add('bg-gray-200','text-gray-800'); bottomBtn.classList.remove('bg-green-600','text-white'); }
    else { bottomBtn.classList.add('bg-green-600','text-white'); bottomBtn.classList.remove('bg-gray-200','text-gray-800'); topBtn.classList.add('bg-gray-200','text-gray-800'); topBtn.classList.remove('bg-green-600','text-white'); }
  }
  drawSectionChart();
}

async function initApartadosAnalytics() {
  await ensureGoogleChartsReady();
  await loadAnalyticsData();
  // Ventas controls
  const vTop = document.getElementById('ventasModeTop'); const vBottom = document.getElementById('ventasModeBottom');
  if (vTop) vTop.onclick = ()=>{ analyticsApartados.ventas.mode='top'; toggleModeButtons(vTop, vBottom); drawApartadoVentasPorDia(); drawApartadoVentasTopProductos(); drawApartadoVentasIngresosCategoria(); };
  if (vBottom) vBottom.onclick = ()=>{ analyticsApartados.ventas.mode='bottom'; toggleModeButtons(vTop, vBottom); drawApartadoVentasPorDia(); drawApartadoVentasTopProductos(); drawApartadoVentasIngresosCategoria(); };
  toggleModeButtons(vTop, vBottom);

  // Clientes controls
  const cTop = document.getElementById('clientesModeTop'); const cBottom = document.getElementById('clientesModeBottom');
  if (cTop) cTop.onclick = ()=>{ analyticsApartados.clientes.mode='top'; toggleModeButtons(cTop, cBottom); drawApartadoClientes(); };
  if (cBottom) cBottom.onclick = ()=>{ analyticsApartados.clientes.mode='bottom'; toggleModeButtons(cTop, cBottom); drawApartadoClientes(); };
  toggleModeButtons(cTop, cBottom);

  // Inventario controls
  const iTop = document.getElementById('inventarioModeTop'); const iBottom = document.getElementById('inventarioModeBottom');
  if (iTop) iTop.onclick = ()=>{ analyticsApartados.inventario.mode='top'; toggleModeButtons(iTop, iBottom); drawApartadoInventario(); };
  if (iBottom) iBottom.onclick = ()=>{ analyticsApartados.inventario.mode='bottom'; toggleModeButtons(iTop, iBottom); drawApartadoInventario(); };
  toggleModeButtons(iTop, iBottom);

  // Pedidos controls
  const pTop = document.getElementById('pedidosModeTop'); const pBottom = document.getElementById('pedidosModeBottom');
  if (pTop) pTop.onclick = ()=>{ analyticsApartados.pedidos.mode='top'; toggleModeButtons(pTop, pBottom); drawApartadoPedidos(); };
  if (pBottom) pBottom.onclick = ()=>{ analyticsApartados.pedidos.mode='bottom'; toggleModeButtons(pTop, pBottom); drawApartadoPedidos(); };
  toggleModeButtons(pTop, pBottom);

  // Pagos controls
  const paTop = document.getElementById('pagosModeTop'); const paBottom = document.getElementById('pagosModeBottom');
  if (paTop) paTop.onclick = ()=>{ analyticsApartados.pagos.mode='top'; toggleModeButtons(paTop, paBottom); drawApartadoPagos(); };
  if (paBottom) paBottom.onclick = ()=>{ analyticsApartados.pagos.mode='bottom'; toggleModeButtons(paTop, paBottom); drawApartadoPagos(); };
  toggleModeButtons(paTop, paBottom);

  // Initial draw
  drawApartadoVentasPorDia();
  drawApartadoVentasTopProductos();
  drawApartadoVentasIngresosCategoria();
  drawApartadoClientes();
  drawApartadoInventario();
  drawApartadoPedidos();
  drawApartadoPagos();
  drawResumenMetrics();
  drawVisitasMes();
}

const analyticsApartados = { ventas:{ timeframe:'dia', mode:'top' }, clientes:{ mode:'top' }, inventario:{ mode:'top' }, pedidos:{ mode:'top' }, pagos:{ mode:'top' } };

function toggleModeButtons(btnTop, btnBottom) {
  if (!btnTop || !btnBottom) return;
  const topActive = btnTop === document.activeElement || btnTop.classList.contains('bg-green-600');
  btnTop.classList.add('bg-green-600','text-white'); btnTop.classList.remove('bg-gray-200','text-gray-800');
  btnBottom.classList.add('bg-gray-200','text-gray-800'); btnBottom.classList.remove('bg-green-600','text-white');
}
function toggleTimeButtons(bDia, bSem, bMes) {
  [bDia,bSem,bMes].forEach((b,i)=>{ if (!b) return; b.classList.add('bg-gray-200','text-gray-800'); b.classList.remove('bg-indigo-600','text-white'); });
  if (bDia) { bDia.classList.add('bg-indigo-600','text-white'); bDia.classList.remove('bg-gray-200','text-gray-800'); }
}

function drawApartadoVentas() {
  const el = document.getElementById('apartadoChartVentas'); if (!el) return;
  const rows = groupVentasByTime(analyticsApartados.ventas.timeframe);
  const sliced = analyticsApartados.ventas.mode==='top'?sliceTop(rows,'valor'):sliceBottom(rows,'valor');
  const dt = window.google.visualization.arrayToDataTable([['Tiempo','Ingresos'], ...sliced.map(r=>[r.label, r.valor])]);
  new window.google.visualization.AreaChart(el).draw(dt, baseChartOptions('#2563eb', true));
}
function drawApartadoClientes() {
  const el = document.getElementById('apartadoChartClientes'); if (!el) return;
  if (!(window.google && window.google.visualization)) return;
  const src = analyticsState.data.clientes || [];
  const sliced = analyticsApartados.clientes.mode==='top'?sliceTop(src,'valor'):sliceBottom(src,'valor');
  const dt = window.google.visualization.arrayToDataTable([['Cliente','Ventas'], ...sliced.map(r=>[r.label, r.valor])]);
  new window.google.visualization.BarChart(el).draw(dt, baseChartOptions('#16a34a', false));
}
function drawApartadoInventario() {
  const el = document.getElementById('apartadoChartInventario'); if (!el) return;
  if (!(window.google && window.google.visualization)) return;
  const src = analyticsState.data.inventarioCat || [];
  const sliced = analyticsApartados.inventario.mode==='top'?sliceTop(src,'valor'):sliceBottom(src,'valor');
  const dt = window.google.visualization.arrayToDataTable([['Categoría','Valor'], ...sliced.map(r=>[r.label, r.valor])]);
  new window.google.visualization.PieChart(el).draw(dt, { legend:{position:'bottom'}, chartArea:{width:'85%',height:'70%'}, backgroundColor:'transparent', colors:['#9333ea'], pieHole:0.35, sliceVisibilityThreshold: 0.02 });
}
function drawApartadoPedidos() {
  const el = document.getElementById('apartadoChartPedidos'); if (!el) return;
  if (!(window.google && window.google.visualization)) return;
  const src = analyticsState.data.pedidos || [];
  const sliced = analyticsApartados.pedidos.mode==='top'?sliceTop(src,'valor'):sliceBottom(src,'valor');
  const dt = window.google.visualization.arrayToDataTable([['Estado','Cantidad'], ...sliced.map(r=>[r.label, r.valor])]);
  new window.google.visualization.PieChart(el).draw(dt, { legend:{position:'bottom'}, chartArea:{width:'85%',height:'70%'}, backgroundColor:'transparent', colors:['#f59e0b'], pieHole:0.35, sliceVisibilityThreshold: 0.02 });
}
function drawApartadoPagos() {
  const el = document.getElementById('apartadoChartPagos'); if (!el) return;
  if (!(window.google && window.google.visualization)) return;
  const src = analyticsState.data.pagos || [];
  const sliced = analyticsApartados.pagos.mode==='top'?sliceTop(src,'monto'):sliceBottom(src,'monto');
  const dt = window.google.visualization.arrayToDataTable([['Venta','Monto'], ...sliced.map(r=>[r.label, r.monto])]);
  new window.google.visualization.BarChart(el).draw(dt, baseChartOptions('#ef4444', true));
}

function drawApartadoVentasTopProductos() {
  const el = document.getElementById('apartadoChartVentasTopProductos'); if (!el) return;
  if (!(window.google && window.google.visualization)) return;
  const src = analyticsState.data.topProductos || [];
  const sliced = analyticsApartados.ventas.mode==='top'?sliceTop(src,'unidades'):sliceBottom(src,'unidades');
  const rows = sliced.length ? sliced.map(r=>[r.label, r.unidades]) : [['Sin datos', 0]];
  const dt = window.google.visualization.arrayToDataTable([['Producto','Unidades'], ...rows]);
  new window.google.visualization.BarChart(el).draw(dt, baseChartOptions('#9333ea', false));
}

function drawApartadoVentasIngresosCategoria() {
  const el = document.getElementById('apartadoChartVentasIngresosCategoria'); if (!el) return;
  if (!(window.google && window.google.visualization)) return;
  const src = analyticsState.data.ventasCat || [];
  const sliced = analyticsApartados.ventas.mode==='top'?sliceTop(src,'ingresos'):sliceBottom(src,'ingresos');
  const rows = sliced.length ? sliced.map(r=>[r.label, r.ingresos]) : [['Sin datos', 0]];
  const dt = window.google.visualization.arrayToDataTable([['Categoría','Ingresos'], ...rows]);
  new window.google.visualization.PieChart(el).draw(dt, { legend:{position:'bottom'}, chartArea:{width:'85%',height:'70%'}, backgroundColor:'transparent', colors:['#2563eb'], pieHole:0.35, sliceVisibilityThreshold: 0.02 });
}

function baseChartOptions(color, currency) {
  return {
    legend: { position: 'bottom' },
    chartArea: { width: '85%', height: '70%' },
    backgroundColor: 'transparent',
    colors: [color],
    hAxis: { textStyle: { color: '#6b7280' }, gridlines: { color: '#f3f4f6' } },
    vAxis: { textStyle: { color: '#6b7280' }, gridlines: { color: '#e5e7eb' }, format: currency ? 'short' : '' },
    tooltip: { textStyle: { color: '#111827' } },
    annotations: { alwaysOutside: false, textStyle: { color: '#374151' } },
    bar: { groupWidth: '70%' }
  };
}

function drawResumenMetrics() {
  const carritosEl = document.getElementById('metricCarritosAbandonados');
  const clientesMesEl = document.getElementById('metricClientesMes');
  const stockTotalEl = document.getElementById('metricStockTotal');
  const agotadosEl = document.getElementById('metricAgotados');
  const valorInvEl = document.getElementById('metricValorInventario');
  const transFallEl = document.getElementById('metricTransaccionesFallidas');
  try {
    const nowMs = Date.now();
    const pendientes = (analyticsState.data.ventasList||[]).filter(v=> String(v.estado||'').toLowerCase()==='pendiente');
    const abandonados = pendientes.filter(v=>{ const t = new Date(v.fecha_venta||v.created_at||0).getTime(); return (nowMs - t) > (24*3600*1000); }).length;
    if (carritosEl) carritosEl.textContent = String(abandonados);
  } catch {}
  try { if (clientesMesEl) clientesMesEl.textContent = String(analyticsState.data.clientesMes||0); } catch {}
  try {
    const inv = analyticsState.data.inventarioCat||[];
    const stockTotal = inv.reduce((acc,i)=> acc + Number(i.unidades||0), 0);
    const valorTotal = inv.reduce((acc,i)=> acc + Number(i.valor||0), 0);
    if (stockTotalEl) stockTotalEl.textContent = String(stockTotal);
    if (valorInvEl) valorInvEl.textContent = new Intl.NumberFormat('es-CL',{style:'currency',currency:'CLP',maximumFractionDigits:0}).format(valorTotal);
  } catch {}
  try {
    const agotados = (analyticsState.data.inventarioCat||[]).filter(i=> Number(i.unidades||0)===0).length;
    if (agotadosEl) agotadosEl.textContent = String(agotados);
  } catch {}
  try {
    const fallidas = (analyticsState.data.pedidos||[]).filter(p=> String(p.label||'').toLowerCase().includes('rechaz')).reduce((a,b)=> a + Number(b.valor||0), 0);
    if (transFallEl) transFallEl.textContent = String(fallidas);
  } catch {}
}

function drawVisitasMes() {
  const el = document.getElementById('chartVisitasMes'); if (!el) return;
  const src = analyticsState.data.visitasMes||[];
  const rows = src.length? src.map(v=>[v.fecha, v.visitas]) : buildEmptyDates(30).map(d=>[d,0]);
  const dt = window.google.visualization.arrayToDataTable([['Fecha','Visitas'], ...rows]);
  new window.google.visualization.LineChart(el).draw(dt, { legend:{position:'bottom'}, chartArea:{width:'85%',height:'70%'}, colors:['#2563eb'] });
}

function buildEmptyDates(days) {
  const out=[]; const now=new Date(); const start=new Date(now); start.setDate(now.getDate()-(days-1));
  for(let i=0;i<days;i++){ const d=new Date(start); d.setDate(start.getDate()+i); out.push(d.toLocaleDateString('es-CL')); }
  return out;
}

function groupVentasByTime(tf) {
  const arr = analyticsState.data.ventasList || [];
  const now = new Date();
  const start = new Date(now);
  let buckets = [];
  if (tf==='dia') {
    start.setHours(0,0,0,0);
    for (let h=0; h<24; h++) buckets.push({ key: h, label: `${String(h).padStart(2,'0')}:00`, valor: 0 });
    arr.forEach(v=>{ const d = new Date(v.fecha_venta); if (d.toDateString() === now.toDateString()) { const h=d.getHours(); buckets[h].valor += Number(v.total_venta||0); } });
    return buckets;
  }
  if (tf==='semana') {
    start.setDate(now.getDate()-6); start.setHours(0,0,0,0);
    for (let i=0;i<7;i++){ const d=new Date(start); d.setDate(start.getDate()+i); buckets.push({ key: d.toISOString().slice(0,10), label: d.toLocaleDateString('es-CL',{weekday:'short', day:'2-digit'}), valor:0 }); }
    arr.forEach(v=>{ const d=new Date(v.fecha_venta); if (d>=start && d<=now){ const k=d.toISOString().slice(0,10); const b=buckets.find(x=>x.key===k); if (b) b.valor += Number(v.total_venta||0);} });
    return buckets;
  }
  // mes (últimos 30 días)
  start.setDate(now.getDate()-29); start.setHours(0,0,0,0);
  for (let i=0;i<30;i++){ const d=new Date(start); d.setDate(start.getDate()+i); buckets.push({ key: d.toISOString().slice(0,10), label: d.toLocaleDateString('es-CL',{month:'2-digit', day:'2-digit'}), valor:0 }); }
  arr.forEach(v=>{ const d=new Date(v.fecha_venta); if (d>=start && d<=now){ const k=d.toISOString().slice(0,10); const b=buckets.find(x=>x.key===k); if (b) b.valor += Number(v.total_venta||0);} });
  return buckets;
}
async function drawApartadoVentasPorDia() {
  const el = document.getElementById('apartadoChartVentasPorDia'); if (!el) return;
  try {
    let ventasDia = await getData('/api/dashboard/charts/ventas_por_dia');
    if (!Array.isArray(ventasDia) || ventasDia.length === 0) {
      ventasDia = [{ fecha: new Date().toLocaleDateString('es-CL'), ingresos: 0, cantidad: 0 }];
    }
    await ensureGoogleChartsReady();
    const rows = ventasDia.map(v => [String(v.fecha), Number(v.ingresos || 0), Number(v.cantidad || 0)]);
    const dataTable = window.google.visualization.arrayToDataTable([
      ['Fecha', 'Ingresos', 'Cantidad'],
      ...rows
    ]);
    const options = {
      legend: { position: 'bottom' },
      series: { 0: { targetAxisIndex: 0, color: '#2563eb' }, 1: { targetAxisIndex: 1, color: '#16a34a' } },
      vAxes: { 0: { format: 'short' }, 1: { format: '' } },
      chartArea: { width: '85%', height: '70%' },
      backgroundColor: 'transparent'
    };
    new window.google.visualization.LineChart(el).draw(dataTable, options);
  } catch (e) {
    console.warn('[Charts] Error Ventas por día apartado', e);
  }
}

function redrawApartados() {
  try {
    drawApartadoVentasPorDia();
    drawApartadoVentasTopProductos();
    drawApartadoVentasIngresosCategoria();
    drawApartadoClientes();
    drawApartadoInventario();
    drawApartadoPedidos();
    drawApartadoPagos();
  } catch {}
}

function setupResizeRedraw() {
  let t;
  window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(redrawApartados, 250); });
}
