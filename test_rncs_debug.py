#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para diagnosticar o problema das RNCs sendo atribuídas apenas ao administrador
"""

import sqlite3
import os

# Configurações
DB_PATH = "ippel_system.db"  # Banco de dados correto

def check_database_structure():
    """Verifica a estrutura da tabela RNCs"""
    print("🔍 Verificando estrutura da tabela RNCs...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(rncs)")
        cols = cursor.fetchall()
        
        print("📋 Estrutura da tabela RNCs:")
        for col in cols:
            print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PK' if col[5] else ''}")
        
        # Verificar se há índices
        cursor.execute("PRAGMA index_list(rncs)")
        indexes = cursor.fetchall()
        print(f"\n🔗 Índices da tabela RNCs: {len(indexes)}")
        for idx in indexes:
            print(f"   {idx[1]} ({'UNIQUE' if idx[2] else 'NORMAL'})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False

def check_rnc_data_distribution():
    """Verifica a distribuição dos dados de RNCs"""
    print("\n📊 Verificando distribuição dos dados de RNCs...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total de RNCs
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
        total_rncs = cursor.fetchone()[0]
        print(f"📈 Total de RNCs (não deletadas): {total_rncs}")
        
        # RNCs por status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM rncs 
            WHERE is_deleted = 0
            GROUP BY status
            ORDER BY count DESC
        """)
        status_data = cursor.fetchall()
        print(f"\n📋 RNCs por status:")
        for status, count in status_data:
            print(f"   {status}: {count}")
        
        # RNCs por usuário (top 20)
        cursor.execute("""
            SELECT r.user_id, u.name, COUNT(*) as count
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.is_deleted = 0
            GROUP BY r.user_id, u.name
            ORDER BY count DESC
            LIMIT 20
        """)
        user_data = cursor.fetchall()
        print(f"\n👥 Top 20 usuários por RNCs:")
        for user_id, name, count in user_data:
            print(f"   ID {user_id}: {name or 'Nome não definido'} - {count} RNCs")
        
        # Verificar RNCs com user_id NULL
        cursor.execute("""
            SELECT COUNT(*) as null_count
            FROM rncs 
            WHERE user_id IS NULL AND is_deleted = 0
        """)
        null_count = cursor.fetchone()[0]
        print(f"\n⚠️ RNCs com user_id NULL: {null_count}")
        
        # Verificar RNCs do administrador (ID 1)
        cursor.execute("""
            SELECT COUNT(*) as admin_count
            FROM rncs 
            WHERE user_id = 1 AND is_deleted = 0
        """)
        admin_count = cursor.fetchone()[0]
        print(f"👑 RNCs do administrador (ID 1): {admin_count}")
        
        # Verificar RNCs por departamento
        cursor.execute("""
            SELECT u.department, COUNT(*) as count
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.is_deleted = 0 AND u.department IS NOT NULL
            GROUP BY u.department
            ORDER BY count DESC
        """)
        dept_data = cursor.fetchall()
        print(f"\n🏢 RNCs por departamento:")
        for dept, count in dept_data:
            print(f"   {dept}: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")
        import traceback
        traceback.print_exc()

def check_sample_rncs():
    """Verifica algumas RNCs de exemplo para entender o problema"""
    print("\n🔍 Verificando RNCs de exemplo...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar algumas RNCs recentes
        cursor.execute("""
            SELECT r.id, r.user_id, u.name, r.status, r.created_at
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.is_deleted = 0
            ORDER BY r.created_at DESC
            LIMIT 10
        """)
        sample_rncs = cursor.fetchall()
        
        print(f"📝 Últimas 10 RNCs criadas:")
        for rnc_id, user_id, user_name, status, created_at in sample_rncs:
            print(f"   RNC {rnc_id}: Usuário ID {user_id} ({user_name}) - Status: {status} - Criada: {created_at}")
        
        # Verificar RNCs com status específicos
        cursor.execute("""
            SELECT r.id, r.user_id, u.name, r.status
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.status IN ('Finalizado', 'finalized') 
              AND r.is_deleted = 0
            ORDER BY r.created_at DESC
            LIMIT 10
        """)
        finalized_rncs = cursor.fetchall()
        
        print(f"\n✅ Últimas 10 RNCs finalizadas:")
        for rnc_id, user_id, user_name, status in finalized_rncs:
            print(f"   RNC {rnc_id}: Usuário ID {user_id} ({user_name}) - Status: {status}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar RNCs de exemplo: {e}")
        import traceback
        traceback.print_exc()

def check_users_table():
    """Verifica a tabela de usuários"""
    print("\n👥 Verificando tabela de usuários...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total de usuários
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        print(f"📊 Total de usuários: {total_users}")
        
        # Usuários ativos
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1 OR is_active IS NULL")
        active_users = cursor.fetchone()[0]
        print(f"✅ Usuários ativos: {active_users}")
        
        # Listar alguns usuários
        cursor.execute("""
            SELECT id, name, department, is_active
            FROM users
            ORDER BY id
            LIMIT 10
        """)
        users = cursor.fetchall()
        
        print(f"\n👤 Primeiros 10 usuários:")
        for user_id, name, department, is_active in users:
            status = "✅ Ativo" if (is_active == 1 or is_active is None) else "❌ Inativo"
            print(f"   ID {user_id}: {name} - {department or 'Sem departamento'} - {status}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar usuários: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🚀 Iniciando diagnóstico das RNCs...")
    print(f"🗄️ Banco de dados: {DB_PATH}")
    
    # Verificar estrutura
    if not check_database_structure():
        return
    
    # Verificar dados
    check_rnc_data_distribution()
    check_sample_rncs()
    check_users_table()
    
    print("\n✨ Diagnóstico concluído!")
    print("\n💡 Recomendações:")
    print("1. Verifique se as RNCs têm user_id correto")
    print("2. Confirme se não há triggers ou procedures alterando user_id")
    print("3. Verifique se o frontend está enviando user_id correto")
    print("4. Teste a API de debug: /api/debug/rncs")

if __name__ == "__main__":
    main()
