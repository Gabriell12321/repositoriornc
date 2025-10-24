#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar se as colunas de gerentes foram criadas corretamente
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'ippel_system.db')

def test_manager_columns():
    """Testa se as colunas de gerente existem na tabela groups"""
    print("=" * 60)
    print("TESTE: Verificando estrutura da tabela groups")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Obter info da tabela groups
    cursor.execute("PRAGMA table_info(groups)")
    columns = cursor.fetchall()
    
    print("\n📋 Colunas da tabela 'groups':")
    print("-" * 60)
    for col in columns:
        print(f"  {col[1]:30} | {col[2]:15} | PK: {col[5]}")
    
    # Verificar se as colunas existem
    column_names = [col[1] for col in columns]
    has_manager = 'manager_user_id' in column_names
    has_sub_manager = 'sub_manager_user_id' in column_names
    
    print("\n✅ Verificação:")
    print(f"  - manager_user_id existe: {has_manager}")
    print(f"  - sub_manager_user_id existe: {has_sub_manager}")
    
    if not has_manager or not has_sub_manager:
        print("\n❌ PROBLEMA: Colunas de gerentes não encontradas!")
        print("   Executando ALTER TABLE para adicionar...")
        
        try:
            if not has_manager:
                cursor.execute('ALTER TABLE groups ADD COLUMN manager_user_id INTEGER')
                print("   ✓ Coluna manager_user_id adicionada")
            
            if not has_sub_manager:
                cursor.execute('ALTER TABLE groups ADD COLUMN sub_manager_user_id INTEGER')
                print("   ✓ Coluna sub_manager_user_id adicionada")
            
            conn.commit()
            print("\n✅ Colunas adicionadas com sucesso!")
        except Exception as e:
            print(f"\n❌ Erro ao adicionar colunas: {e}")
    else:
        print("\n✅ Todas as colunas necessárias estão presentes!")
    
    # Mostrar grupos atuais
    print("\n" + "=" * 60)
    print("GRUPOS CADASTRADOS:")
    print("=" * 60)
    
    cursor.execute('''
        SELECT 
            g.id,
            g.name,
            g.manager_user_id,
            g.sub_manager_user_id,
            m.name as manager_name,
            sm.name as sub_manager_name
        FROM groups g
        LEFT JOIN users m ON g.manager_user_id = m.id
        LEFT JOIN users sm ON g.sub_manager_user_id = sm.id
        ORDER BY g.name
    ''')
    
    groups = cursor.fetchall()
    
    if groups:
        for group in groups:
            print(f"\n📁 {group[1]} (ID: {group[0]})")
            if group[4]:
                print(f"   🏆 Gerente: {group[4]} (ID: {group[2]})")
            else:
                print(f"   ⚠️ Gerente: Não definido")
            
            if group[5]:
                print(f"   👤 Sub-gerente: {group[5]} (ID: {group[3]})")
            else:
                print(f"   ⚠️ Sub-gerente: Não definido")
    else:
        print("  (Nenhum grupo encontrado)")
    
    conn.close()
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_manager_columns()
