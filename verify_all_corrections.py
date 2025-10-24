#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificação final - Lista todos os grupos e usuários corrigidos
"""

import sqlite3

DB_PATH = 'ippel_system.db'

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 100)
    print("📊 VERIFICAÇÃO FINAL - GRUPOS E USUÁRIOS")
    print("=" * 100)
    
    # Verificar grupos
    print("\n✅ GRUPOS CORRIGIDOS:")
    print("-" * 100)
    cursor.execute("SELECT id, name FROM groups ORDER BY name")
    groups = cursor.fetchall()
    
    for group_id, name in groups:
        # Verificar se há caracteres problemáticos
        has_error = '�' in name or 'Ã' in name
        status = "❌" if has_error else "✅"
        print(f"{status} ID {group_id:3d} | {name}")
    
    print(f"\nTotal de grupos: {len(groups)}")
    
    # Verificar usuários que foram corrigidos
    print("\n✅ USUÁRIOS CORRIGIDOS (amostra dos que tinham erros):")
    print("-" * 100)
    
    corrected_ids = [25, 31, 52, 57, 74, 92, 93, 112, 115, 116, 117, 118, 120, 121, 122, 136, 163, 185, 203, 220, 221]
    
    for user_id in corrected_ids:
        cursor.execute("SELECT id, name, (SELECT name FROM groups WHERE id = users.group_id) as grupo FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            user_id, name, grupo = result
            has_error = '�' in name or 'Ã' in name
            status = "❌" if has_error else "✅"
            print(f"{status} ID {user_id:3d} | {name:45s} | {grupo or 'Sem grupo'}")
    
    # Verificar se ainda há erros no banco todo
    print("\n🔍 VERIFICAÇÃO COMPLETA:")
    print("-" * 100)
    
    cursor.execute("SELECT COUNT(*) FROM groups WHERE name LIKE '%�%' OR name LIKE '%Ã%'")
    groups_with_errors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE name LIKE '%�%' OR name LIKE '%Ã%'")
    users_with_errors = cursor.fetchone()[0]
    
    if groups_with_errors == 0 and users_with_errors == 0:
        print("✅ SUCESSO! Nenhum erro de português encontrado!")
        print(f"   • {len(groups)} grupos verificados")
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        print(f"   • {total_users} usuários verificados")
    else:
        print(f"⚠️  Ainda há erros:")
        print(f"   • Grupos com erros: {groups_with_errors}")
        print(f"   • Usuários com erros: {users_with_errors}")
    
    print("\n" + "=" * 100)
    
    conn.close()

if __name__ == '__main__':
    main()
