#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from datetime import datetime

def analyze_database():
    """Análise completa da estrutura do banco de dados IPPEL RNC"""
    
    db_path = 'ippel_system.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("📊 ANÁLISE COMPLETA DO BANCO DE DADOS IPPEL RNC")
        print("=" * 80)
        print(f"📅 Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📁 Arquivo: {db_path}")
        
        # 1. Obter lista de tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 TABELAS ENCONTRADAS: {len(tables)}")
        print("-" * 50)
        
        table_info = {}
        
        for table_name in tables:
            table_name = table_name[0]
            print(f"\n🔍 Tabela: {table_name}")
            
            # Obter informações das colunas
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            print(f"   📊 Registros: {count}")
            print(f"   📝 Colunas ({len(columns)}):")
            
            column_info = []
            for col in columns:
                col_id, col_name, col_type, not_null, default_value, primary_key = col
                pk_indicator = " (PK)" if primary_key else ""
                nn_indicator = " NOT NULL" if not_null else ""
                default_indicator = f" DEFAULT {default_value}" if default_value else ""
                
                column_detail = f"      • {col_name}: {col_type}{pk_indicator}{nn_indicator}{default_indicator}"
                print(column_detail)
                
                column_info.append({
                    'name': col_name,
                    'type': col_type,
                    'not_null': bool(not_null),
                    'default_value': default_value,
                    'primary_key': bool(primary_key)
                })
            
            table_info[table_name] = {
                'columns': column_info,
                'record_count': count
            }
            
            # Obter chaves estrangeiras
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            if foreign_keys:
                print(f"   🔗 Chaves Estrangeiras:")
                for fk in foreign_keys:
                    print(f"      • {fk[3]} → {fk[2]}.{fk[4]}")
        
        # 2. Análise específica da tabela RNCs
        print("\n" + "=" * 80)
        print("🎯 ANÁLISE DETALHADA DA TABELA 'rncs'")
        print("=" * 80)
        
        if 'rncs' in [t[0] for t in tables]:
            # Status das RNCs
            cursor.execute("SELECT status, COUNT(*) FROM rncs GROUP BY status ORDER BY COUNT(*) DESC")
            statuses = cursor.fetchall()
            print("\n📈 Distribuição por Status:")
            for status, count in statuses:
                print(f"   • {status}: {count}")
            
            # Prioridades
            cursor.execute("SELECT priority, COUNT(*) FROM rncs GROUP BY priority ORDER BY COUNT(*) DESC")
            priorities = cursor.fetchall()
            print("\n🚨 Distribuição por Prioridade:")
            for priority, count in priorities:
                print(f"   • {priority}: {count}")
            
            # Departamentos
            cursor.execute("SELECT department, COUNT(*) FROM rncs WHERE department IS NOT NULL GROUP BY department ORDER BY COUNT(*) DESC")
            departments = cursor.fetchall()
            print("\n🏢 Distribuição por Departamento:")
            for dept, count in departments:
                print(f"   • {dept}: {count}")
            
            # RNCs por usuário
            cursor.execute("""
                SELECT u.name, u.department, COUNT(r.id) as total_rncs
                FROM users u
                LEFT JOIN rncs r ON u.id = r.user_id
                GROUP BY u.id, u.name, u.department
                HAVING total_rncs > 0
                ORDER BY total_rncs DESC
                LIMIT 10
            """)
            user_rncs = cursor.fetchall()
            print("\n👤 Top 10 Usuários por RNCs Criadas:")
            for name, dept, count in user_rncs:
                print(f"   • {name} ({dept}): {count} RNCs")
            
            # RNCs finalizadas vs ativas
            cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Finalizado'")
            finalized = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM rncs WHERE status != 'Finalizado' AND is_deleted = 0")
            active = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 1")
            deleted = cursor.fetchone()[0]
            
            print(f"\n📊 Resumo Geral:")
            print(f"   • RNCs Ativas: {active}")
            print(f"   • RNCs Finalizadas: {finalized}")
            print(f"   • RNCs Excluídas: {deleted}")
            print(f"   • Total: {active + finalized + deleted}")
            
            # Valor total das RNCs
            cursor.execute("SELECT SUM(price) FROM rncs WHERE price IS NOT NULL")
            total_value = cursor.fetchone()[0] or 0
            print(f"   • Valor Total: R$ {total_value:,.2f}")
            
        # 3. Análise da tabela de usuários
        print("\n" + "=" * 80)
        print("👥 ANÁLISE DETALHADA DA TABELA 'users'")
        print("=" * 80)
        
        if 'users' in [t[0] for t in tables]:
            # Usuários por departamento
            cursor.execute("SELECT department, COUNT(*) FROM users WHERE is_active = 1 GROUP BY department ORDER BY COUNT(*) DESC")
            user_depts = cursor.fetchall()
            print("\n🏢 Usuários por Departamento:")
            for dept, count in user_depts:
                print(f"   • {dept}: {count}")
            
            # Usuários por role
            cursor.execute("SELECT role, COUNT(*) FROM users WHERE is_active = 1 GROUP BY role ORDER BY COUNT(*) DESC")
            user_roles = cursor.fetchall()
            print("\n🔐 Usuários por Função:")
            for role, count in user_roles:
                print(f"   • {role}: {count}")
        
        # 4. Análise de grupos e permissões
        print("\n" + "=" * 80)
        print("🔐 ANÁLISE DE GRUPOS E PERMISSÕES")
        print("=" * 80)
        
        if 'groups' in [t[0] for t in tables]:
            cursor.execute("""
                SELECT g.name, g.description, COUNT(u.id) as user_count
                FROM groups g
                LEFT JOIN users u ON g.id = u.group_id AND u.is_active = 1
                GROUP BY g.id, g.name, g.description
                ORDER BY user_count DESC
            """)
            groups = cursor.fetchall()
            print("\n👥 Grupos existentes:")
            for name, desc, count in groups:
                print(f"   • {name}: {count} usuários")
                if desc:
                    print(f"     Descrição: {desc}")
        
        # 5. Índices da base de dados
        print("\n" + "=" * 80)
        print("📇 ÍNDICES DA BASE DE DADOS")
        print("=" * 80)
        
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        indexes = cursor.fetchall()
        print(f"\n🔍 Índices encontrados: {len(indexes)}")
        for name, table, sql in indexes:
            print(f"   • {name} (tabela: {table})")
            if sql:
                print(f"     SQL: {sql}")
        
        # 6. Salvar análise em JSON
        output_file = f"database_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'database_file': db_path,
            'tables': table_info,
            'analysis': {
                'total_tables': len(tables),
                'total_users': table_info.get('users', {}).get('record_count', 0),
                'total_rncs': table_info.get('rncs', {}).get('record_count', 0),
                'total_groups': table_info.get('groups', {}).get('record_count', 0)
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Análise salva em: {output_file}")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro durante a análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_database()
