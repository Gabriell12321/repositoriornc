// Gráficos Avançados - Sistema RNC IPPEL
// Implementações de Heatmap, Gauge e Radar Charts

class AdvancedCharts {
    constructor() {
        this.charts = new Map();
        this.inFlight = new Set();
        this.colors = {
            primary: '#007bff',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#17a2b8',
            light: '#f8f9fa',
            dark: '#343a40'
        };
    }

    // Heatmap Chart Implementation
    createHeatmapChart(canvasId, data, options = {}) {
        if (this.inFlight.has(canvasId)) {
            // Já existe uma criação em andamento; evita corrida
            return this.charts.get(canvasId) || null;
        }
        this.inFlight.add(canvasId);
        // Destruir gráfico existente primeiro
        this.destroyChart(canvasId);

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');

        // Garantir limpeza total do canvas em ambientes onde um Chart ainda esteja associado
        try {
            // Chart.js v3/v4
            const existingV3 = (typeof Chart !== 'undefined' && Chart.getChart) ? Chart.getChart(canvas) : null;
            if (existingV3) {
                try { existingV3.destroy(); } catch (_) {}
            }
            // Chart.js v2 (Chart.instances)
            if (typeof Chart !== 'undefined' && Chart.instances) {
                const list = Array.isArray(Chart.instances) ? Chart.instances : Object.values(Chart.instances);
                list.forEach((inst) => {
                    try {
                        if (inst && inst.chart && inst.chart.canvas === canvas) {
                            inst.chart.destroy();
                        } else if (inst && inst.canvas === canvas) {
                            inst.destroy && inst.destroy();
                        }
                    } catch(_){}
                });
            }
            // Reset físico do canvas para limpar contexto/refs
            canvas.width = canvas.width;
        } catch(e) {
            // apenas seguir se algo falhar
        }

        // Segurança extra: se algum gráfico ainda estiver associado ao canvas, destruir antes de criar
        const existingBeforeCreateHeatmap = (typeof Chart !== 'undefined' && Chart.getChart) ? Chart.getChart(canvas) : null;
        if (existingBeforeCreateHeatmap) {
            try { existingBeforeCreateHeatmap.destroy(); } catch (e) { console.warn('Erro ao destruir chart existente (heatmap):', e); }
        }

        // Configuração padrão do heatmap
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Mapa de Calor - RNCs por Período',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            const point = context[0];
                            const raw = point.raw || {};
                            const x = raw.x ?? 0;
                            const y = raw.y ?? 0;
                            return `${data.yLabels[y] || ''} - ${data.xLabels[x] || ''}`;
                        },
                        label: function(context) {
                            const raw = context.raw || {};
                            return `RNCs: ${raw.v ?? 0}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    min: 0,
                    max: data.xLabels.length - 1,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return data.xLabels[value] || '';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Hora do Dia'
                    }
                },
                y: {
                    type: 'linear',
                    min: 0,
                    max: data.yLabels.length - 1,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return data.yLabels[value] || '';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Dia da Semana'
                    }
                }
            }
        };

        // Pré-cálculo para evitar NaN quando todos os valores forem 0
        const flatValues = data.values.flat();
        const maxForScale = Math.max(1, Math.max(...flatValues));

        // Processar dados para o formato do Chart.js
        const processedData = {
            datasets: [{
                label: 'RNCs',
                data: data.values.map((row, y) =>
                    row.map((value, x) => ({ x, y, v: value }))
                ).flat(),
                backgroundColor: function(context) {
                    const raw = context.raw || {};
                    const intensity = Math.max(0, Math.min(1, (raw.v ?? 0) / maxForScale));
                    return `rgba(220, 53, 69, ${intensity})`;
                },
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                pointRadius: function(context) {
                    const raw = context.raw || {};
                    const ratio = Math.max(0, Math.min(1, (raw.v ?? 0) / maxForScale));
                    return Math.max(3, ratio * 15);
                }
            }]
        };

        try {
            const chart = new Chart(ctx, {
                type: 'scatter',
                data: processedData,
                options: { ...defaultOptions, ...options }
            });

            this.charts.set(canvasId, chart);
            return chart;
        } catch (error) {
            // Tenta uma vez mais se for erro de canvas já em uso
            const msg = (error && error.message) || '';
            if (msg.includes('Canvas is already in use')) {
                const existing = (typeof Chart !== 'undefined' && Chart.getChart) ? Chart.getChart(canvas) : null;
                if (existing) {
                    try { existing.destroy(); } catch(_) {}
                }
                // Resetar canvas novamente antes do retry
                try { canvas.width = canvas.width; } catch(_){}
                try {
                    const retry = new Chart(ctx, {
                        type: 'scatter',
                        data: processedData,
                        options: { ...defaultOptions, ...options }
                    });
                    this.charts.set(canvasId, retry);
                    return retry;
                } catch (e2) {
                    console.error(`Erro ao recriar heatmap chart ${canvasId}:`, e2);
                }
            }
            console.error(`Erro ao criar heatmap chart ${canvasId}:`, error);
            return null;
        } finally {
            this.inFlight.delete(canvasId);
        }
    }

    // Gauge Chart Implementation
    createGaugeChart(canvasId, value, options = {}) {
        if (this.inFlight.has(canvasId)) {
            return this.charts.get(canvasId) || null;
        }
        this.inFlight.add(canvasId);
        // Destruir gráfico existente primeiro
        this.destroyChart(canvasId);

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');

        // Segurança extra: se algum gráfico ainda estiver associado ao canvas, destruir antes de criar
        const existingBeforeCreateGauge = (typeof Chart !== 'undefined' && Chart.getChart) ? Chart.getChart(canvas) : null;
        if (existingBeforeCreateGauge) {
            try { existingBeforeCreateGauge.destroy(); } catch (e) { console.warn('Erro ao destruir chart existente (gauge):', e); }
        }
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            circumference: Math.PI,
            rotation: Math.PI,
            cutout: '80%',
            plugins: {
                title: {
                    display: true,
                    text: options.title || 'Indicador de Performance',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            },
            animation: {
                animateRotate: true,
                duration: 2000
            }
        };

        const maxValue = options.max || 100;
        const minValue = options.min || 0;
        // Normaliza e garante que fique entre 0 e 100 para evitar valores negativos no dataset
        const rawNormalized = ((value - minValue) / (maxValue - minValue)) * 100;
        const normalizedValue = Math.max(0, Math.min(100, Number.isFinite(rawNormalized) ? rawNormalized : 0));
        
        // Determinar cor baseada no valor (permite override por options.colors.progress)
        let color;
        if (options.colors && options.colors.progress) {
            color = options.colors.progress;
        } else if (normalizedValue >= 80) color = this.colors.success;
        else if (normalizedValue >= 60) color = this.colors.warning;
        else color = this.colors.danger;

        const trackColor = (options.colors && (options.colors.track || options.colors.background)) || '#e9ecef';
        const data = {
            datasets: [{
                data: [normalizedValue, Math.max(0, 100 - normalizedValue)],
                backgroundColor: [color, trackColor],
                borderWidth: 0,
                borderRadius: 10
            }]
        };

        try {
            const chartConfig = {
                type: 'doughnut',
                data: data,
                options: { ...defaultOptions, ...options },
                plugins: [{
                    id: 'gaugeText',
                    afterDraw: function(chart) {
                        const { ctx, chartArea } = chart;
                        const centerX = (chartArea.left + chartArea.right) / 2;
                        const centerY = (chartArea.top + chartArea.bottom) / 2 + 20;

                        ctx.save();
                        ctx.font = `bold ${options.valueSize || 24}px Arial`;
                        ctx.fillStyle = color;
                        ctx.textAlign = 'center';
                        ctx.fillText(`${Math.round(value)}${options.unit || '%'}`, centerX, centerY);

                        ctx.font = `${options.fontSize || 14}px Arial`;
                        ctx.fillStyle = '#666';
                        ctx.fillText(options.label || 'Valor Atual', centerX, centerY + 25);
                        ctx.restore();
                    }
                }]
            };

            let chart = new Chart(ctx, chartConfig);
            this.charts.set(canvasId, chart);
            return chart;
        } catch (error) {
            const msg = (error && error.message) || '';
            if (msg.includes('Canvas is already in use')) {
                const existing = (typeof Chart !== 'undefined' && Chart.getChart) ? Chart.getChart(canvas) : null;
                if (existing) {
                    try { existing.destroy(); } catch(_) {}
                }
                try {
                    const retry = new Chart(ctx, {
                        type: 'doughnut',
                        data: data,
                        options: { ...defaultOptions, ...options }
                    });
                    this.charts.set(canvasId, retry);
                    return retry;
                } catch (e2) {
                    console.error(`Erro ao recriar gauge chart ${canvasId}:`, e2);
                }
            }
            console.error(`Erro ao criar gauge chart ${canvasId}:`, error);
            return null;
        } finally {
            this.inFlight.delete(canvasId);
        }
    }

    // Radar Chart Avançado
    createAdvancedRadarChart(canvasId, data, options = {}) {
        if (this.inFlight.has(canvasId)) {
            return this.charts.get(canvasId) || null;
        }
        this.inFlight.add(canvasId);
        // Destruir gráfico existente primeiro
        this.destroyChart(canvasId);

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');

        // Segurança extra: se algum gráfico ainda estiver associado ao canvas, destruir antes de criar
        const existingBeforeCreateRadar = (typeof Chart !== 'undefined' && Chart.getChart) ? Chart.getChart(canvas) : null;
        if (existingBeforeCreateRadar) {
            try { existingBeforeCreateRadar.destroy(); } catch (e) { console.warn('Erro ao destruir chart existente (radar):', e); }
        }
        
        // Fallback: se houver menos de 3 rótulos, o radar fica pouco legível.
        // Nesse caso, renderizamos um gráfico de barras comparando Quantidade x Eficiência.
        if (!data || !data.labels || data.labels.length < 3) {
            const labels = (data && data.labels && data.labels.length ? data.labels : ['N/D']);
            const processedDataBar = {
                labels,
                datasets: (data && data.datasets ? data.datasets : []).map((dataset, index) => ({
                    label: dataset.label,
                    data: dataset.data,
                    backgroundColor: `${this.getColorByIndex(index)}66`,
                    borderColor: this.getColorByIndex(index),
                    borderWidth: 1
                }))
            };
            const chart = new Chart(ctx, {
                type: 'bar',
                data: processedDataBar,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: options.title || 'Comparativo por Departamento',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: { position: 'bottom' }
                    },
                    scales: {
                        y: { beginAtZero: true, max: options.maxValue || 100 }
                    }
                }
            });
            this.charts.set(canvasId, chart);
            return chart;
        }

        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Análise Multidimensional - RNCs',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.r}`;
                        }
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: options.maxValue || 100,
                    ticks: {
                        stepSize: 20,
                        showLabelBackdrop: false
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    },
                    angleLines: {
                        color: 'rgba(0,0,0,0.1)'
                    },
                    pointLabels: {
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart'
            }
        };

        // Processar dados para múltiplos datasets
        const processedData = {
            labels: data.labels,
            datasets: data.datasets.map((dataset, index) => ({
                label: dataset.label,
                data: dataset.data,
                backgroundColor: `${this.getColorByIndex(index)}20`,
                borderColor: this.getColorByIndex(index),
                borderWidth: 2,
                pointBackgroundColor: this.getColorByIndex(index),
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8,
                fill: true
            }))
        };

        try {
            const chart = new Chart(ctx, {
                type: 'radar',
                data: processedData,
                options: { ...defaultOptions, ...options }
            });

            this.charts.set(canvasId, chart);
            return chart;
        } catch (error) {
            const msg = (error && error.message) || '';
            if (msg.includes('Canvas is already in use')) {
                const existing = (typeof Chart !== 'undefined' && Chart.getChart) ? Chart.getChart(canvas) : null;
                if (existing) {
                    try { existing.destroy(); } catch(_) {}
                }
                try {
                    const retry = new Chart(ctx, {
                        type: 'radar',
                        data: processedData,
                        options: { ...defaultOptions, ...options }
                    });
                    this.charts.set(canvasId, retry);
                    return retry;
                } catch (e2) {
                    console.error(`Erro ao recriar radar chart ${canvasId}:`, e2);
                }
            }
            console.error(`Erro ao criar radar chart ${canvasId}:`, error);
            return null;
        } finally {
            this.inFlight.delete(canvasId);
        }
    }

    // Gráfico de Sankey (Fluxo)
    createSankeyChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        // Implementação simplificada usando Chart.js
        const ctx = canvas.getContext('2d');
        
        const processedData = {
            labels: data.labels,
            datasets: [{
                label: 'Fluxo de RNCs',
                data: data.values,
                backgroundColor: data.values.map((_, index) => 
                    this.getColorByIndex(index)
                ),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        };

        const chart = new Chart(ctx, {
            type: 'bar',
            data: processedData,
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Fluxo de Processos - RNCs',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Quantidade'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Etapas do Processo'
                        }
                    }
                },
                ...options
            }
        });

        this.charts.set(canvasId, chart);
        return chart;
    }

    // Gráfico de Treemap (Hierárquico)
    createTreemapChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        // Implementação usando scatter plot para simular treemap
        const ctx = canvas.getContext('2d');
        
        const processedData = {
            datasets: [{
                label: 'Distribuição Hierárquica',
                data: data.map((item, index) => ({
                    x: index % 4,
                    y: Math.floor(index / 4),
                    r: Math.sqrt(item.value) * 2
                })),
                backgroundColor: data.map((_, index) => 
                    this.getColorByIndex(index)
                ),
                borderColor: '#fff',
                borderWidth: 2
            }]
        };

        const chart = new Chart(ctx, {
            type: 'bubble',
            data: processedData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribuição por Categorias',
                        font: { size: 16, weight: 'bold' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const dataIndex = context.dataIndex;
                                return `${data[dataIndex].label}: ${data[dataIndex].value}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        display: false
                    }
                },
                ...options
            }
        });

        this.charts.set(canvasId, chart);
        return chart;
    }

    // Utilitários
    getColorByIndex(index) {
        const colorArray = [
            this.colors.primary,
            this.colors.success,
            this.colors.warning,
            this.colors.danger,
            this.colors.info,
            '#6f42c1', // purple
            '#fd7e14', // orange
            '#20c997'  // teal
        ];
        return colorArray[index % colorArray.length];
    }

    // Atualizar gráfico existente
    updateChart(canvasId, newData) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.data = newData;
            chart.update('active');
        }
    }

    // Destruir gráfico
    destroyChart(canvasId) {
        // Primeiro, verificar se existe um gráfico no nosso mapa
        const chart = this.charts.get(canvasId);
        if (chart) {
            try {
                chart.destroy();
            } catch (e) {
                console.warn(`Erro ao destruir gráfico ${canvasId}:`, e);
            }
            this.charts.delete(canvasId);
        }
        
        // Também verificar se existe um gráfico registrado globalmente no Chart.js
        const canvas = document.getElementById(canvasId);
        if (canvas) {
            const existingChart = Chart.getChart(canvas);
            if (existingChart) {
                try {
                    existingChart.destroy();
                } catch (e) {
                    console.warn(`Erro ao destruir gráfico global ${canvasId}:`, e);
                }
            }
        }
    }

    // Exportar gráfico como imagem
    exportChart(canvasId, filename = 'chart') {
        const chart = this.charts.get(canvasId);
        if (chart) {
            const url = chart.toBase64Image();
            const link = document.createElement('a');
            link.download = `${filename}.png`;
            link.href = url;
            link.click();
        }
    }

    // Redimensionar todos os gráficos
    resizeAllCharts() {
        this.charts.forEach(chart => {
            chart.resize();
        });
    }

    // Animação de entrada para gráficos
    animateChartEntry(canvasId, delay = 0) {
        setTimeout(() => {
            const chart = this.charts.get(canvasId);
            if (chart) {
                chart.update('active');
            }
        }, delay);
    }

    // Criar gráfico de comparação temporal
    createTimeComparisonChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: data.datasets.map((dataset, index) => ({
                    label: dataset.label,
                    data: dataset.data,
                    borderColor: this.getColorByIndex(index),
                    backgroundColor: `${this.getColorByIndex(index)}20`,
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: this.getColorByIndex(index),
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Comparação Temporal',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Período'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Quantidade'
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                },
                ...options
            }
        });

        this.charts.set(canvasId, chart);
        return chart;
    }
}

// Instância global
const advancedCharts = new AdvancedCharts();
// Expor também no escopo global para integrações que referenciam window.advancedCharts
if (typeof window !== 'undefined') {
    window.advancedCharts = advancedCharts;
}

// Funções de conveniência para uso global
window.createHeatmap = (canvasId, data, options) => 
    advancedCharts.createHeatmapChart(canvasId, data, options);

window.createGauge = (canvasId, value, options) => 
    advancedCharts.createGaugeChart(canvasId, value, options);

window.createAdvancedRadar = (canvasId, data, options) => 
    advancedCharts.createAdvancedRadarChart(canvasId, data, options);

window.createSankey = (canvasId, data, options) => 
    advancedCharts.createSankeyChart(canvasId, data, options);

window.createTreemap = (canvasId, data, options) => 
    advancedCharts.createTreemapChart(canvasId, data, options);

window.createTimeComparison = (canvasId, data, options) => 
    advancedCharts.createTimeComparisonChart(canvasId, data, options);

// Event listeners para redimensionamento
window.addEventListener('resize', () => {
    advancedCharts.resizeAllCharts();
});

// Exportar para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdvancedCharts;
}