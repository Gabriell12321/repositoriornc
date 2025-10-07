#!/usr/bin/env python3
"""Teste direto da API de grupos"""

from routes.field_locks import list_groups, check_admin
import sqlite3

print("=== TESTE DIRETO DA API ===")

# Teste 1: check_admin
print(f"1. check_admin() retorna: {check_admin()}")

# Teste 2: Conectar diretamente no banco
try:
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM groups ORDER BY name")
    groups = cursor.fetchall()
    print(f"2. Grupos no banco: {len(groups)} encontrados")
    for group in groups[:3]:  # Primeiros 3
        print(f"   - ID: {group[0]}, Nome: {group[1]}")
    conn.close()
except Exception as e:
    print(f"2. Erro ao acessar banco: {e}")

# Teste 3: Simular a função list_groups (sem Flask context)
try:
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, description, created_at
        FROM groups
        ORDER BY name
    """)
    
    groups = []
    for row in cursor.fetchall():
        groups.append({
            'id': row[0],
            'name': row[1],
            'description': row[2] or '',
            'created_at': row[3]
        })
    
    conn.close()
    
    print(f"3. Simulação list_groups: {len(groups)} grupos processados")
    print(f"   Resultado seria: {groups}")
    
except Exception as e:
    print(f"3. Erro na simulação: {e}")