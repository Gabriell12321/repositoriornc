// Avatar Picker - IPPEL
(function(){
  const API = '/api/user/avatar';
  const CLS = {
    modal: 'avatarModal',
    avatar: 'userAvatar'
  };

  function ensureModal(){
    let el = document.getElementById(CLS.modal);
    if(!el){
      el = document.createElement('div');
      el.id = CLS.modal;
      document.body.appendChild(el);
    }
    // Se o container existir mas estiver vazio, preencher conteúdo
    if(!el.querySelector('.box')){
      el.innerHTML = `
      <div class="box">
        <div class="title">Escolha seu avatar</div>
        <div class="grid" id="avaGrid"></div>
        <div style="margin-top:12px; padding-top:10px; border-top:1px solid #eee;">
          <div style="font-weight:700; margin-bottom:6px;">Personalizar</div>
          <div style="display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap:10px; align-items:center;">
            <label>Cores</label>
            <div style="display:flex; gap:8px; align-items:center;">
              <input type="color" id="avaC1" value="#dc3545"/>
              <input type="color" id="avaC2" value="#b21f35"/>
            </div>
            <label>Ângulo</label>
            <input type="range" id="avaAngle" min="0" max="360" value="135"/>
            <label>Raio</label>
            <input type="range" id="avaRadius" min="6" max="24" value="12"/>
            <label>Brilho</label>
            <input type="range" id="avaGlow" min="0" max="0.5" step="0.01" value="0.18"/>
            <label>Velocidade</label>
            <input type="range" id="avaSpeed" min="2" max="12" step="0.5" value="6"/>
          </div>
          <div style="margin-top:10px; display:flex; gap:8px; justify-content:flex-end;">
            <button class="btn ghost" id="avaReset">Resetar</button>
            <button class="btn primary" id="avaSave">Salvar personalizado</button>
          </div>
        </div>
        <div class="actions">
          <button class="btn ghost" id="avaClose">Cancelar</button>
        </div>
      </div>`;
      el.addEventListener('click', (e)=>{ if(e.target.id===CLS.modal) hide(); });
      const closeBtn = document.getElementById('avaClose');
      if(closeBtn) closeBtn.addEventListener('click', hide);

  const presets = [
      'ava-ippel','ava-galaxy','ava-ocean','ava-rainbow','ava-neon','ava-sunset','ava-wave','ava-pulse',
      'ava-forest','ava-lava','ava-mint','ava-sky','ava-rose','ava-candy','ava-silver','ava-carbon'
    ];
      const grid = document.getElementById('avaGrid');
      // Presets com foco corporativo (cores sóbrias)
      const corp = ['ava-corp-blue','ava-corp-slate','ava-corp-navy','ava-corp-teal','ava-corp-gray','ava-corp-indigo','ava-initials'];
      const allPresets = corp.concat(presets);
      const initials = (window.__USER_NAME__||'U U').split(/\s+/).map(p=>p[0]||'').slice(0,2).join('').toUpperCase();
      allPresets.forEach(k=>{
        const item = document.createElement('div');
        item.className = 'item';
        item.innerHTML = `<div class="ava ${k} ${k.startsWith('ava-corp')||k==='ava-initials'?'ava-corp':''}" title="${k}" data-key="${k}"></div>`;
        const avaEl = item.firstElementChild;
        if(avaEl && (k.startsWith('ava-corp') || k==='ava-initials')){
          avaEl.textContent = initials;
        }
        grid.appendChild(item);
      });

      // Avatares de imagem (presets)
      const imgs = [
        'ava1.svg','ava2.svg','ava3.svg','ava4.svg','ava5.svg','ava6.svg','ava7.svg','ava8.svg',
        // DiceBear - Cartoonish
        'https://api.dicebear.com/7.x/adventurer/svg?seed=Alex',
        'https://api.dicebear.com/7.x/adventurer/svg?seed=Maria',
        'https://api.dicebear.com/7.x/adventurer/svg?seed=Carlos',
        'https://api.dicebear.com/7.x/adventurer/svg?seed=Ana'
      ];
      imgs.forEach(name=>{
        const item = document.createElement('div');
        item.className = 'item';
        const src = name.startsWith('http') ? name : `/static/avatars/${name}`;
        item.innerHTML = `<div class="ava ava-image" title="${name}" data-key="ava-image" data-image="${src}"><img src="${src}" alt="avatar"></div>`;
        grid.appendChild(item);
      });

      // Delegação de eventos para cliques (robusta)
      grid.addEventListener('click', (e)=>{
        const ava = e.target.closest('.item .ava');
        if(!ava) return;
        const key = ava.dataset.key || '';
        if(key === 'ava-image'){
          const img = ava.dataset.image;
          if(img) select('ava-image', { image: img });
          return;
        }
        if(key){ select(key); return; }
        // Fallback: tentar inferir pela classe
        const classes = ava.className.split(/\s+/);
        const found = classes.find(c=>c.startsWith('ava-') && c !== 'ava' && c !== 'ava-image' && c !== 'ava-corp');
        if(found) select(found);
      });

    // Personalização
  const c1 = document.getElementById('avaC1');
  const c2 = document.getElementById('avaC2');
  const ang = document.getElementById('avaAngle');
  const rad = document.getElementById('avaRadius');
  const glow = document.getElementById('avaGlow');
  const speed = document.getElementById('avaSpeed');
  const reset = document.getElementById('avaReset');
  const save = document.getElementById('avaSave');

    function applyPreview(){
      document.documentElement.style.setProperty('--ava-c1', c1.value);
      document.documentElement.style.setProperty('--ava-c2', c2.value);
      document.documentElement.style.setProperty('--ava-angle', ang.value + 'deg');
      document.documentElement.style.setProperty('--ava-radius', rad.value + 'px');
      document.documentElement.style.setProperty('--ava-glow', glow.value);
      document.documentElement.style.setProperty('--ava-speed', speed.value + 's');
      const header = document.getElementById(CLS.avatar);
      if(header){ header.classList.add('ava-custom'); header.classList.remove('ava-galaxy','ava-ocean','ava-rainbow','ava-neon','ava-sunset','ava-wave','ava-pulse','ava-ippel','ava-forest','ava-lava','ava-mint','ava-sky','ava-rose','ava-candy','ava-silver','ava-carbon'); }
    }
      [c1,c2,ang,rad,glow,speed].forEach(el=> el.addEventListener('input', applyPreview));
      if(reset) reset.addEventListener('click', ()=>{
        c1.value = '#dc3545'; c2.value = '#b21f35'; ang.value = 135; rad.value = 12; glow.value = 0.18; speed.value = 6; applyPreview();
      });
      if(save) save.addEventListener('click', async ()=>{
        const prefs = { c1:c1.value, c2:c2.value, angle: Number(ang.value), radius: Number(rad.value), glow: Number(glow.value), speed: Number(speed.value) };
        await select('ava-custom', prefs);
      });
    }
  }

  function show(){ ensureModal(); document.getElementById(CLS.modal).style.display='flex'; }
  function hide(){ const m=document.getElementById(CLS.modal); if(m) m.style.display='none'; }

  async function select(key, prefs){
    try{
      const body = { avatar:key };
      if(prefs) body.prefs = prefs;
      const resp = await fetch(API, { method:'POST', headers:{'Content-Type':'application/json'}, credentials:'include', body: JSON.stringify(body) });
      const data = await resp.json();
      if(!data.success) throw new Error(data.message||'Falha ao salvar');
      applyToHeader(key, data.prefs);
      hide();
    }catch(e){ alert('Erro ao salvar avatar: '+e.message); }
  }

  function applyToHeader(key, prefs){
    const el = document.getElementById(CLS.avatar);
    if(!el) return;
  el.className = `user-avatar ava ${key||'ava-ippel'}`;
    // Reset content before applying
    el.innerHTML = '';
    if(key === 'ava-custom' && prefs){
      document.documentElement.style.setProperty('--ava-c1', prefs.c1||'#dc3545');
      document.documentElement.style.setProperty('--ava-c2', prefs.c2||'#b21f35');
      document.documentElement.style.setProperty('--ava-angle', (prefs.angle||135) + 'deg');
      document.documentElement.style.setProperty('--ava-radius', (prefs.radius||12) + 'px');
      document.documentElement.style.setProperty('--ava-glow', String(prefs.glow ?? 0.18));
      document.documentElement.style.setProperty('--ava-speed', (prefs.speed||6) + 's');
      // Letter overlay for custom
      const ch = (window.__USER_NAME__||'U').charAt(0).toUpperCase();
      el.textContent = ch;
    } else if(key === 'ava-image' && prefs && prefs.image){
      el.classList.add('ava-image');
      const img = document.createElement('img');
      img.src = prefs.image;
      img.alt = 'avatar';
      el.appendChild(img);
    } else if(key && (key.startsWith('ava-corp') || key==='ava-initials')){
      el.classList.add('ava-corp');
      const ch = (window.__USER_NAME__||'U U').split(/\s+/).map(p=>p[0]||'').slice(0,2).join('').toUpperCase();
      el.textContent = ch;
    } else {
      // Default: show initial
      const ch = (window.__USER_NAME__||'U').charAt(0).toUpperCase();
      el.textContent = ch;
    }
  }

  function attach(){
    const el = document.getElementById(CLS.avatar);
    if(!el) return;
    el.addEventListener('click', show);
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    attach();
    if(window.__OPEN_AVATAR_ON_READY__){
      try { show(); } catch(_) {}
      window.__OPEN_AVATAR_ON_READY__ = false;
    }
  });

  // Expose
  window.IPPELAvatar = { show, hide, applyToHeader };
})();
