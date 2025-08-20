#!/usr/bin/env python3
import sqlite3
import os

def test_create_rnc_with_department():
    """Simular criação de RNC com departamento"""
    print("=== TESTE DE CRIAÇÃO RNC COM DEPARTAMENTO ===\n")
    
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # 1. Verificar usuário admin
        print("1. 🔍 Verificando usuário admin...")
        cursor.execute("SELECT id, name, department FROM users WHERE name = 'Administrador' OR name LIKE '%admin%' LIMIT 1")
        admin_user = cursor.fetchone()
        if admin_user:
            admin_id, admin_name, admin_dept = admin_user
            print(f"   ✅ Admin encontrado: ID {admin_id}, Nome: {admin_name}, Depto: {admin_dept}")
        else:
            print("   ❌ Usuário admin não encontrado")
            return
        
        # 2. Verificar grupos disponíveis
        print("\n2. 📋 Verificando grupos disponíveis...")
        cursor.execute("SELECT id, name FROM groups ORDER BY name")
        groups = cursor.fetchall()
        print("   Grupos encontrados:")
        for group_id, group_name in groups:
            print(f"     - ID {group_id}: {group_name}")
        
        # 3. Criar RNC teste para grupo Engenharia
        print("\n3. 📝 Criando RNC teste para Engenharia...")
        
        # Gerar número do RNC
        cursor.execute("SELECT MAX(CAST(SUBSTR(rnc_number, 5) AS INTEGER)) FROM rncs WHERE rnc_number LIKE 'RNC%'")
        last_number = cursor.fetchone()[0] or 0
        new_number = f"RNC{last_number + 1:05d}"
        
        # Inserir RNC com departamento "Engenharia"
        cursor.execute("""
            INSERT INTO rncs 
            (rnc_number, title, description, equipment, client, priority, status, price, user_id, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_number,
            "Teste RNC Admin para Engenharia",
            "RNC criada pelo admin para testar sistema de grupos",
            "Equipamento Teste",
            "Cliente Teste",
            "Alta",
            "Pendente",
            100.50,
            admin_id,
            "Engenharia"  # Departamento do grupo
        ))
        
        rnc_id = cursor.lastrowid
        print(f"   ✅ RNC criado: {new_number} (ID: {rnc_id})")
        
        # 4. Verificar se RNC foi criado corretamente
        print("\n4. 🔍 Verificando RNC criado...")
        cursor.execute("SELECT id, rnc_number, title, department, user_id FROM rncs WHERE id = ?", (rnc_id,))
        rnc_data = cursor.fetchone()
        if rnc_data:
            rnc_id, rnc_num, title, dept, user_id = rnc_data
            print(f"   ✅ RNC {rnc_num}: {title[:30]}... -> Depto: '{dept}' (User: {user_id})")
        
        # 5. Verificar quais usuários do grupo Engenharia deveriam ver esta RNC
        print("\n5. 👥 Usuários do grupo Engenharia que deveriam ver a RNC:")
        cursor.execute("SELECT id, name, department FROM users WHERE department = 'Engenharia'")
        eng_users = cursor.fetchall()
        for user_id, name, dept in eng_users:
            print(f"   - ID {user_id}: {name} ({dept})")
        
        # 6. Testar consulta de RNCs para usuário de engenharia
        print("\n6. 🔍 Testando consulta para usuário de engenharia...")
        if eng_users:
            test_user_id = eng_users[0][0]  # Pegar primeiro usuário
            test_user_name = eng_users[0][1]
            
            cursor.execute("""
                SELECT id, rnc_number, title, department 
                FROM rncs 
                WHERE is_deleted = 0 
                AND (user_id = ? OR department = 'Engenharia')
                ORDER BY id DESC 
                LIMIT 5
            """, (test_user_id,))
            
            rncs_for_user = cursor.fetchall()
            print(f"   ✅ RNCs visíveis para {test_user_name}:")
            for rnc_id, rnc_num, title, dept in rncs_for_user:
                print(f"     - {rnc_num}: {title[:40]}... (Depto: {dept})")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Teste concluído! RNC {new_number} criado para grupo Engenharia")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_create_rnc_with_department()
