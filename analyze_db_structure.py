#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar a estrutura do banco de dados IPPEL
"""

import sqlite3
import sys
import os

def analyze_database():
    db_path = 'ippel_system.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Arquivo {db_path} não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("📊 ANÁLISE DO BANCO DE DADOS IPPEL")
        print("=" * 60)
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n🗃️  TABELAS ENCONTRADAS ({len(tables)}):")
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n" + "=" * 60)
        
        # Analisar cada tabela
        for table in tables:
            table_name = table[0]
            print(f"\n📋 TABELA: {table_name}")
            print("-" * 40)
            
            # Estrutura da tabela
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("   COLUNAS:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_text = " [PK]" if pk else ""
                null_text = " NOT NULL" if not_null else ""
                default_text = f" DEFAULT {default_val}" if default_val else ""
                print(f"     {col_name} ({col_type}){pk_text}{null_text}{default_text}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   REGISTROS: {count}")
            
            # Mostrar alguns dados de exemplo (se houver)
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_data = cursor.fetchall()
                print("   EXEMPLO DE DADOS:")
                for i, row in enumerate(sample_data, 1):
                    print(f"     {i}: {row}")
        
        print("\n" + "=" * 60)
        print("🔍 ESTATÍSTICAS GERAIS")
        print("=" * 60)
        
        # Estatísticas específicas do sistema
        stats = {}
        
        # Verificar tabela users
        if any(t[0] == 'users' for t in tables):
            cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
            roles = cursor.fetchall()
            stats['users_by_role'] = dict(roles)
        
        # Verificar tabela rncs
        if any(t[0] == 'rncs' for t in tables):
            cursor.execute("SELECT COUNT(*) FROM rncs")
            stats['total_rncs'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT status, COUNT(*) FROM rncs GROUP BY status")
            statuses = cursor.fetchall()
            stats['rncs_by_status'] = dict(statuses)
            
            cursor.execute("SELECT priority, COUNT(*) FROM rncs GROUP BY priority")
            priorities = cursor.fetchall()
            stats['rncs_by_priority'] = dict(priorities)
        
        # Verificar tabela rnc_reports (possível tabela alternativa)
        if any(t[0] == 'rnc_reports' for t in tables):
            cursor.execute("SELECT COUNT(*) FROM rnc_reports")
            stats['total_rnc_reports'] = cursor.fetchone()[0]
        
        # Verificar tabela groups
        if any(t[0] == 'groups' for t in tables):
            cursor.execute("SELECT COUNT(*) FROM groups")
            stats['total_groups'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT name FROM groups")
            groups = cursor.fetchall()
            stats['group_names'] = [g[0] for g in groups]
        
        # Exibir estatísticas
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n" + "=" * 60)
        print("✅ Análise concluída!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao analisar banco: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    analyze_database()