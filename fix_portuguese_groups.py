#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir erros de português nos nomes dos grupos/setores
Uso: python fix_portuguese_groups.py
"""

import sqlite3
import os
import sys

# Configurar encoding UTF-8
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = 'ippel_system.db'

# Mapeamento de correções
CORRECTIONS = {
    # Formato: 'nome_errado_pattern': 'nome_correto'
    'Não Definidos': 'Não Definidos',  # Já está correto
    'N�o Definidos': 'Não Definidos',
    'Produ��o': 'Produção',
    'Produ�ao': 'Produção',
    'Producao': 'Produção',
    'Produ��o': 'Produção',
    'Usin. Cil�ndrica CNC': 'Usinagem Cilíndrica CNC',
    'Usin. Cilindrica CNC': 'Usinagem Cilíndrica CNC',
    'Usin. Cil�ndrica Convencional': 'Usinagem Cilíndrica Convencional',
    'Usin. Cilindrica Convencional': 'Usinagem Cilíndrica Convencional',
}

def fix_encoding(text):
    """Corrige problemas de encoding em texto"""
    if not text:
        return text
    
    # Dicionário de substituições de caracteres mal codificados
    replacements = {
        '�': 'ã',
        'ã': 'ã',
        '�': 'õ',
        'õ': 'õ',
        '�': 'á',
        'á': 'á',
        '�': 'é',
        'é': 'é',
        '�': 'í',
        'í': 'í',
        '�': 'ó',
        'ó': 'ó',
        '�': 'ú',
        'ú': 'ú',
        '�': 'â',
        'â': 'â',
        '�': 'ê',
        'ê': 'ê',
        '�': 'ô',
        'ô': 'ô',
        '�': 'ç',
        'ç': 'ç',
        'Ã£': 'ã',
        'Ã§': 'ç',
        'Ã©': 'é',
        'Ã³': 'ó',
        'Ãº': 'ú',
    }
    
    result = text
    for wrong, correct in replacements.items():
        result = result.replace(wrong, correct)
    
    return result

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Erro: Banco de dados '{DB_PATH}' não encontrado!")
        print(f"   Certifique-se de estar na pasta correta do projeto.")
        return 1
    
    print(f"📂 Conectando ao banco: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Listar grupos atuais
    print("\n📋 GRUPOS ANTES DA CORREÇÃO:")
    print("-" * 60)
    cursor.execute("SELECT id, name FROM groups ORDER BY name")
    groups_before = cursor.fetchall()
    
    for group_id, name in groups_before:
        print(f"  {group_id:3d} | {name}")
    
    # Fazer backup
    print(f"\n💾 Fazendo backup da tabela groups...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups_backup_portuguese_fix AS 
        SELECT * FROM groups
    """)
    conn.commit()
    
    # Corrigir encoding e nomes
    print(f"\n🔧 Aplicando correções...")
    corrections_made = 0
    
    cursor.execute("SELECT id, name FROM groups")
    all_groups = cursor.fetchall()
    
    for group_id, old_name in all_groups:
        new_name = fix_encoding(old_name)
        
        # Verificar mapeamento de correções
        for pattern, correct_name in CORRECTIONS.items():
            if pattern.lower() in new_name.lower() or pattern == new_name:
                new_name = correct_name
                break
        
        if new_name != old_name:
            print(f"  ✏️  ID {group_id:3d}: '{old_name}' → '{new_name}'")
            cursor.execute("UPDATE groups SET name = ? WHERE id = ?", (new_name, group_id))
            corrections_made += 1
    
    conn.commit()
    
    # Listar grupos após correção
    print("\n📋 GRUPOS APÓS CORREÇÃO:")
    print("-" * 60)
    cursor.execute("SELECT id, name FROM groups ORDER BY name")
    groups_after = cursor.fetchall()
    
    for group_id, name in groups_after:
        print(f"  {group_id:3d} | {name}")
    
    print(f"\n✅ Correções aplicadas: {corrections_made}")
    print(f"📊 Total de grupos: {len(groups_after)}")
    print(f"💾 Backup salvo em: groups_backup_portuguese_fix")
    
    conn.close()
    return 0

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
