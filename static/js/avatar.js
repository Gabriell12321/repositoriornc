// Avatar Picker - IPPEL
(function(){
  const API = '/api/user/avatar';
  const CLS = {
    modal: 'avatarModal',
    avatar: 'userAvatar'
  };

  function ensureModal(){
    if(document.getElementById(CLS.modal)) return;
    const el = document.createElement('div');
    el.id = CLS.modal;
    el.innerHTML = `
      <div class="box">
        <div class="title">Escolha seu avatar</div>
        <div class="grid" id="avaGrid"></div>
        <div class="actions">
          <button class="btn ghost" id="avaClose">Cancelar</button>
        </div>
      </div>`;
    document.body.appendChild(el);
    el.addEventListener('click', (e)=>{ if(e.target.id===CLS.modal) hide(); });
    document.getElementById('avaClose').addEventListener('click', hide);

    const presets = [
      'ava-ippel','ava-galaxy','ava-ocean','ava-rainbow','ava-neon','ava-sunset','ava-wave','ava-pulse'
    ];
    const grid = document.getElementById('avaGrid');
    presets.forEach(k=>{
      const item = document.createElement('div');
      item.className = 'item';
      item.innerHTML = `<div class="ava ${k}" title="${k}"></div>`;
      item.addEventListener('click', ()=> select(k));
      grid.appendChild(item);
    });
  }

  function show(){ ensureModal(); document.getElementById(CLS.modal).style.display='flex'; }
  function hide(){ const m=document.getElementById(CLS.modal); if(m) m.style.display='none'; }

  async function select(key){
    try{
      const resp = await fetch(API, { method:'POST', headers:{'Content-Type':'application/json'}, credentials:'include', body: JSON.stringify({ avatar:key }) });
      const data = await resp.json();
      if(!data.success) throw new Error(data.message||'Falha ao salvar');
      applyToHeader(key);
      hide();
    }catch(e){ alert('Erro ao salvar avatar: '+e.message); }
  }

  function applyToHeader(key){
    const el = document.getElementById(CLS.avatar);
    if(!el) return;
    el.className = `user-avatar ava ${key||'ava-ippel'}`;
    // keep initial if showing letter
    if(!el.dataset.initial){ el.textContent = (window.__USER_NAME__||'U').charAt(0).toUpperCase(); }
  }

  function attach(){
    const el = document.getElementById(CLS.avatar);
    if(!el) return;
    el.addEventListener('click', show);
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    attach();
  });

  // Expose
  window.IPPELAvatar = { show, hide, applyToHeader };
})();
