#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar permissões atuais do sistema
"""

import sqlite3

def check_current_permissions():
    """Verifica as permissões atuais do sistema"""
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("🔍 Verificando permissões atuais do sistema...")
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Tabelas encontradas: {tables}")
        
        # Verificar grupos
        cursor.execute("SELECT id, name FROM groups")
        groups = cursor.fetchall()
        
        if not groups:
            print("❌ Nenhum grupo encontrado!")
            return
        
        print(f"\n👥 Grupos encontrados: {len(groups)}")
        
        # Para cada grupo, verificar permissões
        for group_id, group_name in groups:
            print(f"\n🔧 Grupo: {group_name} (ID: {group_id})")
            
            cursor.execute('''
                SELECT permission_name, permission_value 
                FROM group_permissions 
                WHERE group_id = ?
            ''', (group_id,))
            
            permissions = cursor.fetchall()
            
            if not permissions:
                print("  ❌ Nenhuma permissão configurada")
            else:
                print(f"  ✅ {len(permissions)} permissões configuradas:")
                for perm_name, perm_value in permissions:
                    status = "✅ ATIVA" if perm_value else "❌ INATIVA"
                    print(f"    - {perm_name}: {status}")
        
        # Verificar permissão específica que estava faltando
        print(f"\n🎯 Verificando permissão 'reply_rncs':")
        cursor.execute('''
            SELECT g.name, gp.permission_value 
            FROM groups g 
            LEFT JOIN group_permissions gp ON g.id = gp.group_id AND gp.permission_name = 'reply_rnc'
        ''')
        
        reply_perms = cursor.fetchall()
        for group_name, perm_value in reply_perms:
            status = "✅ CONFIGURADA" if perm_value else "❌ NÃO CONFIGURADA"
            print(f"  - {group_name}: {status}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar permissões: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_current_permissions()
