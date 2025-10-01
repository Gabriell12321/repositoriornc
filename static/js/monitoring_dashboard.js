// Monitoring Dashboard logic extracted to external JS to satisfy strict CSP (no inline scripts)

(() => {
  let failChart;

  function fmtDate(ts) {
    try { return new Date(ts).toLocaleString(); } catch (e) { return ts; }
  }

  async function loadSummary() {
    const hoursInput = document.getElementById('hoursInput');
    const hours = Math.max(1, Math.min(168, parseInt((hoursInput && hoursInput.value) || '24')));
    const hoursSpan = document.getElementById('hoursSpan');
    if (hoursSpan) hoursSpan.textContent = hours;

    const res = await fetch(`/api/monitoring/summary?hours=${hours}`);
    const j = await res.json();
    if (!j.success) return;

    const c = j.counters || {};
    const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
    set('m_auth_ok', c.auth_success || 0);
    set('m_auth_fail', c.auth_fail || 0);
    set('m_lockouts', c.auth_lockout || 0);
    set('m_401', c.api_unauthorized || 0);
    set('m_active_lockouts', j.active_lockouts || 0);

    // Chart
    const labels = (j.timeline || []).map(x => x.bucket);
    const data = (j.timeline || []).map(x => x.count);
    const ctx = document.getElementById('failChart');
    if (ctx) {
      if (failChart) failChart.destroy();
      // global Chart from chart.js
      // eslint-disable-next-line no-undef
      failChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Falhas/Lockouts por hora',
            data,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239,68,68,.15)',
            fill: true,
            tension: .25
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } }
        }
      });
    }
  }

  async function loadLockouts() {
    const res = await fetch('/api/monitoring/lockouts');
    const j = await res.json();
    const tbody = document.getElementById('lockoutsTBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!j.success || !j.lockouts || !j.lockouts.length) {
      tbody.innerHTML = '<tr><td class="muted" colspan="4">Nenhum lockout ativo</td></tr>';
      return;
    }
    for (const r of j.lockouts) {
      const when = r.locked_until ? new Date(r.locked_until * 1000).toLocaleString() : '-';
      tbody.insertAdjacentHTML('beforeend', `<tr><td>${r.name || '-'}</td><td>${r.email || '-'}</td><td>${r.failed_count || 0}</td><td>${when}</td></tr>`);
    }
  }

  async function loadEvents() {
    const res = await fetch('/api/monitoring/security-events?limit=300');
    const j = await res.json();
    const tbody = document.getElementById('eventsTBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!j.success || !j.events || !j.events.length) {
      tbody.innerHTML = '<tr><td class="muted" colspan="7">Sem eventos</td></tr>';
      return;
    }
    for (const ev of j.events.reverse()) {
      tbody.insertAdjacentHTML('beforeend', `<tr><td>${fmtDate(ev.ts)}</td><td>${ev.cat || ''}</td><td>${ev.act || ''}</td><td>${ev.status || ''}</td><td>${(ev.ip || '')}</td><td>${ev.user_id || ''}</td><td>${ev.email || ''}</td></tr>`);
    }
  }

  function initEvents() {
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) refreshBtn.addEventListener('click', () => { loadSummary(); });
  }

  window.addEventListener('DOMContentLoaded', () => {
    initEvents();
    loadSummary();
    loadLockouts();
    loadEvents();
    setInterval(loadSummary, 30000);
    setInterval(loadLockouts, 60000);
    setInterval(loadEvents, 60000);
  });

  // Expose for potential manual triggering from console
  window.IPPEL_MONITORING = { loadSummary, loadLockouts, loadEvents };
})();
// Monitoring Dashboard JS (externalized to comply with stricter CSP)
(function(){
  let failChart;
  function fmtDate(ts){
    try{ return new Date(ts).toLocaleString(); }catch(e){ return ts; }
  }
  async function loadSummary(){
    const hours = Math.max(1, Math.min(168, parseInt(document.getElementById('hoursInput').value||'24')));
    const hoursSpan = document.getElementById('hoursSpan');
    if(hoursSpan) hoursSpan.textContent = hours;
    const res = await fetch(`/api/monitoring/summary?hours=${hours}`);
    const j = await res.json();
    if(!j.success) return;
    const c = j.counters || {};
    const setText = (id, v)=>{ const el=document.getElementById(id); if(el) el.textContent = v; };
    setText('m_auth_ok', c.auth_success||0);
    setText('m_auth_fail', c.auth_fail||0);
    setText('m_lockouts', c.auth_lockout||0);
    setText('m_401', c.api_unauthorized||0);
    setText('m_active_lockouts', j.active_lockouts||0);
    const labels = (j.timeline||[]).map(x=>x.bucket);
    const data = (j.timeline||[]).map(x=>x.count);
    const ctx = document.getElementById('failChart');
    if(!ctx) return;
    if(failChart) failChart.destroy();
    // eslint-disable-next-line no-undef
    failChart = new Chart(ctx, { type:'line', data:{ labels, datasets:[{ label:'Falhas/Lockouts por hora', data, borderColor:'#ef4444', backgroundColor:'rgba(239,68,68,.15)', fill:true, tension:.25 }]}, options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{ display:false } } } });
  }
  async function loadLockouts(){
    const res = await fetch('/api/monitoring/lockouts');
    const j = await res.json();
    const tbody = document.getElementById('lockoutsTBody');
    if(!tbody){ return; }
    tbody.innerHTML = '';
    if(!j.success || !j.lockouts || !j.lockouts.length){
      tbody.innerHTML = '<tr><td class="muted" colspan="4">Nenhum lockout ativo</td></tr>';
      return;
    }
    for(const r of j.lockouts){
      const when = r.locked_until ? new Date(r.locked_until*1000).toLocaleString() : '-';
      tbody.insertAdjacentHTML('beforeend', `<tr><td>${r.name||'-'}</td><td>${r.email||'-'}</td><td>${r.failed_count||0}</td><td>${when}</td></tr>`);
    }
  }
  async function loadEvents(){
    const res = await fetch('/api/monitoring/security-events?limit=300');
    const j = await res.json();
    const tbody = document.getElementById('eventsTBody');
    if(!tbody){ return; }
    tbody.innerHTML = '';
    if(!j.success || !j.events || !j.events.length){
      tbody.innerHTML = '<tr><td class="muted" colspan="7">Sem eventos</td></tr>';
      return;
    }
    for(const ev of j.events.reverse()){
      tbody.insertAdjacentHTML('beforeend', `<tr><td>${fmtDate(ev.ts)}</td><td>${ev.cat||''}</td><td>${ev.act||''}</td><td>${ev.status||''}</td><td>${(ev.ip||'')}</td><td>${ev.user_id||''}</td><td>${ev.email||''}</td></tr>`);
    }
  }
  function init(){
    const hoursInput = document.getElementById('hoursInput');
    if(hoursInput){
      const btns = document.querySelectorAll('button[onclick="loadSummary()"]');
      btns.forEach(b=>b.addEventListener('click', loadSummary));
    }
    loadSummary();
    loadLockouts();
    loadEvents();
    setInterval(loadSummary, 30000);
    setInterval(loadLockouts, 60000);
    setInterval(loadEvents, 60000);
  }
  if(document.readyState === 'loading'){
    window.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
