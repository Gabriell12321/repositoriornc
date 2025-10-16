// ================================================================================
// SISTEMA DE PERFORMANCE E LAZY LOADING - IPPEL RNC
// Otimizações de frontend para melhorar UX e velocidade de carregamento
// ================================================================================

(function() {
    'use strict';

    // ==================== LAZY LOADING SYSTEM ====================
    
    class LazyLoader {
        constructor() {
            this.imageObserver = null;
            this.componentObserver = null;
            this.initializeObservers();
        }

        initializeObservers() {
            // Observer para imagens lazy
            if ('IntersectionObserver' in window) {
                this.imageObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.loadImage(entry.target);
                            this.imageObserver.unobserve(entry.target);
                        }
                    });
                }, { rootMargin: '50px' });

                // Observer para componentes lazy
                this.componentObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.loadComponent(entry.target);
                            this.componentObserver.unobserve(entry.target);
                        }
                    });
                }, { rootMargin: '100px' });
            }
        }

        loadImage(img) {
            const src = img.dataset.src;
            if (src) {
                img.src = src;
                img.classList.add('loaded');
                img.removeAttribute('data-src');
            }
        }

        loadComponent(element) {
            const componentType = element.dataset.lazyComponent;
            
            switch (componentType) {
                case 'rnc-list':
                    this.loadRNCList(element);
                    break;
                case 'dashboard-charts':
                    this.loadDashboardCharts(element);
                    break;
                case 'user-list':
                    this.loadUserList(element);
                    break;
            }
        }

        async loadRNCList(element) {
            try {
                element.innerHTML = '<div class="loading-spinner">Carregando RNCs...</div>';
                
                // Buscar dados de forma assíncrona
                const response = await fetch('/api/rnc/list?limit=20', {
                    credentials: 'include'
                });
                
                const data = await response.json();
                if (data.success) {
                    this.renderRNCList(element, data.rncs);
                } else {
                    element.innerHTML = '<div class="error">Erro ao carregar RNCs</div>';
                }
            } catch (error) {
                element.innerHTML = '<div class="error">Erro de conexão</div>';
                console.error('Erro ao carregar RNCs:', error);
            }
        }

        renderRNCList(container, rncs) {
            const html = rncs.map(rnc => `
                <div class="rnc-item" data-id="${rnc.id}">
                    <h4>${this.escapeHtml(rnc.title)}</h4>
                    <p>Status: ${this.escapeHtml(rnc.status)}</p>
                    <p>Cliente: ${this.escapeHtml(rnc.client)}</p>
                </div>
            `).join('');
            
            container.innerHTML = html;
        }

        observeImages() {
            if (this.imageObserver) {
                document.querySelectorAll('img[data-src]').forEach(img => {
                    this.imageObserver.observe(img);
                });
            }
        }

        observeComponents() {
            if (this.componentObserver) {
                document.querySelectorAll('[data-lazy-component]').forEach(el => {
                    this.componentObserver.observe(el);
                });
            }
        }

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }

    // ==================== PERFORMANCE MONITOR ====================
    
    class PerformanceMonitor {
        constructor() {
            this.metrics = {
                pageLoadTime: 0,
                apiCallTimes: [],
                renderTimes: [],
                memoryUsage: []
            };
            this.startTime = performance.now();
            this.initializeMonitoring();
        }

        initializeMonitoring() {
            // Monitorar tempo de carregamento da página
            window.addEventListener('load', () => {
                this.metrics.pageLoadTime = performance.now() - this.startTime;
                this.reportMetrics();
            });

            // Monitorar uso de memória (se disponível)
            if ('memory' in performance) {
                setInterval(() => {
                    this.metrics.memoryUsage.push({
                        timestamp: Date.now(),
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize
                    });
                    
                    // Manter apenas os últimos 60 pontos
                    if (this.metrics.memoryUsage.length > 60) {
                        this.metrics.memoryUsage.shift();
                    }
                }, 30000); // A cada 30 segundos
            }
        }

        measureApiCall(url, startTime, endTime, success) {
            this.metrics.apiCallTimes.push({
                url: url,
                duration: endTime - startTime,
                success: success,
                timestamp: Date.now()
            });

            // Manter apenas as últimas 100 chamadas
            if (this.metrics.apiCallTimes.length > 100) {
                this.metrics.apiCallTimes.shift();
            }
        }

        measureRenderTime(component, duration) {
            this.metrics.renderTimes.push({
                component: component,
                duration: duration,
                timestamp: Date.now()
            });
        }

        reportMetrics() {
            // Enviar métricas para o servidor (opcional)
            if (this.shouldReportMetrics()) {
                fetch('/api/metrics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        pageLoadTime: this.metrics.pageLoadTime,
                        averageApiTime: this.getAverageApiTime(),
                        slowQueries: this.getSlowQueries(),
                        memoryTrend: this.getMemoryTrend()
                    })
                }).catch(() => {}); // Ignorar erros silenciosamente
            }
        }

        shouldReportMetrics() {
            // Reportar apenas 5% das sessões para não sobrecarregar o servidor
            return Math.random() < 0.05;
        }

        getAverageApiTime() {
            if (this.metrics.apiCallTimes.length === 0) return 0;
            const sum = this.metrics.apiCallTimes.reduce((acc, call) => acc + call.duration, 0);
            return sum / this.metrics.apiCallTimes.length;
        }

        getSlowQueries() {
            return this.metrics.apiCallTimes.filter(call => call.duration > 2000);
        }

        getMemoryTrend() {
            if (this.metrics.memoryUsage.length < 2) return 'stable';
            
            const recent = this.metrics.memoryUsage.slice(-10);
            const trend = recent[recent.length - 1].used - recent[0].used;
            
            if (trend > 10 * 1024 * 1024) return 'increasing';
            if (trend < -5 * 1024 * 1024) return 'decreasing';
            return 'stable';
        }
    }

    // ==================== CACHE SYSTEM ====================
    
    class FrontendCache {
        constructor() {
            this.cache = new Map();
            this.maxSize = 100;
            this.maxAge = 5 * 60 * 1000; // 5 minutos
        }

        set(key, data, customTTL = null) {
            const ttl = customTTL || this.maxAge;
            const entry = {
                data: data,
                timestamp: Date.now(),
                ttl: ttl
            };

            this.cache.set(key, entry);

            // Limpar cache se muito grande
            if (this.cache.size > this.maxSize) {
                this.evictOldest();
            }
        }

        get(key) {
            const entry = this.cache.get(key);
            if (!entry) return null;

            // Verificar se expirou
            if (Date.now() - entry.timestamp > entry.ttl) {
                this.cache.delete(key);
                return null;
            }

            return entry.data;
        }

        evictOldest() {
            // Remover 20% das entradas mais antigas
            const entries = Array.from(this.cache.entries());
            entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
            
            const toRemove = Math.floor(entries.length * 0.2);
            for (let i = 0; i < toRemove; i++) {
                this.cache.delete(entries[i][0]);
            }
        }

        clear() {
            this.cache.clear();
        }

        getStats() {
            return {
                size: this.cache.size,
                maxSize: this.maxSize,
                oldestEntry: this.getOldestTimestamp(),
                memoryUsage: this.estimateMemoryUsage()
            };
        }

        getOldestTimestamp() {
            let oldest = Date.now();
            for (const entry of this.cache.values()) {
                if (entry.timestamp < oldest) {
                    oldest = entry.timestamp;
                }
            }
            return oldest;
        }

        estimateMemoryUsage() {
            let totalSize = 0;
            for (const entry of this.cache.values()) {
                totalSize += JSON.stringify(entry.data).length;
            }
            return totalSize;
        }
    }

    // ==================== OPTIMIZED FETCH ====================
    
    class OptimizedFetch {
        constructor(cache, performanceMonitor) {
            this.cache = cache;
            this.performanceMonitor = performanceMonitor;
            this.abortControllers = new Map();
            this.requestQueue = [];
            this.maxConcurrentRequests = 6;
            this.activeRequests = 0;
        }

        async fetch(url, options = {}, cacheKey = null, cacheTTL = null) {
            // Verificar cache primeiro
            if (cacheKey && !options.bypassCache) {
                const cached = this.cache.get(cacheKey);
                if (cached) {
                    return cached;
                }
            }

            // Cancelar requisições antigas para a mesma URL
            this.cancelPreviousRequest(url);

            // Adicionar à fila se muitas requisições ativas
            if (this.activeRequests >= this.maxConcurrentRequests) {
                return new Promise((resolve, reject) => {
                    this.requestQueue.push(() => this.executeRequest(url, options, cacheKey, cacheTTL).then(resolve).catch(reject));
                });
            }

            return this.executeRequest(url, options, cacheKey, cacheTTL);
        }

        async executeRequest(url, options, cacheKey, cacheTTL) {
            const startTime = performance.now();
            const abortController = new AbortController();
            
            // Armazenar controller para possível cancelamento
            this.abortControllers.set(url, abortController);
            
            // Configurar timeout
            const timeout = options.timeout || 15000;
            const timeoutId = setTimeout(() => {
                abortController.abort();
            }, timeout);

            this.activeRequests++;

            try {
                const response = await fetch(url, {
                    ...options,
                    signal: abortController.signal,
                    credentials: options.credentials || 'include'
                });

                clearTimeout(timeoutId);
                const endTime = performance.now();
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                
                // Cachear se solicitado
                if (cacheKey && data) {
                    this.cache.set(cacheKey, data, cacheTTL);
                }

                // Registrar métricas
                this.performanceMonitor.measureApiCall(url, startTime, endTime, true);

                return data;

            } catch (error) {
                clearTimeout(timeoutId);
                const endTime = performance.now();
                
                // Registrar erro nas métricas
                this.performanceMonitor.measureApiCall(url, startTime, endTime, false);
                
                throw error;
                
            } finally {
                this.activeRequests--;
                this.abortControllers.delete(url);
                
                // Processar próxima requisição na fila
                if (this.requestQueue.length > 0) {
                    const nextRequest = this.requestQueue.shift();
                    setTimeout(nextRequest, 0);
                }
            }
        }

        cancelPreviousRequest(url) {
            const controller = this.abortControllers.get(url);
            if (controller) {
                controller.abort();
                this.abortControllers.delete(url);
            }
        }

        cancelAllRequests() {
            for (const controller of this.abortControllers.values()) {
                controller.abort();
            }
            this.abortControllers.clear();
            this.requestQueue.length = 0;
        }
    }

    // ==================== INITIALIZATION ====================
    
    // Instâncias globais
    window.IPPELPerformance = {
        lazyLoader: new LazyLoader(),
        performanceMonitor: new PerformanceMonitor(),
        cache: new FrontendCache(),
        optimizedFetch: null
    };

    // Inicializar fetch otimizado
    window.IPPELPerformance.optimizedFetch = new OptimizedFetch(
        window.IPPELPerformance.cache,
        window.IPPELPerformance.performanceMonitor
    );

    // Função utilitária global para fetch otimizado
    window.fetchOptimized = function(url, options = {}, cacheMinutes = 0) {
        const cacheKey = cacheMinutes > 0 ? `fetch:${url}:${JSON.stringify(options)}` : null;
        const cacheTTL = cacheMinutes > 0 ? cacheMinutes * 60 * 1000 : null;
        
        return window.IPPELPerformance.optimizedFetch.fetch(url, options, cacheKey, cacheTTL);
    };

    // Inicialização quando DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function() {
        // Observar imagens e componentes lazy
        window.IPPELPerformance.lazyLoader.observeImages();
        window.IPPELPerformance.lazyLoader.observeComponents();

        // Adicionar indicadores de performance em desenvolvimento
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            setTimeout(() => {
                const stats = window.IPPELPerformance.cache.getStats();
                console.log('IPPEL Performance Stats:', {
                    cacheSize: stats.size,
                    pageLoadTime: window.IPPELPerformance.performanceMonitor.metrics.pageLoadTime,
                    averageApiTime: window.IPPELPerformance.performanceMonitor.getAverageApiTime()
                });
            }, 5000);
        }
    });

    // Limpeza ao sair da página
    window.addEventListener('beforeunload', function() {
        window.IPPELPerformance.optimizedFetch.cancelAllRequests();
    });

})();
