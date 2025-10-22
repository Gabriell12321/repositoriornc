// IPPEL RNC System - Main JavaScript
// Tratamento global de erros para evitar interferência de extensões

(function() {
    'use strict';

    // Configuração global
    const CONFIG = {
        API_BASE: '/api',
        RETRY_ATTEMPTS: 2,
        RETRY_DELAY: 500
    };

    // Silenciar ruídos conhecidos de extensões (ex.: erros de SVG em jQuery/translateContent)
    try {
        const _origError = console.error.bind(console);
        const _origWarn = console.warn.bind(console);
        function _shouldSilence(args) {
            const msg = args && args.length ? String(args[0] || '') : '';
            return /attribute d:\s*expected number/i.test(msg)
                || /translatecontent\.js/i.test(msg)
                || (/jquery-3\.4\.1\.min\.js/i.test(msg) && /attribute d/i.test(msg));
        }
        console.error = function(...args) {
            if (_shouldSilence(args)) return; 
            return _origError(...args);
        };
        console.warn = function(...args) {
            if (_shouldSilence(args)) return; 
            return _origWarn(...args);
        };
        window.addEventListener('unhandledrejection', function(ev){
            try {
                const reason = ev && (ev.reason || ev.detail);
                const msg = reason ? String(reason) : '';
                if (/attribute d:\s*expected number/i.test(msg)) {
                    ev.preventDefault();
                }
            } catch {}
        });
    } catch {}

    // Tratamento global de erros
    window.addEventListener('error', function(event) {
        // Ignorar erros de extensões do navegador
        if (event.filename && (
            event.filename.includes('content.js') || 
            event.filename.includes('extension') ||
            event.filename.includes('chrome-extension')
        )) {
            event.preventDefault();
            console.warn('Erro de extensão do navegador ignorado:', event.message);
            return false;
        }

        // Ignorar erros de SVG inválido disparados por scripts de terceiros (ex.: jQuery injetado por extensões)
        try {
            const isJQueryFile = event.filename && event.filename.toLowerCase().includes('jquery');
            const isForeignOrigin = event.filename && typeof location !== 'undefined' && !event.filename.includes(location.host);
            const isSvgPathError = event.message && event.message.toLowerCase().includes('attribute d: expected number');
            if (isSvgPathError || (isJQueryFile && isForeignOrigin)) {
                event.preventDefault();
                console.warn('Erro de terceiros ignorado:', event.message, 'em', event.filename);
                return false;
            }
        } catch (e) {
            // se der erro aqui, apenas segue o fluxo padrão
        }
        
        // Para outros erros, log mas não interromper
        console.warn('Erro capturado:', event.message);
        return false;
    });

    // Função utilitária para fazer requisições com retry
    async function fetchWithRetry(url, options = {}, retries = CONFIG.RETRY_ATTEMPTS) {
        for (let i = 0; i < retries; i++) {
            try {
                const response = await fetch(url, { credentials: 'same-origin', ...options });
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response;
            } catch (error) {
                if (i === retries - 1) {
                    throw error;
                }
                // backoff leve
                await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY * (i + 1)));
            }
        }
    }

    // Função para carregar dados do formulário
    function loadFormData() {
        try {
            const savedData = localStorage.getItem('rncFormData');
            if (savedData) {
                const formData = JSON.parse(savedData);
                Object.keys(formData).forEach(key => {
                    const field = document.getElementById(key) || document.querySelector(`[name="${key}"]`);
                    if (field) {
                        if (field.type === 'checkbox') {
                            field.checked = formData[key];
                        } else {
                            field.value = formData[key];
                        }
                    }
                });
            }
        } catch (error) {
            console.warn('Erro ao carregar dados do formulário:', error);
        }
    }

    // Função para salvar dados do formulário
    function saveFormData() {
        try {
            const form = document.querySelector('form');
            if (!form) return;

            const formData = {};
            const fields = form.querySelectorAll('input, textarea, select');
            
            fields.forEach(field => {
                if (field.type === 'checkbox') {
                    formData[field.id] = field.checked;
                } else {
                    formData[field.name || field.id] = field.value;
                }
            });
            
            localStorage.setItem('rncFormData', JSON.stringify(formData));
        } catch (error) {
            console.warn('Erro ao salvar dados do formulário:', error);
        }
    }

    // Função para carregar informações do usuário
    async function loadUserInfo() {
        try {
            // Usar fetch direto para poder tratar 401 sem lançar exceção
            const response = await fetch(`${CONFIG.API_BASE}/user/info`, { credentials: 'include' });
            if (response.status === 401) {
                // Sem sessão: em páginas protegidas, redireciona; na página de login, apenas ignore
                const path = (location && location.pathname) ? location.pathname : '';
                if (path && path !== '/' && !/login/i.test(path)) {
                    window.location.href = '/';
                }
                return;
            }
            const data = await response.json();
            
            if (data.success) {
                // Mostrar área do usuário
                const userArea = document.getElementById('userArea');
                if (userArea) userArea.style.display = 'block';
                
                // Preencher informações
                const userName = document.getElementById('userName');
                const userDepartment = document.getElementById('userDepartment');
                
                if (userName) userName.textContent = data.user.name;
                if (userDepartment) userDepartment.textContent = data.user.department;

                // Guardar em cache básico para render rápido do dashboard
                try {
                    const dcRaw = localStorage.getItem('dashboardCacheV1');
                    const dc = dcRaw ? JSON.parse(dcRaw) : {};
                    localStorage.setItem('dashboardCacheV1', JSON.stringify({ ...dc, user: data.user, ts: Date.now() }));
                } catch (e) {}
                
                // Preencher automaticamente os campos de assinatura
                const assinaturaGerente = document.getElementById('assinatura_gerente');
                const nomeResponsavel = document.getElementById('nome_responsavel');
                
                if (assinaturaGerente && !assinaturaGerente.value) {
                    assinaturaGerente.value = data.user.name;
                }
                
                if (nomeResponsavel && !nomeResponsavel.value) {
                    nomeResponsavel.value = data.user.name;
                }
                
                // Preencher data de emissão automaticamente
                const dataEmissao = document.getElementById('data_emissao');
                if (dataEmissao && !dataEmissao.value) {
                    const hoje = new Date();
                    const dia = hoje.getDate().toString().padStart(2, '0');
                    const mes = (hoje.getMonth() + 1).toString().padStart(2, '0');
                    const ano = hoje.getFullYear();
                    dataEmissao.value = `${dia}/${mes}/${ano}`;
                }
                
                // Preencher área responsável automaticamente
                const areaResponsavel = document.getElementById('area_responsavel');
                if (areaResponsavel && !areaResponsavel.value) {
                    areaResponsavel.value = data.user.department;
                }
                
                // Carregar RNCs do usuário
                loadUserRNCs();
            } else {
                // Se não estiver logado, só redireciona fora da tela de login
                const path = (location && location.pathname) ? location.pathname : '';
                if (path && path !== '/' && !/login/i.test(path)) {
                    window.location.href = '/';
                }
            }
        } catch (error) {
            console.warn('Erro ao carregar informações do usuário:', error);
            // Não redirecionar automaticamente; permite a tela de login funcionar
        }
    }

    // Função para carregar RNCs do usuário
    async function loadUserRNCs() {
        try {
            const response = await fetchWithRetry(`${CONFIG.API_BASE}/rnc/list`);
            const data = await response.json();
            
            if (data.success) {
                const rncCount = data.rncs.length;
                const userRNCs = document.getElementById('userRNCs');
                if (userRNCs) userRNCs.textContent = `${rncCount} RNC(s) criado(s)`;
            }
        } catch (error) {
            console.warn('Erro ao carregar RNCs do usuário:', error);
            // Não interromper o fluxo por erro de carregamento de RNCs
        }
    }

    // Inicialização quando o DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function() {
        try {
            loadFormData();
            // Só tenta carregar info do usuário se existir algum elemento que precise
            if (document.getElementById('userArea') || document.getElementById('userName') || /dashboard/i.test(document.title)) {
                loadUserInfo();
            }
            
            // Auto-save form data on input
            document.addEventListener('input', saveFormData);
            document.addEventListener('change', saveFormData);
            
        } catch (error) {
            console.warn('Erro ao inicializar aplicação:', error);
        }
    });

    // Diagnóstico leve para Chart.js — tenta criar um gráfico de teste na página /dashboard
    document.addEventListener('DOMContentLoaded', function() {
        try {
            if (typeof location !== 'undefined' && location.pathname && location.pathname.indexOf('/dashboard') !== -1) {
                console.log('[DIAG] Iniciando diagnóstico de Chart.js...');
                console.log('[DIAG] Chart typeof ->', typeof Chart, 'version ->', (typeof Chart !== 'undefined' && Chart.version) ? Chart.version : 'n/a');
                try {
                    const canvas = document.createElement('canvas');
                    canvas.id = '__ippel_diag_chart__';
                    canvas.style.display = 'none';
                    document.body.appendChild(canvas);
                    const ctx = canvas.getContext('2d');
                    let created = false;
                    try {
                        const tmp = new Chart(ctx, { type: 'bar', data: { labels: ['d'], datasets: [{ data: [1] }] }, options: { responsive: false } });
                        created = true;
                        try { tmp.destroy(); } catch(_){}
                    } catch (err) {
                        console.error('[DIAG] Falha ao criar chart de teste:', err);
                    } finally {
                        try { document.body.removeChild(canvas); } catch(_){}
                    }
                    console.log('[DIAG] canvases count:', document.querySelectorAll('canvas').length, 'created_ok:', created);
                } catch (e) {
                    console.warn('[DIAG] Erro no diagnóstico Chart.js:', e);
                }
            }
        } catch (e) {}
    });

    // Hook avançado: intercepta todas as criações de Chart para log detalhado (diagnóstico)
    document.addEventListener('DOMContentLoaded', function() {
        try {
            if (typeof Chart !== 'undefined') {
                try {
                    const ChartProxy = new Proxy(Chart, {
                        construct(target, args, newTarget) {
                            try {
                                const ctx = args[0];
                                const config = args[1] || {};
                                let canvas = null;
                                try {
                                    if (ctx && ctx.canvas) canvas = ctx.canvas;
                                    else if (typeof ctx === 'string') canvas = document.getElementById(ctx);
                                } catch(_){}
                                const canvasId = canvas && canvas.id ? canvas.id : '(no-id)';
                                console.log('[CHARTHOOK] creating Chart: canvas=', canvasId, 'type=', config.type || '(unspecified)');
                                const result = Reflect.construct(target, args, newTarget);
                                return result;
                            } catch (err) {
                                console.error('[CHARTHOOK] error during Chart construction:', err, args && args[1]);
                                throw err;
                            }
                        }
                    });
                    // copy static properties if needed (Proxy forwards most statics)
                    window.Chart = ChartProxy;
                    console.log('[CHARTHOOK] Chart proxy installed');
                } catch (e) {
                    console.warn('[CHARTHOOK] falha ao instalar proxy:', e);
                }
            } else {
                console.warn('[CHARTHOOK] Chart não está definido no momento do hook');
            }
        } catch (e) {
            console.warn('[CHARTHOOK] erro inesperado ao instalar hook:', e);
        }
    });

    // Expor funções para uso global
    window.IPPELApp = {
        loadFormData,
        saveFormData,
        loadUserInfo,
        loadUserRNCs,
        fetchWithRetry
    };

})(); 