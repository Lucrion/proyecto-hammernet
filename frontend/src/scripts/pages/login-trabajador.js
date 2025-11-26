import { API_URL, corsConfig, API_TIMEOUT } from '../utils/config.js';
import { digitsOnly, formatRutFromDigits } from '../utils/rut.js';
corsConfig.headers = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json' };

async function checkServerAvailability() { try { const c=new AbortController(); const t=setTimeout(()=>c.abort(), API_TIMEOUT/2); const r=await fetch(`${API_URL}/health`,{method:'GET',signal:c.signal}); clearTimeout(t); return {available:r.ok}; } catch { return {available:false}; } }
function showStatus(m,type='info'){ const el=document.getElementById('statusMessage'); if(!el) return; el.textContent=m; el.className='mt-2 text-sm text-center'; el.classList.add(type==='error'?'text-red-600':type==='success'?'text-green-600':type==='warning'?'text-yellow-600':'text-gray-600'); el.classList.remove('hidden'); }
function showLoading(b){ const btn=document.getElementById('loginButton'); const sp=document.getElementById('loadingSpinner'); if(!btn||!sp) return; if(b){ sp.classList.remove('hidden'); btn.disabled=true; btn.classList.add('opacity-75'); } else { sp.classList.add('hidden'); btn.disabled=false; btn.classList.remove('opacity-75'); } }

async function handleLogin(e){ e.preventDefault(); const usernameInput=(document.getElementById('username')?.value||'').trim(); const baseRut = usernameInput.includes('-') ? usernameInput.split('-')[0] : usernameInput; const username = digitsOnly(baseRut); const password=document.getElementById('password')?.value||''; if(!username||!password){ showStatus('Por favor, ingrese RUT y contraseña','error'); return; }
  showLoading(true); showStatus('Verificando credenciales...','info'); const ok=await checkServerAvailability(); if(!ok.available){ showStatus('El servidor no está disponible. Intente más tarde.','error'); showLoading(false); return; }
  try{ const controller=new AbortController(); const timeoutId=setTimeout(()=>controller.abort(),10000); const formData=new URLSearchParams(); formData.append('username', username); formData.append('password', password); formData.append('grant_type','password'); const opts={ method:'POST', body:formData, signal:controller.signal, ...corsConfig };
    const response=await fetch(`${API_URL}/auth/login-trabajador`, opts); clearTimeout(timeoutId);
    if(!response.ok){ const txt=await response.text(); let msg = response.status===403 ? 'Acceso restringido a trabajadores' : (response.status===401 ? 'Credenciales incorrectas' : `Error de autenticación (${response.status})`); try{ const j=JSON.parse(txt); if(j?.detail) msg = typeof j.detail==='string'? j.detail : JSON.stringify(j.detail); }catch{} showStatus(msg,'error'); showLoading(false); return; }
    const data=await response.json(); const user={ id_usuario:data.id_usuario, nombre:data.nombre, rut:data.rut ?? username, rol:data.role||'trabajador' };
    sessionStorage.setItem('isLoggedIn','true'); sessionStorage.setItem('token',data.access_token); sessionStorage.setItem('user',JSON.stringify(user)); sessionStorage.setItem('role',user.rol); sessionStorage.setItem('nombreUsuario', user.nombre || formatRutFromDigits(user.rut));
    showStatus('Autenticación exitosa. Redirigiendo...','success'); setTimeout(()=>{ window.location.href='/admin'; },800);
  } catch(err){ showLoading(false); showStatus('Error de autenticación','error'); }
}

document.addEventListener('DOMContentLoaded', async ()=>{ const form=document.getElementById('loginForm'); const label=document.getElementById('usernameLabel'); const input=document.getElementById('username'); const create=document.getElementById('createAccountContainer'); if(label) label.textContent='RUT'; if(input) input.placeholder='20.347.793-7'; if(create) create.classList.add('hidden'); if(form) form.addEventListener('submit', handleLogin); });

