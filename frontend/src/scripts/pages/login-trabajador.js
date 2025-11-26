import { API_URL, corsConfig, API_TIMEOUT } from '../scripts/utils/config.js';
import { digitsOnly, formatRutFromDigits, formatRutUI } from '../scripts/utils/rut.js';
corsConfig.headers = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json' };

async function checkServerAvailability() { try { const c=new AbortController(); const t=setTimeout(()=>c.abort(), API_TIMEOUT/2); const r=await fetch(`${API_URL}/health`,{method:'GET',signal:c.signal}); clearTimeout(t); return {available:r.ok}; } catch { return {available:false}; } }
function showStatus(m,type='info'){ const el=document.getElementById('statusMessage'); if(!el) return; el.textContent=m; el.className='mt-2 text-sm text-center'; el.classList.add(type==='error'?'text-red-600':type==='success'?'text-green-600':type==='warning'?'text-yellow-600':'text-gray-600'); el.classList.remove('hidden'); }
function showLoading(b){ const btn=document.getElementById('loginButton'); const sp=document.getElementById('loadingSpinner'); if(!btn||!sp) return; if(b){ sp.classList.remove('hidden'); btn.disabled=true; btn.classList.add('opacity-75'); } else { sp.classList.add('hidden'); btn.disabled=false; btn.classList.remove('opacity-75'); } }

async function handleLogin(e){ e.preventDefault(); const usernameInput=(document.getElementById('username')?.value||'').trim(); const baseRut = usernameInput.includes('-') ? usernameInput.split('-')[0] : usernameInput; const username = digitsOnly(baseRut); const password=document.getElementById('password')?.value||''; if(!username||!password){ showStatus('Por favor, ingrese RUT y contraseña','error'); return; }
  showLoading(true); showStatus('Verificando credenciales...','info'); const ok=await checkServerAvailability(); if(!ok.available){ showStatus('No se pudo verificar el servidor. Intentando iniciar sesión...','info'); }
  try{ const controller=new AbortController(); const timeoutId=setTimeout(()=>controller.abort(),10000);
    const paths=[`${API_URL}/auth/login`, `${API_URL}/auth/login-trabajador`, `${API_URL}/login`, `${API_URL}/auth/token`];
    const attempts=[
      { headers:{ 'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json' }, body:new URLSearchParams({ username, password, grant_type:'password' }) },
      { headers:{ 'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json' }, body:new URLSearchParams({ email: username, password }) },
      { headers:{ 'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json' }, body:new URLSearchParams({ rut: username, password }) },
      { headers:{ 'Content-Type':'application/json','Accept':'application/json' }, body: JSON.stringify({ username, password }) },
      { headers:{ 'Content-Type':'application/json','Accept':'application/json' }, body: JSON.stringify({ email: username, password }) },
      { headers:{ 'Content-Type':'application/json','Accept':'application/json' }, body: JSON.stringify({ rut: username, password }) }
    ];
    let response=null;
    for(const p of paths){
      for(const a of attempts){
        try{ response = await fetch(p, { method:'POST', signal:controller.signal, mode:corsConfig.mode, credentials:corsConfig.credentials, headers:a.headers, body:a.body }); if(response && response.ok) break; }catch{}
      }
      if(response && response.ok) break;
    }
    clearTimeout(timeoutId);
    if(!response || !response.ok){ const txt= response ? (await response.text()) : ''; let msg = response && response.status===401 ? 'Credenciales incorrectas' : `Error de autenticación (${response ? response.status : 'sin respuesta'})`; try{ const j=JSON.parse(txt); if(j?.detail) msg = typeof j.detail==='string'? j.detail : JSON.stringify(j.detail); }catch{} showStatus(msg,'error'); showLoading(false); return; }
    const data=await response.json(); const user={ id_usuario:data.id_usuario, nombre:data.nombre, rut:data.rut ?? username, rol:(data.role||data.rol||'trabajador') };
    const workerRoles=['administrador','admin','trabajador','vendedor','bodeguero']; const isWorker=workerRoles.includes(String(user.rol).toLowerCase());
    sessionStorage.setItem('isLoggedIn','true'); sessionStorage.setItem('token',data.access_token); sessionStorage.setItem('user',JSON.stringify(user)); sessionStorage.setItem('role',user.rol); sessionStorage.setItem('nombreUsuario', user.nombre || formatRutFromDigits(user.rut));
    document.cookie = `isLoggedIn=true; path=/; SameSite=Lax`;
    document.cookie = `role=${encodeURIComponent(user.rol)}; path=/; SameSite=Lax`;
    showStatus('Autenticación exitosa. Redirigiendo...','success'); setTimeout(()=>{ window.location.href = isWorker ? '/admin' : '/'; },800);
  } catch(err){ showLoading(false); showStatus('Error de autenticación','error'); }
}

document.addEventListener('DOMContentLoaded', async ()=>{ const form=document.getElementById('loginForm'); const label=document.getElementById('usernameLabel'); const input=document.getElementById('username'); const create=document.getElementById('createAccountContainer'); if(label) label.textContent='RUT'; if(input){ input.placeholder='20.347.793-7'; input.addEventListener('input', (e)=>{ const formatted = formatRutUI(e.target.value); e.target.value = formatted; e.target.selectionStart = e.target.selectionEnd = formatted.length; }); } if(create) create.classList.add('hidden'); if(form) form.addEventListener('submit', handleLogin); });
