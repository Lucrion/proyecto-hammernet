// Script para probar la conectividad con la API de producción
// Ejecutar con: node test_production_api.js

const https = require('https');
const http = require('http');

// URLs a probar
const PRODUCTION_API = 'https://hammernet-backend.onrender.com';
const LOCAL_API = 'http://localhost:8000';

// Función para hacer peticiones HTTP/HTTPS
function makeRequest(url, path = '/productos') {
  return new Promise((resolve, reject) => {
    const fullUrl = url + path;
    const isHttps = url.startsWith('https');
    const client = isHttps ? https : http;
    
    console.log(`\n🔍 Probando: ${fullUrl}`);
    
    const startTime = Date.now();
    
    const req = client.get(fullUrl, (res) => {
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve({
            status: res.statusCode,
            responseTime,
            dataLength: data.length,
            productsCount: Array.isArray(jsonData) ? jsonData.length : 'No es array',
            headers: res.headers
          });
        } catch (e) {
          resolve({
            status: res.statusCode,
            responseTime,
            dataLength: data.length,
            error: 'Respuesta no es JSON válido',
            rawData: data.substring(0, 200) + (data.length > 200 ? '...' : '')
          });
        }
      });
    });
    
    req.on('error', (error) => {
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      reject({
        error: error.message,
        responseTime,
        code: error.code
      });
    });
    
    req.setTimeout(10000, () => {
      req.destroy();
      reject({
        error: 'Timeout - La petición tardó más de 10 segundos',
        responseTime: 10000
      });
    });
  });
}

// Función principal
async function testAPIs() {
  console.log('🚀 Iniciando pruebas de conectividad API...');
  console.log('=' .repeat(50));
  
  // Probar API de producción
  try {
    const prodResult = await makeRequest(PRODUCTION_API);
    console.log('✅ API de Producción - ÉXITO');
    console.log(`   Status: ${prodResult.status}`);
    console.log(`   Tiempo de respuesta: ${prodResult.responseTime}ms`);
    console.log(`   Productos encontrados: ${prodResult.productsCount}`);
    console.log(`   Tamaño de respuesta: ${prodResult.dataLength} bytes`);
    
    if (prodResult.headers['access-control-allow-origin']) {
      console.log(`   CORS habilitado: ${prodResult.headers['access-control-allow-origin']}`);
    }
  } catch (error) {
    console.log('❌ API de Producción - ERROR');
    console.log(`   Error: ${error.error}`);
    console.log(`   Código: ${error.code || 'N/A'}`);
    console.log(`   Tiempo: ${error.responseTime}ms`);
  }
  
  // Probar API local (si está disponible)
  try {
    const localResult = await makeRequest(LOCAL_API);
    console.log('\n✅ API Local - ÉXITO');
    console.log(`   Status: ${localResult.status}`);
    console.log(`   Tiempo de respuesta: ${localResult.responseTime}ms`);
    console.log(`   Productos encontrados: ${localResult.productsCount}`);
  } catch (error) {
    console.log('\n⚠️  API Local - NO DISPONIBLE (esto es normal en producción)');
    console.log(`   Error: ${error.error}`);
  }
  
  // Probar endpoint específico de producto
  console.log('\n🔍 Probando endpoint de producto específico...');
  try {
    const productResult = await makeRequest(PRODUCTION_API, '/productos/1');
    console.log('✅ Endpoint de producto específico - ÉXITO');
    console.log(`   Status: ${productResult.status}`);
    console.log(`   Tiempo de respuesta: ${productResult.responseTime}ms`);
  } catch (error) {
    console.log('❌ Endpoint de producto específico - ERROR');
    console.log(`   Error: ${error.error}`);
  }
  
  console.log('\n' + '=' .repeat(50));
  console.log('🏁 Pruebas completadas');
  console.log('\n💡 Recomendaciones:');
  console.log('   - Si la API de producción falla, verifica que el backend esté desplegado');
  console.log('   - Si hay errores de CORS, verifica la configuración del backend');
  console.log('   - Si el tiempo de respuesta es muy alto (>5000ms), puede haber problemas de red');
}

// Ejecutar las pruebas
testAPIs().catch(console.error);