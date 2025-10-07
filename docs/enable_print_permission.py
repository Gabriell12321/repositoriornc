import sqlite3
import os
import sys

def enable_print_permission():
    """
    Este script habilita a permissão de impressão para todos os grupos no sistema.
    """
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar se a permissão existe
        cursor.execute("SELECT * FROM permissions WHERE permission_name = 'can_print_reports'")
        permission = cursor.fetchone()
        
        if not permission:
            print("Permissão 'can_print_reports' não encontrada. Criando...")
            cursor.execute("""
                INSERT INTO permissions (permission_name, description) 
                VALUES ('can_print_reports', 'Permite imprimir relatórios de RNCs')
            """)
            conn.commit()
            
            # Obter o ID da permissão recém-criada
            cursor.execute("SELECT permission_id FROM permissions WHERE permission_name = 'can_print_reports'")
            permission_id = cursor.fetchone()[0]
        else:
            permission_id = permission[0]
            
        # Habilitar a permissão para todos os grupos
        print(f"Habilitando permissão de impressão (ID: {permission_id}) para todos os grupos...")
        
        # Verificar grupos existentes
        cursor.execute("SELECT group_id FROM groups")
        groups = cursor.fetchall()
        
        for group in groups:
            group_id = group[0]
            # Verificar se o grupo já tem a permissão
            cursor.execute("""
                SELECT * FROM group_permissions 
                WHERE group_id = ? AND permission_id = ?
            """, (group_id, permission_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Atualizar a permissão existente para habilitada (1)
                cursor.execute("""
                    UPDATE group_permissions 
                    SET enabled = 1 
                    WHERE group_id = ? AND permission_id = ?
                """, (group_id, permission_id))
                print(f"Atualizada permissão para o grupo ID {group_id}")
            else:
                # Adicionar a permissão para o grupo
                cursor.execute("""
                    INSERT INTO group_permissions (group_id, permission_id, enabled) 
                    VALUES (?, ?, 1)
                """, (group_id, permission_id))
                print(f"Adicionada permissão para o grupo ID {group_id}")
        
        # Confirmar as alterações
        conn.commit()
        print("Permissões de impressão habilitadas com sucesso!")
        
    except Exception as e:
        print(f"Erro ao atualizar permissões: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    enable_print_permission()
