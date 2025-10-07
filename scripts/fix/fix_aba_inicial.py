#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para corrigir ordem de carregamento da aba inicial"""

file_path = r'templates\dashboard_improved.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar a linha 3789 (índice 3788) com switchTab dentro do setTimeout
# Mover para antes do setTimeout (linha 3782 aproximadamente)

# Remover switchTab da linha 3789 e linhas adjacentes
modified_lines = []
skip_next_blank = False

for i, line in enumerate(lines):
    line_num = i + 1
    
    # Remover switchTab e comentário da linha 3788-3789
    if line_num == 3788 and '// Garantir que a aba ativa' in line:
        skip_next_blank = True
        continue
    elif line_num == 3789 and "switchTab('active')" in line:
        continue
    elif line_num == 3790 and skip_next_blank and line.strip() == '':
        skip_next_blank = False
        continue
    
    # Adicionar switchTab ANTES do setTimeout (linha 3782)
    if line_num == 3782 and '}, 300);' in line:
        modified_lines.append(line)
        modified_lines.append('                \n')
        modified_lines.append('                // Garantir que a aba ativa seja mostrada IMEDIATAMENTE (fora do timeout)\n')
        modified_lines.append("                console.log('🎯 Forçando exibição da aba ATIVOS...');\n")
        modified_lines.append("                switchTab('active');\n")
        continue
    
    modified_lines.append(line)

# Salvar arquivo modificado
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(modified_lines)

print('✅ Arquivo corrigido com sucesso!')
print(f'📝 Total de linhas: {len(modified_lines)}')
print('🎯 switchTab("active") movido para ANTES do setTimeout de 300ms')
