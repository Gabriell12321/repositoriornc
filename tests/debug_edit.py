#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug do sistema de edição de RNCs
"""
import sqlite3
import json

def debug_edit_permissions():
    """Debug das permissões de edição"""
    print("🔍 DEBUG - Sistema de Edição de RNCs")
    print("=" * 50)
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # 1. Verificar usuários e suas permissões de edição
    print("\n1. 👥 Usuários e permissões de edição:")
    cursor.execute('''
        SELECT u.id, u.name, u.email, g.name as group_name,
               GROUP_CONCAT(gp.permission_name) as permissions
        FROM users u
        LEFT JOIN groups g ON u.group_id = g.id
        LEFT JOIN group_permissions gp ON g.id = gp.group_id AND gp.permission_value = 1
        WHERE u.is_active = 1 AND (gp.permission_name LIKE '%edit%' OR gp.permission_name IS NULL)
        GROUP BY u.id
        LIMIT 5
    ''')
    
    users = cursor.fetchall()
    for user in users:
        print(f"   👤 {user[1]} ({user[2]})")
        print(f"      🏢 Grupo: {user[3]}")
        permissions = user[4].split(',') if user[4] else []
        edit_perms = [p for p in permissions if 'edit' in p]
        print(f"      ✏️ Permissões de edição: {edit_perms}")
        print()
    
    # 2. Verificar RNCs existentes
    print("2. 📁 RNCs disponíveis para teste:")
    cursor.execute('''
        SELECT id, rnc_number, title, user_id, status, created_at
        FROM rncs
        WHERE is_deleted = 0
        ORDER BY created_at DESC
        LIMIT 5
    ''')
    
    rncs = cursor.fetchall()
    for rnc in rncs:
        print(f"   📄 RNC {rnc[0]}: {rnc[1]} - {rnc[2]}")
        print(f"      👤 Criador: ID {rnc[3]}")
        print(f"      📊 Status: {rnc[4]}")
        print()
    
    # 3. Simular verificação de permissões para cada usuário
    print("3. 🧪 Simulação de permissões de edição:")
    
    if users and rncs:
        test_user = users[0]  # Primeiro usuário
        test_rnc = rncs[0]    # Primeiro RNC
        
        user_id = test_user[0]
        rnc_creator_id = test_rnc[3]
        
        print(f"   🎯 Testando usuário: {test_user[1]} (ID: {user_id})")
        print(f"   📄 Testando RNC: {test_rnc[1]} (Criador ID: {rnc_creator_id})")
        
        # Verificar permissões específicas
        cursor.execute('''
            SELECT gp.permission_name, gp.permission_value
            FROM group_permissions gp
            JOIN users u ON u.group_id = gp.group_id
            WHERE u.id = ? AND gp.permission_name IN ('edit_all_rncs', 'edit_own_rnc')
        ''', (user_id,))
        
        perms = cursor.fetchall()
        
        has_edit_all = any(p[0] == 'edit_all_rncs' and p[1] == 1 for p in perms)
        has_edit_own = any(p[0] == 'edit_own_rnc' and p[1] == 1 for p in perms)
        is_creator = user_id == rnc_creator_id
        
        print(f"   ✅ Pode editar todos RNCs: {has_edit_all}")
        print(f"   ✅ Pode editar próprios RNCs: {has_edit_own}")
        print(f"   ✅ É o criador do RNC: {is_creator}")
        
        can_edit = has_edit_all or (has_edit_own and is_creator)
        print(f"   🎯 RESULTADO: Pode editar este RNC? {can_edit}")
        
        # Teste adicional: verificar se usuário é admin
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        role = cursor.fetchone()
        is_admin = role and role[0] == 'admin'
        print(f"   👑 É admin: {is_admin}")
        
        final_can_edit = can_edit or is_admin
        print(f"   🏆 RESULTADO FINAL: {final_can_edit}")
    
    conn.close()

def test_edit_workflow():
    """Testar workflow completo de edição"""
    print("\n" + "=" * 50)
    print("🔧 TESTE DE WORKFLOW DE EDIÇÃO")
    print("=" * 50)
    
    # Simular dados que seriam enviados numa edição
    test_data = {
        'title': 'RNC Teste Editado',
        'description': 'Descrição editada pelo teste',
        'equipment': 'Equipamento Teste',
        'client': 'Cliente Teste',
        'priority': 'Alta',
        'status': 'Em Andamento'
    }
    
    print("📝 Dados de teste para edição:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    # Verificar se existe um RNC para testar
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, title FROM rncs WHERE is_deleted = 0 LIMIT 1')
    rnc = cursor.fetchone()
    
    if rnc:
        rnc_id = rnc[0]
        original_title = rnc[1]
        
        print(f"\n🎯 Testando edição do RNC {rnc_id}")
        print(f"   📄 Título original: {original_title}")
        
        # Simular atualização (sem commit para não alterar dados reais)
        try:
            cursor.execute('''
                UPDATE rncs 
                SET title = ?, description = ?, equipment = ?, client = ?, 
                    priority = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                test_data['title'],
                test_data['description'],
                test_data['equipment'], 
                test_data['client'],
                test_data['priority'],
                test_data['status'],
                rnc_id
            ))
            
            print("   ✅ Query de UPDATE executada com sucesso")
            print(f"   📝 Linhas afetadas: {cursor.rowcount}")
            
            # Verificar se os dados foram alterados (sem commit)
            cursor.execute('SELECT title, description, priority, status FROM rncs WHERE id = ?', (rnc_id,))
            updated = cursor.fetchone()
            
            if updated:
                print(f"   ✅ Novo título: {updated[0]}")
                print(f"   ✅ Nova descrição: {updated[1]}")
                print(f"   ✅ Nova prioridade: {updated[2]}")
                print(f"   ✅ Novo status: {updated[3]}")
            
            # Rollback para não salvar as alterações de teste
            conn.rollback()
            print("   🔄 Rollback executado (teste não alterou dados reais)")
            
        except Exception as e:
            print(f"   ❌ Erro na atualização: {e}")
            conn.rollback()
    else:
        print("   ⚠️ Nenhum RNC encontrado para teste")
    
    conn.close()

if __name__ == "__main__":
    debug_edit_permissions()
    test_edit_workflow()
