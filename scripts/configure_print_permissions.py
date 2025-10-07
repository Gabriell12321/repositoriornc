#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e configurar permissões de impressão de relatórios
"""

import sqlite3
import sys
import os

# Adicionar o caminho do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_existing_permissions():
    """Verifica permissões existentes no sistema"""
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar permissões existentes
        cursor.execute("SELECT DISTINCT permission_name FROM group_permissions ORDER BY permission_name")
        permissions = cursor.fetchall()
        
        print("🔍 PERMISSÕES EXISTENTES NO SISTEMA:")
        print("=" * 50)
        for perm in permissions:
            print(f"• {perm[0]}")
        
        # Verificar grupos existentes
        cursor.execute("SELECT id, name FROM groups ORDER BY name")
        groups = cursor.fetchall()
        
        print("\n👥 GRUPOS EXISTENTES:")
        print("=" * 30)
        for group in groups:
            print(f"• ID {group[0]}: {group[1]}")
        
        conn.close()
        return permissions, groups
        
    except Exception as e:
        print(f"❌ Erro ao verificar permissões: {e}")
        return [], []

def add_print_reports_permission():
    """Adiciona a permissão de impressão de relatórios"""
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar se a permissão já existe
        cursor.execute("SELECT COUNT(*) FROM group_permissions WHERE permission_name = 'can_print_reports'")
        exists = cursor.fetchone()[0]
        
        if exists > 0:
            print("✅ A permissão 'can_print_reports' já existe no sistema")
        else:
            # Adicionar permissão para todos os grupos existentes (inicialmente desabilitada)
            cursor.execute("SELECT id, name FROM groups")
            groups = cursor.fetchall()
            
            for group_id, group_name in groups:
                cursor.execute("""
                    INSERT INTO group_permissions (group_id, permission_name, permission_value)
                    VALUES (?, 'can_print_reports', 0)
                """, (group_id,))
                print(f"➕ Permissão 'can_print_reports' adicionada para o grupo '{group_name}' (desabilitada)")
            
            conn.commit()
            print("✅ Permissão 'can_print_reports' configurada com sucesso!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar permissão: {e}")
        return False

def enable_permission_for_group(group_id):
    """Habilita a permissão de impressão para um grupo específico"""
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar se o grupo existe
        cursor.execute("SELECT name FROM groups WHERE id = ?", (group_id,))
        group = cursor.fetchone()
        
        if not group:
            print(f"❌ Grupo com ID {group_id} não encontrado")
            return False
        
        # Habilitar a permissão
        cursor.execute("""
            UPDATE group_permissions 
            SET permission_value = 1 
            WHERE group_id = ? AND permission_name = 'can_print_reports'
        """, (group_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Permissão de impressão habilitada para o grupo '{group[0]}'")
            return True
        else:
            print(f"⚠️ Nenhuma permissão foi atualizada para o grupo '{group[0]}'")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao habilitar permissão: {e}")
        return False

def show_permission_status():
    """Mostra o status atual das permissões de impressão"""
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT g.id, g.name, 
                   COALESCE(gp.permission_value, 0) as can_print
            FROM groups g
            LEFT JOIN group_permissions gp ON g.id = gp.group_id 
                AND gp.permission_name = 'can_print_reports'
            ORDER BY g.name
        """)
        
        results = cursor.fetchall()
        
        print("\n📊 STATUS DAS PERMISSÕES DE IMPRESSÃO:")
        print("=" * 50)
        for group_id, group_name, can_print in results:
            status = "✅ HABILITADO" if can_print else "❌ DESABILITADO"
            print(f"• Grupo {group_id} ({group_name}): {status}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")

def main():
    """Função principal para configurar permissões de impressão"""
    print("🔧 CONFIGURADOR DE PERMISSÕES - IMPRESSÃO DE RELATÓRIOS")
    print("=" * 60)
    
    # 1. Verificar permissões existentes
    permissions, groups = check_existing_permissions()
    
    # 2. Adicionar a nova permissão se não existir
    add_print_reports_permission()
    
    # 3. Mostrar status atual
    show_permission_status()
    
    # 4. Oferecer opções para habilitar
    print("\n🎛️ OPÇÕES PARA HABILITAR PERMISSÃO:")
    print("Para habilitar a permissão de impressão para um grupo específico:")
    print("python configure_print_permissions.py --enable GROUP_ID")
    print("\nExemplo: python configure_print_permissions.py --enable 1")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--enable":
        if len(sys.argv) > 2:
            try:
                group_id = int(sys.argv[2])
                enable_permission_for_group(group_id)
                show_permission_status()
            except ValueError:
                print("❌ ID do grupo deve ser um número")
        else:
            print("❌ Uso: python configure_print_permissions.py --enable GROUP_ID")
    else:
        main()
