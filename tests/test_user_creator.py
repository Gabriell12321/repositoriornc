#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from server_form import DB_PATH, get_rnc_data_safe

def test_user_creator():
    print("🧪 Testando sistema de exibição do criador da RNC...")
    
    # Teste 1: Verificar RNC existente
    print("\n1️⃣ Teste: Verificar dados da RNC 1")
    rnc_data, error = get_rnc_data_safe(1)
    
    if rnc_data:
        print(f"✅ RNC encontrada!")
        print(f"   📋 Número: {rnc_data[1]}")
        print(f"   📝 Título: {rnc_data[2]}")
        print(f"   👤 Criado por: {rnc_data[15]}")  # user_name
        print(f"   🎯 Atribuído para: {rnc_data[16]}")  # assigned_user_name
    else:
        print(f"❌ Erro: {error}")
    
    # Teste 2: Listar todas as RNCs
    print("\n2️⃣ Teste: Listar todas as RNCs")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.id, r.rnc_number, r.title, u.name as user_name, au.name as assigned_user_name
        FROM rncs r 
        LEFT JOIN users u ON r.user_id = u.id 
        LEFT JOIN users au ON r.assigned_user_id = au.id
        WHERE r.is_deleted = 0
        ORDER BY r.id
    ''')
    
    rncs = cursor.fetchall()
    conn.close()
    
    for rnc in rncs:
        print(f"   📋 RNC {rnc[1]}: '{rnc[2]}'")
        print(f"      👤 Criado por: {rnc[3] or 'Não definido'}")
        print(f"      🎯 Atribuído para: {rnc[4] or 'Não atribuído'}")
        print()

if __name__ == "__main__":
    test_user_creator() 