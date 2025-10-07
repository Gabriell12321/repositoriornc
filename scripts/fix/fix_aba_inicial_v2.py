#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para corrigir ordem de carregamento da aba inicial - v2"""

file_path = r'templates\dashboard_improved.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Procurar e substituir o padrão específico
old_pattern = """                }, 300);
                
                // Inicializar seletores de ano e mês para desempenho por funcionário"""

new_pattern = """                }, 300);
                
                // Garantir que a aba ativa seja mostrada IMEDIATAMENTE
                console.log('🎯 Forçando exibição da aba ATIVOS...');
                switchTab('active');
                
                // Inicializar seletores de ano e mês para desempenho por funcionário"""

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ Arquivo corrigido com sucesso!')
    print('🎯 switchTab("active") adicionado IMEDIATAMENTE após timeout')
else:
    print('❌ Padrão não encontrado. Conteúdo ao redor:')
    # Mostrar o que tem próximo de "}, 300);"
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '}, 300);' in line and i > 3700:
            print(f'\nLinha {i}:')
            for j in range(max(0, i-2), min(len(lines), i+5)):
                print(f'{j}: {lines[j][:80]}')
            break
