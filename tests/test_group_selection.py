#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from server_form import DB_PATH, get_all_groups, get_users_by_group

def test_group_selection():
    print("🧪 Testando sistema de seleção de grupos para RNCs...")
    
    # Teste 1: Verificar grupos disponíveis
    print("\n1️⃣ Teste: Verificar grupos disponíveis")
    groups = get_all_groups()
    
    if groups:
        print(f"✅ Encontrados {len(groups)} grupos:")
        for group in groups:
            print(f"   📋 {group[1]} - {group[3]} usuários")
            print(f"      📝 Descrição: {group[2] or 'Sem descrição'}")
    else:
        print("❌ Nenhum grupo encontrado")
    
    # Teste 2: Verificar usuários por grupo
    print("\n2️⃣ Teste: Verificar usuários por grupo")
    for group in groups:
        users = get_users_by_group(group[0])
        print(f"   👥 {group[1]}: {len(users)} usuários")
        for user in users:
            print(f"      - {user[1]} ({user[2]})")
    
    # Teste 3: Simular criação de RNC com grupos
    print("\n3️⃣ Teste: Simular criação de RNC com grupos")
    if groups:
        selected_groups = [groups[0][0], groups[1][0]] if len(groups) >= 2 else [groups[0][0]]
        print(f"   🎯 Grupos selecionados: {[groups[i][1] for i in range(len(selected_groups))]}")
        
        # Calcular total de usuários que receberão a RNC
        total_users = 0
        for group_id in selected_groups:
            users = get_users_by_group(group_id)
            total_users += len(users)
            print(f"      📋 {groups[group_id-1][1]}: {len(users)} usuários")
        
        print(f"   👥 Total de usuários que receberão a RNC: {total_users}")
    else:
        print("   ❌ Nenhum grupo disponível para teste")

if __name__ == "__main__":
    test_group_selection() 