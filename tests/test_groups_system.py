#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from server_form import DB_PATH, create_user, get_all_groups, get_users_by_group

def test_group_system():
    print("🧪 Testando sistema de grupos...")
    
    # Teste 1: Criar usuário com grupo existente
    print("\n1️⃣ Teste: Criar usuário com grupo 'Engenharia' (existente)")
    result = create_user(
        name="João Silva",
        email="joao.silva@teste.com",
        password="123456",
        department="Engenharia",
        role="user",
        permissions=["create_rnc"]
    )
    print(f"✅ Resultado: {result}")
    
    # Teste 2: Criar usuário com grupo novo
    print("\n2️⃣ Teste: Criar usuário com grupo 'Marketing' (novo)")
    result = create_user(
        name="Maria Santos",
        email="maria.santos@teste.com",
        password="123456",
        department="Marketing",
        role="user",
        permissions=["create_rnc"]
    )
    print(f"✅ Resultado: {result}")
    
    # Teste 3: Listar todos os grupos
    print("\n3️⃣ Teste: Listar todos os grupos")
    groups = get_all_groups()
    for group in groups:
        print(f"   📋 {group[1]} - {group[3]} usuários")
    
    # Teste 4: Verificar usuários por grupo
    print("\n4️⃣ Teste: Verificar usuários por grupo")
    for group in groups:
        users = get_users_by_group(group[0])
        print(f"   👥 {group[1]}: {len(users)} usuários")
        for user in users:
            print(f"      - {user[1]} ({user[2]})")

if __name__ == "__main__":
    test_group_system() 