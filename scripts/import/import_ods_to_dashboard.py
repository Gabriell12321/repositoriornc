import pandas as pd
import os
import re
import json
from pathlib import Path

def extract_ods_data():
    """Extrai dados das planilhas ODS e prepara para integração no painel"""
    base_path = "ARQUIVOS PARA PUXAR INFORMAÇÕES PARA O PAINEL"
    
    # Dicionário para armazenar todos os dados
    all_data = {}
    
    # Lista dos anos para processar (16-25)
    years = range(16, 26)
    
    print("🔄 Extraindo dados das planilhas ODS...")
    print("=" * 60)
    
    for year in years:
        file_path = f"{base_path}/Levantamento RNC e Garantias {year}.ods"
        
        if not os.path.exists(file_path):
            print(f"⚠️ Arquivo não encontrado: {file_path}")
            continue
            
        try:
            print(f"\n📄 Processando: {file_path}")
            
            # Ler planilha
            df = pd.read_excel(file_path, engine='odf')
            
            # Encontrar linha com cabeçalhos dos departamentos
            header_row = None
            for idx, row in df.iterrows():
                row_str = ' '.join([str(val).lower() for val in row.values if pd.notna(val)])
                if 'produção' in row_str and 'engenharia' in row_str:
                    header_row = idx
                    break
            
            if header_row is None:
                print(f"   ❌ Não foi possível encontrar cabeçalho de departamentos")
                continue
            
            # Extrair dados a partir da linha seguinte ao cabeçalho
            data_start = header_row + 1
            year_data = []
            
            # Processar cada linha de dados
            for idx in range(data_start, len(df)):
                row = df.iloc[idx]
                
                # Verificar se a primeira coluna tem formato de data/mês
                date_cell = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
                
                # Pular linhas vazias ou linhas que não são dados mensais
                if not date_cell or date_cell == 'nan' or 'total' in date_cell.lower():
                    continue
                
                # Extrair mês/ano da célula de data
                month_match = re.search(r'(\d{1,2})/(\d{2})', date_cell)
                if not month_match:
                    continue
                
                month = int(month_match.group(1))
                year_from_data = int(month_match.group(2))
                
                # Verificar se o ano bate
                if year_from_data != year:
                    continue
                
                # Extrair valores por departamento
                monthly_data = {
                    'month': f"{month:02d}",
                    'year': f"20{year}",
                    'data': f"{month:02d}/{year}",
                    'departments': {}
                }
                
                # Mapear colunas para departamentos (ajustando para diferentes layouts)
                dept_mapping = {}
                header_values = [str(val).strip().lower() if pd.notna(val) else "" for val in df.iloc[header_row].values]
                
                for col_idx, header in enumerate(header_values):
                    if 'produção' in header:
                        dept_mapping['Produção'] = col_idx
                    elif 'engenharia' in header:
                        dept_mapping['Engenharia'] = col_idx
                    elif 'terceiros' in header:
                        dept_mapping['Terceiros'] = col_idx
                    elif 'compras' in header:
                        dept_mapping['Compras'] = col_idx
                    elif 'comercial' in header:
                        dept_mapping['Comercial'] = col_idx
                    elif 'pcp' in header:
                        dept_mapping['PCP'] = col_idx
                    elif 'expedição' in header:
                        dept_mapping['Expedição'] = col_idx
                    elif 'qualidade' in header:
                        dept_mapping['Qualidade'] = col_idx
                    elif 'transporte' in header:
                        dept_mapping['Transporte'] = col_idx
                    elif 'total' in header:
                        dept_mapping['Total'] = col_idx
                
                # Extrair valores para cada departamento
                total = 0
                for dept_name, col_idx in dept_mapping.items():
                    if col_idx < len(row):
                        value = row.iloc[col_idx]
                        if pd.notna(value) and isinstance(value, (int, float)):
                            monthly_data['departments'][dept_name] = float(value)
                            if dept_name != 'Total':
                                total += float(value)
                        else:
                            monthly_data['departments'][dept_name] = 0.0
                    else:
                        monthly_data['departments'][dept_name] = 0.0
                
                # Se não temos total calculado, usar o total da planilha
                if 'Total' in monthly_data['departments'] and monthly_data['departments']['Total'] > 0:
                    monthly_data['total'] = monthly_data['departments']['Total']
                else:
                    monthly_data['total'] = total
                
                year_data.append(monthly_data)
                print(f"   📅 {monthly_data['data']}: Total R$ {monthly_data['total']:,.2f}")
            
            if year_data:
                all_data[f"20{year}"] = year_data
                print(f"   ✅ {len(year_data)} meses processados para 20{year}")
            else:
                print(f"   ❌ Nenhum dado extraído para 20{year}")
                
        except Exception as e:
            print(f"   ❌ Erro ao processar {file_path}: {e}")
    
    return all_data

def generate_javascript_data(all_data):
    """Gera código JavaScript com os dados extraídos"""
    
    js_code = """
        // 📊 Dados Reais das Planilhas ODS (2016-2025)
        // Gerado automaticamente a partir das planilhas de levantamento
        
        const REAL_LEVANTAMENTO_DATA = {"""
    
    for year, year_data in all_data.items():
        js_code += f"""
            "{year}": {{
                "year": {year},
                "months": ["""
        
        for month_data in year_data:
            depts = month_data['departments']
            js_code += f"""
                    {{
                        "month": "{month_data['month']}",
                        "data": "{month_data['data']}",
                        "total": {month_data['total']},
                        "Produção": {depts.get('Produção', 0)},
                        "Engenharia": {depts.get('Engenharia', 0)},
                        "Terceiros": {depts.get('Terceiros', 0)},
                        "Compras": {depts.get('Compras', 0)},
                        "Comercial": {depts.get('Comercial', 0)},
                        "PCP": {depts.get('PCP', 0)},
                        "Expedição": {depts.get('Expedição', 0)},
                        "Qualidade": {depts.get('Qualidade', 0)},
                        "Transporte": {depts.get('Transporte', 0)}
                    }},"""
        
        js_code = js_code.rstrip(',')
        js_code += """
                ]
            },"""
    
    js_code = js_code.rstrip(',')
    js_code += """
        };
        
        // 🔄 Função para obter dados de um ano específico
        function getRealLevantamentoData(year) {
            const yearStr = year.toString();
            if (REAL_LEVANTAMENTO_DATA[yearStr]) {
                return REAL_LEVANTAMENTO_DATA[yearStr].months;
            }
            return null;
        }
        
        // 📈 Função para obter anos disponíveis
        function getAvailableYears() {
            return Object.keys(REAL_LEVANTAMENTO_DATA).map(y => parseInt(y)).sort();
        }"""
    
    return js_code

def update_dashboard_with_real_data():
    """Atualiza o dashboard com os dados reais das planilhas"""
    
    # Extrair dados das planilhas
    print("🔄 Iniciando extração de dados...")
    all_data = extract_ods_data()
    
    if not all_data:
        print("❌ Nenhum dado foi extraído das planilhas!")
        return
    
    # Gerar código JavaScript
    print("\n🔄 Gerando código JavaScript...")
    js_code = generate_javascript_data(all_data)
    
    # Atualizar a função loadLevByYear no dashboard
    dashboard_path = "templates/dashboard_improved.html"
    
    # Ler arquivo atual
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar e substituir a função loadLevByYear
    new_function = f"""        {js_code}
        
        async function loadLevByYear(){{
            try{{
                const sel = document.getElementById('levYearSelect');
                const year = parseInt(sel && sel.value ? sel.value : '2016', 10);
                
                // Tentar usar dados reais primeiro
                const realData = getRealLevantamentoData(year);
                let mockData = [];
                
                if (realData) {{
                    // Usar dados reais das planilhas
                    mockData = realData.map(monthData => ({{
                        'Data': monthData.data,
                        'Total': monthData.total,
                        'Produção': monthData.Produção,
                        'Engenharia': monthData.Engenharia,
                        'Terceiros': monthData.Terceiros,
                        'Compras': monthData.Compras,
                        'Comercial': monthData.Comercial,
                        'PCP': monthData.PCP,
                        'Expedição': monthData.Expedição,
                        'Qualidade': monthData.Qualidade,
                        'Transporte': monthData.Transporte
                    }})));
                    
                    console.log(`📊 Dados reais carregados para ${{year}}: ${{realData.length}} meses`);
                }} else {{
                    // Fallback para dados simulados
                    const months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];
                    const baseData = {{
                        2013: [120, 110, 150, 100, 130, 95, 125, 110, 100, 105, 120, 85],
                        2014: [133, 117, 163, 110, 142, 109, 136, 121, 108, 117, 131, 98],
                        2015: [100, 120, 137, 107, 137, 205, 148, 102, 53, 61, 55, 53]
                    }};
                    
                    const counts = baseData[year] || baseData[2014];
                    
                    for(let i = 0; i < 12; i++) {{
                        const monthData = {{
                            'Data': `${{months[i]}}/${{String(year).slice(-2)}}`,
                            'Total': counts[i] || 0
                        }};
                        const total = monthData.Total;
                        monthData['Produção'] = Math.floor(total * 0.28);
                        monthData['Engenharia'] = Math.floor(total * 0.18);
                        monthData['Qualidade'] = Math.floor(total * 0.16);
                        monthData['Terceiros'] = Math.floor(total * 0.12);
                        monthData['Compras'] = Math.floor(total * 0.08);
                        monthData['Comercial'] = Math.floor(total * 0.06);
                        monthData['PCP'] = Math.floor(total * 0.05);
                        monthData['Expedição'] = Math.floor(total * 0.04);
                        monthData['Transporte'] = Math.floor(total * 0.03);
                        
                        mockData.push(monthData);
                    }}
                    
                    console.log(`📋 Dados simulados carregados para ${{year}}`);
                }}
                
                // Atualizar tabela
                const rows = mockData.map(obj => [obj['Data'], obj['Produção'], obj['Engenharia'], obj['Terceiros'], obj['Compras'], obj['Comercial'], obj['PCP'], obj['Expedição'], obj['Qualidade'], obj['Transporte'], obj['Total']]);
                renderLev1415(rows, []);
                
                // Atualizar gráfico Total por Mês
                const labels = mockData.map(o => o['Data']);
                const totals = mockData.map(o => o['Total']);
                const ctx1 = document.getElementById('levTotalMes');
                if (ctx1){{
                    if (window._levTotalMesChart) window._levTotalMesChart.destroy();
                    
                    // Cores baseadas no ano
                    const colors = {{
                        2013: '#6c757d', 2014: '#0d6efd', 2015: '#198754', 2016: '#fd7e14',
                        2017: '#dc3545', 2018: '#6610f2', 2019: '#20c997', 2020: '#ffc107',
                        2021: '#d63384', 2022: '#6f42c1', 2023: '#e83e8c', 2024: '#17a2b8', 2025: '#28a745'
                    }};
                    const color = colors[year] || '#0d6efd';
                    
                    // Determinar tipo de dados (valores ou contagem)
                    const isMonetary = realData && totals.some(t => t > 1000);
                    const dataLabel = isMonetary ? `Total (R$) ${{year}}` : `Total RNCs ${{year}}`;
                    const yAxisLabel = isMonetary ? 'Valores (R$)' : 'Quantidade de RNCs';
                    
                    window._levTotalMesChart = new Chart(ctx1.getContext('2d'), {{ 
                        type:'line', 
                        data:{{ 
                            labels, 
                            datasets:[{{ 
                                label: dataLabel, 
                                data: totals, 
                                borderColor: color, 
                                backgroundColor: color.replace(')', ',0.1)').replace('rgb', 'rgba'), 
                                tension:.35,
                                pointBackgroundColor: color,
                                pointBorderColor: '#ffffff',
                                pointBorderWidth: 2,
                                pointRadius: 5,
                                pointHoverRadius: 8,
                                fill: true
                            }}] 
                        }}, 
                        options:{{ 
                            responsive: true, 
                            maintainAspectRatio: false,
                            interaction: {{
                                intersect: false,
                                mode: 'index'
                            }},
                            plugins: {{
                                legend: {{
                                    display: true,
                                    position: 'top',
                                    labels: {{
                                        font: {{ size: 12, weight: 'bold' }},
                                        color: '#333'
                                    }}
                                }},
                                title: {{
                                    display: true,
                                    text: `📈 ${{dataLabel.replace('Total', 'Total por Mês')}}`,
                                    color: '#333',
                                    font: {{ size: 16, weight: 'bold' }}
                                }},
                                tooltip: {{
                                    backgroundColor: 'rgba(0,0,0,0.8)',
                                    titleColor: '#fff',
                                    bodyColor: '#fff',
                                    borderColor: color,
                                    borderWidth: 1,
                                    callbacks: {{
                                        label: function(context) {{
                                            const value = context.parsed.y;
                                            if (isMonetary) {{
                                                return `${{context.dataset.label}}: R$ ${{value.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}`;
                                            }} else {{
                                                return `${{context.dataset.label}}: ${{value}} RNCs`;
                                            }}
                                        }}
                                    }}
                                }}
                            }},
                            scales: {{
                                y: {{
                                    beginAtZero: true,
                                    grid: {{ 
                                        color: 'rgba(0,0,0,0.1)',
                                        drawBorder: false
                                    }},
                                    title: {{
                                        display: true,
                                        text: yAxisLabel,
                                        font: {{ size: 12, weight: 'bold' }}
                                    }},
                                    ticks: {{
                                        font: {{ size: 11 }},
                                        callback: function(value) {{
                                            if (isMonetary) {{
                                                return 'R$ ' + value.toLocaleString('pt-BR');
                                            }} else {{
                                                return value;
                                            }}
                                        }}
                                    }}
                                }},
                                x: {{
                                    grid: {{ 
                                        color: 'rgba(0,0,0,0.1)',
                                        drawBorder: false
                                    }},
                                    title: {{
                                        display: true,
                                        text: 'Mês/Ano',
                                        font: {{ size: 12, weight: 'bold' }}
                                    }},
                                    ticks: {{
                                        font: {{ size: 11 }}
                                    }}
                                }}
                            }}
                        }} 
                    }});
                }}
                
                // Atualizar gráfico por departamento do último mês com dados não zero
                const last = mockData.slice().reverse().find(r => (r && r['Total'] > 0)) || mockData[mockData.length - 1] || {{}};
                const depts = ['Produção','Engenharia','Terceiros','Compras','Comercial','PCP','Expedição','Qualidade','Transporte'];
                const ctx2 = document.getElementById('levPorDept');
                if (ctx2){{
                    if (window._levPorDeptChart) window._levPorDeptChart.destroy();
                    
                    const isMonetary = realData && Object.values(last).some(v => typeof v === 'number' && v > 1000);
                    const deptLabel = isMonetary ? `Valores por Departamento (${{last['Data']||''}})` : `RNCs por Departamento (${{last['Data']||''}})`;
                    const yAxisLabel = isMonetary ? 'Valores (R$)' : 'Quantidade de RNCs';
                    
                    window._levPorDeptChart = new Chart(ctx2.getContext('2d'), {{ 
                        type:'bar', 
                        data:{{ 
                            labels: depts, 
                            datasets:[{{ 
                                label: deptLabel, 
                                data: depts.map(d => last[d]||0), 
                                backgroundColor:[
                                    'rgba(13,110,253,0.8)',
                                    'rgba(102,16,242,0.8)', 
                                    'rgba(111,66,193,0.8)',
                                    'rgba(214,51,132,0.8)',
                                    'rgba(220,53,69,0.8)',
                                    'rgba(253,126,20,0.8)',
                                    'rgba(255,193,7,0.8)',
                                    'rgba(25,135,84,0.8)',
                                    'rgba(32,201,151,0.8)'
                                ],
                                borderColor:[
                                    '#0d6efd','#6610f2','#6f42c1','#d63384','#dc3545','#fd7e14','#ffc107','#198754','#20c997'
                                ],
                                borderWidth: 2,
                                borderRadius: 4,
                                borderSkipped: false
                            }}] 
                        }}, 
                        options:{{ 
                            responsive: true, 
                            maintainAspectRatio: false,
                            interaction: {{
                                intersect: false,
                                mode: 'index'
                            }},
                            plugins: {{
                                legend: {{
                                    display: true,
                                    position: 'top',
                                    labels: {{
                                        font: {{ size: 12, weight: 'bold' }},
                                        color: '#333'
                                    }}
                                }},
                                title: {{
                                    display: true,
                                    text: `🏭 ${{deptLabel}}`,
                                    color: '#333',
                                    font: {{ size: 16, weight: 'bold' }}
                                }},
                                tooltip: {{
                                    backgroundColor: 'rgba(0,0,0,0.8)',
                                    titleColor: '#fff',
                                    bodyColor: '#fff',
                                    borderWidth: 1,
                                    callbacks: {{
                                        label: function(context) {{
                                            const value = context.parsed.y;
                                            if (isMonetary) {{
                                                return `${{context.dataset.label.split(' ')[0]}}: R$ ${{value.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}`;
                                            }} else {{
                                                return `${{context.dataset.label.split(' ')[0]}}: ${{value}} RNCs`;
                                            }}
                                        }}
                                    }}
                                }}
                            }},
                            scales: {{
                                y: {{
                                    beginAtZero: true,
                                    grid: {{ 
                                        color: 'rgba(0,0,0,0.1)',
                                        drawBorder: false
                                    }},
                                    title: {{
                                        display: true,
                                        text: yAxisLabel,
                                        font: {{ size: 12, weight: 'bold' }}
                                    }},
                                    ticks: {{
                                        font: {{ size: 11 }},
                                        callback: function(value) {{
                                            if (isMonetary) {{
                                                return 'R$ ' + value.toLocaleString('pt-BR');
                                            }} else {{
                                                return value;
                                            }}
                                        }}
                                    }}
                                }},
                                x: {{
                                    grid: {{ 
                                        display: false
                                    }},
                                    title: {{
                                        display: true,
                                        text: 'Departamentos',
                                        font: {{ size: 12, weight: 'bold' }}
                                    }},
                                    ticks: {{
                                        font: {{ size: 10 }},
                                        maxRotation: 45,
                                        minRotation: 0
                                    }}
                                }}
                            }}
                        }} 
                    }});
                }}
            }}catch(e){{ console.error('Erro loadLevByYear:', e); }}
        }}"""
    
    # Padrão para encontrar a função loadLevByYear existente
    pattern = r'async function loadLevByYear\(\)\{.*?\n        \}'
    
    if re.search(pattern, content, re.DOTALL):
        # Substituir função existente
        new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
        print("✅ Função loadLevByYear encontrada e substituída")
    else:
        print("⚠️ Função loadLevByYear não encontrada, adicionando no final do script")
        # Adicionar antes do fechamento do script
        script_end = content.rfind('</script>')
        new_content = content[:script_end] + new_function + '\n    ' + content[script_end:]
    
    # Atualizar também a função fillYearSelect para incluir os anos reais
    years_available = sorted([int(y) for y in all_data.keys()])
    fill_years_function = f"""        function fillYearSelect() {{
            const sel = document.getElementById('levYearSelect');
            if (!sel) return;
            
            sel.innerHTML = '';
            
            // Anos com dados reais das planilhas
            const realYears = {years_available};
            
            // Anos simulados
            const simulatedYears = [2013, 2014, 2015];
            
            // Combinar e ordenar todos os anos
            const allYears = [...new Set([...simulatedYears, ...realYears])].sort();
            
            allYears.forEach(year => {{
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year + (realYears.includes(year) ? ' ✓' : ' *');
                if (year === {years_available[0] if years_available else 2016}) option.selected = true; // Default para primeiro ano com dados reais
                sel.appendChild(option);
            }});
            
            // Adicionar legenda
            const legend = document.createElement('small');
            legend.style.color = '#666';
            legend.style.fontSize = '10px';
            legend.innerHTML = '<br>✓ = Dados reais das planilhas | * = Dados simulados';
            sel.parentNode.appendChild(legend);
        }}"""
    
    # Substituir função fillYearSelect
    fill_pattern = r'function fillYearSelect\(\) \{.*?\n        \}'
    if re.search(fill_pattern, new_content, re.DOTALL):
        new_content = re.sub(fill_pattern, fill_years_function, new_content, flags=re.DOTALL)
        print("✅ Função fillYearSelect atualizada com anos reais")
    
    # Salvar arquivo atualizado
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # Salvar dados em arquivo JSON para backup (em data/)
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    data_dir = root / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    with open(data_dir / 'levantamento_data_backup.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Dashboard atualizado com dados reais!")
    print(f"📊 Anos processados: {', '.join(sorted(all_data.keys()))}")
    print(f"📁 Backup salvo em: {str((data_dir / 'levantamento_data_backup.json').relative_to(root))}")
    print(f"🔄 Arquivo atualizado: {dashboard_path}")

if __name__ == "__main__":
    update_dashboard_with_real_data()
