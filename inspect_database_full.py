#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para inspecionar completamente a estrutura do banco de dados SQLite
"""
import sqlite3
import os

db_path = r"C:\RNC\ippel_system.db"

if not os.path.exists(db_path):
    print(f"❌ Banco de dados não encontrado: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("📊 ESTRUTURA COMPLETA DO BANCO DE DADOS")
print("=" * 80)
print(f"Arquivo: {db_path}")
print(f"Tamanho: {os.path.getsize(db_path):,} bytes ({os.path.getsize(db_path) / 1024 / 1024:.2f} MB)")
print()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print(f"📋 TABELAS ({len(tables)}):")
print("-" * 80)
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  • {table}: {count:,} registros")
print()

# Detalhes de cada tabela
for table in tables:
    print("=" * 80)
    print(f"📦 TABELA: {table}")
    print("=" * 80)
    
    # Estrutura (colunas)
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    
    print(f"\n🔧 Colunas ({len(columns)}):")
    for col in columns:
        col_id, name, type_, notnull, default, pk = col
        pk_marker = " 🔑 PRIMARY KEY" if pk else ""
        null_marker = " NOT NULL" if notnull else ""
        default_marker = f" DEFAULT {default}" if default else ""
        print(f"  {col_id + 1:2d}. {name:30s} {type_:15s}{pk_marker}{null_marker}{default_marker}")
    
    # Foreign Keys
    cursor.execute(f"PRAGMA foreign_key_list({table})")
    fks = cursor.fetchall()
    if fks:
        print(f"\n🔗 Foreign Keys ({len(fks)}):")
        for fk in fks:
            id_, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
            print(f"  • {from_col} → {ref_table}.{to_col} (ON DELETE {on_delete}, ON UPDATE {on_update})")
    
    # Índices
    cursor.execute(f"PRAGMA index_list({table})")
    indexes = cursor.fetchall()
    if indexes:
        print(f"\n📑 Índices ({len(indexes)}):")
        for idx in indexes:
            seq, name, unique, origin, partial = idx
            unique_marker = " UNIQUE" if unique else ""
            print(f"  • {name}{unique_marker}")
    
    # Amostra de dados (primeira linha)
    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
    sample = cursor.fetchone()
    if sample and table == 'rncs':  # Mostrar amostra completa só da tabela rncs
        print(f"\n📄 Amostra de Dados (1 registro):")
        cursor.execute(f"PRAGMA table_info({table})")
        col_names = [col[1] for col in cursor.fetchall()]
        for col_name, value in zip(col_names, sample):
            display_value = str(value)[:50] + "..." if value and len(str(value)) > 50 else value
            print(f"  {col_name:30s} = {display_value}")
    
    print()

# Estatísticas importantes
print("=" * 80)
print("📈 ESTATÍSTICAS IMPORTANTES")
print("=" * 80)

# RNCs por status
cursor.execute("SELECT status, COUNT(*) FROM rncs GROUP BY status ORDER BY COUNT(*) DESC")
print("\n📊 RNCs por Status:")
for status, count in cursor.fetchall():
    print(f"  • {status}: {count:,}")

# RNCs por área
cursor.execute("SELECT area_responsavel, COUNT(*) FROM rncs WHERE area_responsavel IS NOT NULL GROUP BY area_responsavel ORDER BY COUNT(*) DESC")
print("\n🏢 RNCs por Área Responsável:")
for area, count in cursor.fetchall():
    print(f"  • {area}: {count:,}")

# Usuários
cursor.execute("SELECT id, email, name FROM users")
print("\n👥 Usuários:")
for user_id, email, name in cursor.fetchall():
    print(f"  • ID {user_id}: {email} ({name})")

# Integridade: RNCs sem user_id válido
cursor.execute("""
    SELECT COUNT(*) FROM rncs 
    WHERE user_id NOT IN (SELECT id FROM users)
""")
orphan_rncs = cursor.fetchone()[0]
print(f"\n⚠️  RNCs órfãs (sem user_id válido): {orphan_rncs}")

# Integridade: rnc_shares sem rnc_id válido
cursor.execute("""
    SELECT COUNT(*) FROM rnc_shares 
    WHERE rnc_id NOT IN (SELECT id FROM rncs)
""")
orphan_shares = cursor.fetchone()[0]
print(f"⚠️  Compartilhamentos órfãos (sem rnc_id válido): {orphan_shares}")

conn.close()

print()
print("=" * 80)
print("✅ Inspeção concluída!")
print("=" * 80)
