#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar permissões do usuário admin
"""

import sqlite3
import json

def check_user_permissions():
    print("Verificando permissões do usuário admin...")
    
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar usuário admin
        cursor.execute("SELECT id, name, email, department, role, permissions FROM users WHERE email = 'admin@ippel.com.br'")
        user = cursor.fetchone()
        
        if user:
            print(f"Usuario encontrado: {user[1]} ({user[2]})")
            print(f"Departamento: {user[3]}")
            print(f"Role: {user[4]}")
            print(f"Permissoes: {user[5]}")
        else:
            print("Usuario admin nao encontrado!")
            return False
        
        # Verificar permissões específicas
        try:
            from services.permissions import has_permission
            user_id = user[0]
            
            permissions = [
                'view_all_rncs',
                'view_finalized_rncs', 
                'view_charts',
                'view_reports',
                'admin_access',
                'create_rnc'
            ]
            
            print("\nPermissoes do usuario:")
            for perm in permissions:
                has_perm = has_permission(user_id, perm)
                print(f"  {perm}: {has_perm}")
                
        except Exception as e:
            print(f"Erro ao verificar permissoes: {e}")
        
        # Verificar RNCs no banco
        cursor.execute("SELECT COUNT(*) FROM rncs")
        total_rncs = cursor.fetchone()[0]
        print(f"\nTotal de RNCs no banco: {total_rncs}")
        
        # Verificar RNCs por status
        cursor.execute("SELECT status, COUNT(*) FROM rncs GROUP BY status")
        status_counts = cursor.fetchall()
        print("RNCs por status:")
        for status, count in status_counts:
            print(f"  {status}: {count}")
        
        # Verificar algumas RNCs específicas
        cursor.execute("SELECT id, rnc_number, title, status, user_id FROM rncs LIMIT 5")
        sample_rncs = cursor.fetchall()
        print("\nPrimeiras 5 RNCs:")
        for rnc in sample_rncs:
            print(f"  ID: {rnc[0]}, Numero: {rnc[1]}, Titulo: {rnc[2]}, Status: {rnc[3]}, User: {rnc[4]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    check_user_permissions()
