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
    const metrics = await getData('/api/dashboard/metrics');

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

    // Gráficos (si Chart.js está disponible)
    if (window.Chart) {
      // Ventas por día
      try {
        const ventasDia = await getData('/api/dashboard/charts/ventas_por_dia');
        const labels = ventasDia.map(v => v.fecha);
        const ingresos = ventasDia.map(v => v.ingresos);
        const cantidades = ventasDia.map(v => v.cantidad);

        const ctx1 = document.getElementById('chartVentasDia');
        if (ctx1) {
          new window.Chart(ctx1, {
            type: 'line',
            data: {
              labels,
              datasets: [
                {
                  label: 'Ingresos',
                  data: ingresos,
                  borderColor: '#2563eb',
                  backgroundColor: 'rgba(37, 99, 235, 0.2)',
                  yAxisID: 'y',
                },
                {
                  label: 'Cantidad de ventas',
                  data: cantidades,
                  borderColor: '#16a34a',
                  backgroundColor: 'rgba(22, 163, 74, 0.2)',
                  yAxisID: 'y1',
                }
              ]
            },
            options: {
              responsive: true,
              interaction: { mode: 'index', intersect: false },
              stacked: false,
              plugins: {
                tooltip: { callbacks: { label: (ctx) => ctx.dataset.label + ': ' + (ctx.dataset.label.includes('Ingreso') ? formatCurrency(ctx.parsed.y) : ctx.parsed.y ) } },
                legend: { position: 'bottom' }
              },
              scales: {
                y: { type: 'linear', position: 'left', ticks: { callback: (v) => formatCurrency(v) } },
                y1: { type: 'linear', position: 'right', grid: { drawOnChartArea: false } }
              }
            }
          });
        }
      } catch (e) {
        console.warn('No se pudo renderizar gráfico de ventas por día:', e);
      }

      // Top productos
      try {
        const topProductos = await getData('/api/dashboard/charts/top_productos?limite=5');
        const labels2 = topProductos.map(p => p.nombre || `ID ${p.id_producto}`);
        const unidades = topProductos.map(p => p.unidades);

        const ctx2 = document.getElementById('chartTopProductos');
        if (ctx2) {
          new window.Chart(ctx2, {
            type: 'bar',
            data: {
              labels: labels2,
              datasets: [{
                label: 'Unidades vendidas',
                data: unidades,
                backgroundColor: 'rgba(147, 51, 234, 0.4)',
                borderColor: '#9333ea'
              }]
            },
            options: {
              responsive: true,
              plugins: { legend: { position: 'bottom' } },
              scales: { y: { beginAtZero: true } }
            }
          });
        }
      } catch (e) {
        console.warn('No se pudo renderizar gráfico de top productos:', e);
      }
    }
  } catch (error) {
    console.error('Error al cargar dashboard:', error);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const isLoggedIn = sessionStorage.getItem('isLoggedIn') || localStorage.getItem('isLoggedIn');
  const token = sessionStorage.getItem('token') || localStorage.getItem('token');
  if (!isLoggedIn || isLoggedIn !== 'true' || !token) {
    window.location.href = '/login';
    return;
  }
  cargarDashboard();
});