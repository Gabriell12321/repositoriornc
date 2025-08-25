#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para debug dos gráficos da aba "Gráficos"
"""

def create_test_html():
    """Cria um arquivo HTML simples para testar os gráficos"""
    
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Teste dos Gráficos RNC</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .chart-container {
            width: 400px;
            height: 300px;
            margin: 20px;
            border: 1px solid #ccc;
            padding: 10px;
        }
        .debug-info {
            background: #f0f0f0;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h1>🔧 Teste de Debug dos Gráficos RNC</h1>
    
    <div class="debug-info">
        <h3>📊 Status do Chart.js:</h3>
        <div id="chartjs-status">Verificando...</div>
    </div>
    
    <div class="debug-info">
        <h3>🎯 Elementos de Canvas:</h3>
        <div id="canvas-status">Verificando...</div>
    </div>
    
    <div class="chart-container">
        <h3>📈 Gráfico de Teste - Tendência</h3>
        <canvas id="testTrendChart"></canvas>
    </div>
    
    <div class="chart-container">
        <h3>📊 Gráfico de Teste - Status</h3>
        <canvas id="testStatusChart"></canvas>
    </div>
    
    <div class="debug-info">
        <h3>🎯 Log de Criação:</h3>
        <div id="creation-log">Aguardando...</div>
    </div>

    <script>
        function log(message) {
            const logDiv = document.getElementById('creation-log');
            logDiv.innerHTML += message + '<br>';
            console.log(message);
        }
        
        function checkChartJS() {
            const statusDiv = document.getElementById('chartjs-status');
            if (typeof Chart !== 'undefined') {
                statusDiv.innerHTML = `✅ Chart.js carregado! Versão: ${Chart.version}`;
                statusDiv.style.color = 'green';
                return true;
            } else {
                statusDiv.innerHTML = '❌ Chart.js NÃO carregado!';
                statusDiv.style.color = 'red';
                return false;
            }
        }
        
        function checkCanvasElements() {
            const statusDiv = document.getElementById('canvas-status');
            const elements = ['testTrendChart', 'testStatusChart'];
            let found = 0;
            let html = '';
            
            elements.forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    html += `✅ ${id}: Encontrado<br>`;
                    found++;
                } else {
                    html += `❌ ${id}: NÃO encontrado<br>`;
                }
            });
            
            statusDiv.innerHTML = html + `<strong>Total: ${found}/${elements.length}</strong>`;
        }
        
        function createTestCharts() {
            log('🚀 Iniciando teste de criação de gráficos...');
            
            if (!checkChartJS()) {
                log('❌ Chart.js não disponível, não é possível criar gráficos');
                return;
            }
            
            // Dados de teste similares aos do sistema
            const testData = {
                trend: [
                    {date: '2025-08-01', count: 12},
                    {date: '2025-08-02', count: 8},
                    {date: '2025-08-03', count: 15},
                    {date: '2025-08-04', count: 10},
                    {date: '2025-08-05', count: 18}
                ],
                status: [
                    {label: 'Aberta', count: 45, color: '#ff6b6b'},
                    {label: 'Em Análise', count: 23, color: '#4ecdc4'},
                    {label: 'Finalizada', count: 67, color: '#96ceb4'}
                ]
            };
            
            // Teste 1: Gráfico de Tendência
            try {
                log('📈 Criando gráfico de tendência...');
                const ctx1 = document.getElementById('testTrendChart');
                if (!ctx1) {
                    log('❌ Canvas testTrendChart não encontrado');
                    return;
                }
                
                const trendChart = new Chart(ctx1, {
                    type: 'line',
                    data: {
                        labels: testData.trend.map(it => new Date(it.date).toLocaleDateString('pt-BR')),
                        datasets: [{
                            label: 'RNCs por Dia',
                            data: testData.trend.map(it => it.count),
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            borderWidth: 2,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
                log('✅ Gráfico de tendência criado com sucesso!');
                
            } catch (error) {
                log(`❌ Erro ao criar gráfico de tendência: ${error.message}`);
            }
            
            // Teste 2: Gráfico de Status
            try {
                log('📊 Criando gráfico de status...');
                const ctx2 = document.getElementById('testStatusChart');
                if (!ctx2) {
                    log('❌ Canvas testStatusChart não encontrado');
                    return;
                }
                
                const statusChart = new Chart(ctx2, {
                    type: 'doughnut',
                    data: {
                        labels: testData.status.map(s => s.label),
                        datasets: [{
                            data: testData.status.map(s => s.count),
                            backgroundColor: testData.status.map(s => s.color),
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });
                log('✅ Gráfico de status criado com sucesso!');
                
            } catch (error) {
                log(`❌ Erro ao criar gráfico de status: ${error.message}`);
            }
            
            log('🎯 Teste de gráficos concluído!');
        }
        
        // Executar testes quando a página carregar
        window.addEventListener('load', function() {
            setTimeout(() => {
                checkChartJS();
                checkCanvasElements();
                createTestCharts();
            }, 500);
        });
    </script>
</body>
</html>
    """
    
    return test_html

def main():
    print("🔧 CRIANDO ARQUIVO DE TESTE DOS GRÁFICOS")
    print("=" * 50)
    
    # Criar arquivo de teste
    test_content = create_test_html()
    
    with open('test_charts_debug.html', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ Arquivo de teste criado: test_charts_debug.html")
    print("")
    print("🚀 COMO USAR:")
    print("1. Abra o arquivo test_charts_debug.html no navegador")
    print("2. Verifique se o Chart.js está carregando")
    print("3. Verifique se os elementos canvas são encontrados")
    print("4. Observe se os gráficos de teste são criados")
    print("")
    print("Se os gráficos de teste funcionarem, o problema está")
    print("específico na implementação do dashboard principal.")
    print("")
    print("💡 DICA: Compare os logs do teste com os logs do dashboard")
    print("   para identificar onde está a diferença.")

if __name__ == "__main__":
    main()
