import { API_URL, corsConfig, API_TIMEOUT } from '../utils/config.js';
import { digitsOnly, formatRutFromDigits, formatRutUI, cleanRutInput } from '../utils/rut.js';
corsConfig.headers = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json' };

async function checkServerAvailability() {
  try { const c = new AbortController(); const t = setTimeout(() => c.abort(), API_TIMEOUT/2);
    const r = await fetch(`${API_URL}/health`, { method:'GET', signal:c.signal }); clearTimeout(t);
    return { available: r.ok }; } catch { return { available: false }; }
}

function showStatus(m, type='info'){ const el=document.getElementById('statusMessage'); if(!el) return; el.textContent=m; el.className='mt-2 text-sm text-center'; el.classList.add(type==='error'?'text-red-600':type==='success'?'text-green-600':type==='warning'?'text-yellow-600':'text-gray-600'); el.classList.remove('hidden'); }
function showLoading(b){ const btn=document.getElementById('loginButton'); const sp=document.getElementById('loadingSpinner'); if(!btn||!sp) return; if(b){ sp.classList.remove('hidden'); btn.disabled=true; btn.classList.add('opacity-75'); } else { sp.classList.add('hidden'); btn.disabled=false; btn.classList.remove('opacity-75'); } }

async function handleLogin(e){ e.preventDefault(); const usernameInput=(document.getElementById('username')?.value||'').trim(); const baseRut = usernameInput.includes('-') ? usernameInput.split('-')[0] : usernameInput; const username = digitsOnly(baseRut); const password=document.getElementById('password')?.value||''; if(!username||!password){ showStatus('Por favor, ingrese RUT y contraseña','error'); return; }
  showLoading(true); showStatus('Verificando credenciales...','info'); const ok=await checkServerAvailability(); if(!ok.available){ showStatus('No se pudo verificar el servidor. Intentando iniciar sesión...','info'); }
  try{ const controller=new AbortController(); const timeoutId=setTimeout(()=>controller.abort(),10000);
    const rawRut = (document.getElementById('username')?.value||'').trim();
    const rutLimpio = cleanRutInput(rawRut);
    const formData = new URLSearchParams();
    formData.append('username', rutLimpio);
    formData.append('password', password);
    formData.append('grant_type','password');
    const opts = { method:'POST', body:formData, signal:controller.signal, mode:corsConfig.mode, credentials:corsConfig.credentials, headers: { 'Content-Type':'application/x-www-form-urlencoded', 'Accept':'application/json' } };
    let response = await fetch(`${API_URL}/auth/login`, opts).catch(()=>null);
    if (!response || !response.ok) {
      response = await fetch(`${API_URL}/auth/login-cliente`, opts).catch(()=>null);
    }
    if (response && !response.ok) {
      const formDataRut = new URLSearchParams();
      formDataRut.append('rut', rutLimpio);
      formDataRut.append('password', password);
      formDataRut.append('grant_type','password');
      const optsRut = { ...opts, body: formDataRut };
      let r2 = await fetch(`${API_URL}/auth/login-cliente`, optsRut).catch(()=>null);
      if (!r2 || !r2.ok) {
        r2 = await fetch(`${API_URL}/auth/login`, optsRut).catch(()=>null);
      }
      response = r2;
    }
    clearTimeout(timeoutId);
    if(!response || !response.ok){ const txt = response ? (await response.text()) : ''; let msg = response && response.status===401 ? 'Credenciales incorrectas' : (response && response.status===422 ? 'Datos no procesables. Revisa formato de RUT y contraseña.' : `Error de autenticación (${response ? response.status : 'sin respuesta'})`); try{ const j=JSON.parse(txt); if(j?.detail) msg = typeof j.detail==='string'? j.detail : JSON.stringify(j.detail); }catch{} showStatus(msg,'error'); showLoading(false); return; }
    const data=await response.json(); const user={ id_usuario:data.id_usuario, nombre:data.nombre, apellido:data.apellido??data.apellidos??data.last_name, email:data.email??data.correo??data.mail, telefono:data.telefono??data.phone??data.celular, rut:data.rut ?? username, rol:(data.role||data.rol||'cliente') };
    const workerRoles=['administrador','admin','trabajador','vendedor','bodeguero']; const isWorker=workerRoles.includes(String(user.rol).toLowerCase());
    localStorage.setItem('isLoggedIn','true'); localStorage.setItem('token',data.access_token); localStorage.setItem('user',JSON.stringify(user)); localStorage.setItem('role',user.rol); localStorage.setItem('nombreUsuario', user.nombre || formatRutFromDigits(user.rut));
    document.cookie = `isLoggedIn=true; path=/; SameSite=Lax`;
    document.cookie = `role=${encodeURIComponent(user.rol)}; path=/; SameSite=Lax`;
    try{
      const headers={ 'Content-Type':'application/json','Authorization':`Bearer ${data.access_token}` };
      const paths=['/api/usuarios/me','/api/users/me','/api/me',`/api/usuarios/${user.id_usuario}`];
      let info=null;
      for(const p of paths){ try{ const r=await fetch(`${API_URL.replace(/\/api$/,'')}${p}`,{ headers }); if(r&&r.ok){ info=await r.json(); break; } }catch{} }
      if(info){
        const apellido = info.apellido ?? info.apellidos ?? info.last_name;
        const email = info.email ?? info.correo ?? info.mail;
        const telefono = info.telefono ?? info.phone ?? info.celular;
        const merged = { ...user };
        if (apellido !== undefined) merged.apellido = apellido;
        if (email !== undefined) merged.email = email;
        if (telefono !== undefined) merged.telefono = telefono;
        localStorage.setItem('user', JSON.stringify(merged));
      }
    }catch{}
    showStatus('Autenticación exitosa. Redirigiendo...','success'); setTimeout(()=>{ window.location.href = isWorker ? '/admin' : '/'; },800);
  } catch(err){ showLoading(false); showStatus('Error de autenticación','error'); }
}

document.addEventListener('DOMContentLoaded', async ()=>{ const form=document.getElementById('loginForm'); const label=document.getElementById('usernameLabel'); const input=document.getElementById('username'); const create=document.getElementById('createAccountContainer'); if(label) label.textContent='RUT'; if(input){ input.placeholder='20.347.793-7'; input.addEventListener('input', (e)=>{ const formatted = formatRutUI(e.target.value); e.target.value = formatted; e.target.selectionStart = e.target.selectionEnd = formatted.length; }); } if(create) create.classList.remove('hidden'); if(form) form.addEventListener('submit', handleLogin); });
