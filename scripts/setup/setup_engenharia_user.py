#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar usuário de teste da Engenharia e verificar acesso às RNCs
"""

import sqlite3
from werkzeug.security import generate_password_hash

def setup_engenharia_user():
    """Cria um usuário de teste da Engenharia"""
    print("=" * 80)
    print("CRIANDO USUÁRIO DE TESTE - ENGENHARIA")
    print("=" * 80)
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Verificar se já existe usuário da engenharia
    cursor.execute("SELECT id, name, department FROM users WHERE LOWER(department) = 'engenharia'")
    existing = cursor.fetchone()
    
    if existing:
        print(f"\n✅ Usuário da Engenharia já existe:")
        print(f"   ID: {existing[0]}")
        print(f"   Nome: {existing[1]}")
        print(f"   Departamento: {existing[2]}")
        user_id = existing[0]
    else:
        # Criar novo usuário da Engenharia
        print("\n📝 Criando novo usuário da Engenharia...")
        password_hash = generate_password_hash('engenharia123')
        
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, department, role, permissions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'Usuário Engenharia',
            'engenharia@ippel.com.br',
            password_hash,
            'Engenharia',
            'user',
            'view_own_rncs,edit_rncs'
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        print("✅ Usuário criado com sucesso!")
        print(f"   ID: {user_id}")
        print(f"   Email: engenharia@ippel.com.br")
        print(f"   Senha: engenharia123")
        print(f"   Departamento: Engenharia")
    
    # Verificar quantas RNCs o usuário terá acesso
    print("\n" + "=" * 80)
    print("VERIFICANDO ACESSO ÀS RNCs")
    print("=" * 80)
    
    # RNCs Finalizadas
    cursor.execute('''
        SELECT COUNT(DISTINCT r.id)
        FROM rncs r
        LEFT JOIN rnc_shares rs ON rs.rnc_id = r.id
        WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL)
          AND r.status = 'Finalizado'
          AND (
              r.user_id = ? 
              OR r.assigned_user_id = ? 
              OR rs.shared_with_user_id = ?
              OR LOWER(r.area_responsavel) = 'engenharia'
              OR LOWER(r.setor) = 'engenharia'
          )
    ''', (user_id, user_id, user_id))
    
    finalized_count = cursor.fetchone()[0]
    print(f"\n📊 RNCs Finalizadas acessíveis: {finalized_count}")
    
    # RNCs Ativas
    cursor.execute('''
        SELECT COUNT(DISTINCT r.id)
        FROM rncs r
        LEFT JOIN rnc_shares rs ON rs.rnc_id = r.id
        WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL)
          AND r.status NOT IN ('Finalizado')
          AND (
              r.user_id = ? 
              OR r.assigned_user_id = ? 
              OR rs.shared_with_user_id = ?
              OR LOWER(r.area_responsavel) = 'engenharia'
              OR LOWER(r.setor) = 'engenharia'
          )
    ''', (user_id, user_id, user_id))
    
    active_count = cursor.fetchone()[0]
    print(f"📊 RNCs Ativas acessíveis: {active_count}")
    
    # Mostrar algumas RNCs finalizadas da Engenharia
    print(f"\n📋 Primeiras 5 RNCs Finalizadas da Engenharia:")
    cursor.execute('''
        SELECT DISTINCT r.id, r.rnc_number, r.title, r.area_responsavel
        FROM rncs r
        WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL)
          AND r.status = 'Finalizado'
          AND (LOWER(r.area_responsavel) = 'engenharia' OR LOWER(r.setor) = 'engenharia')
        LIMIT 5
    ''')
    
    sample_rncs = cursor.fetchall()
    for rnc in sample_rncs:
        print(f"   • RNC #{rnc[0]}: {rnc[1]} - {rnc[2][:60]}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 80)
    print("\n💡 INSTRUÇÕES:")
    print("   1. Faça login com: engenharia@ippel.com.br / engenharia123")
    print(f"   2. Você terá acesso a {finalized_count} RNCs finalizadas")
    print(f"   3. E {active_count} RNCs ativas")
    print("\n")

if __name__ == "__main__":
    setup_engenharia_user()
