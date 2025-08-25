#!/usr/bin/env python3
"""Script para testar e corrigir sistema de grupos"""

import sqlite3

DB_PATH = 'ippel_system.db'

print("🔧 Testando e corrigindo sistema de grupos...")

try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("\n📊 Usuários e seus departamentos:")
    cur.execute("SELECT id, name, email, department, role FROM users")
    users = cur.fetchall()
    for user in users:
        print(f"  ID: {user[0]}, Nome: {user[1]}, Email: {user[2]}, Depto: {user[3]}, Role: {user[4]}")
    
    print("\n📋 RNCs recentes:")
    cur.execute("SELECT id, rnc_number, title, department, user_id, status FROM rncs ORDER BY created_at DESC LIMIT 10")
    rncs = cur.fetchall()
    for rnc in rncs:
        print(f"  ID: {rnc[0]}, RNC: {rnc[1]}, Título: {rnc[2][:30]}..., Depto: {rnc[3]}, User: {rnc[4]}, Status: {rnc[5]}")
    
    # Simular busca de RNCs para um usuário da Engenharia
    print("\n🔍 Simulando busca para usuário da Engenharia:")
    cur.execute("SELECT id FROM users WHERE department = 'Engenharia' LIMIT 1")
    eng_user = cur.fetchone()
    if eng_user:
        eng_user_id = eng_user[0]
        print(f"  Usuário da Engenharia: ID {eng_user_id}")
        
        # RNCs que ele deveria ver (criadas por ele OU para o departamento Engenharia)
        cur.execute("""
            SELECT id, rnc_number, title, department, user_id 
            FROM rncs 
            WHERE user_id = ? OR department = 'Engenharia'
            ORDER BY created_at DESC LIMIT 5
        """, (eng_user_id,))
        
        rncs_for_eng = cur.fetchall()
        print(f"  RNCs que deveria ver: {len(rncs_for_eng)}")
        for rnc in rncs_for_eng:
            print(f"    - {rnc[1]}: {rnc[2][:30]}... (Depto: {rnc[3]}, User: {rnc[4]})")
    
    conn.close()
    print("\n✅ Teste concluído!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
