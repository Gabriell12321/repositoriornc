#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import hashlib
import sys
import os

# Adicionar o caminho do servidor ao sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_users():
    """Criar usuários de teste para cada departamento"""
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Usuários de teste para cada departamento
    test_users = [
        {
            'name': 'Teste Engenharia',
            'email': 'engenharia@teste.com',
            'password': 'teste123',
            'department': 'Engenharia',
            'role': 'user'
        },
        {
            'name': 'Teste Producao',
            'email': 'producao@teste.com', 
            'password': 'teste123',
            'department': 'Produção',
            'role': 'user'
        },
        {
            'name': 'Teste Qualidade',
            'email': 'qualidade@teste.com',
            'password': 'teste123', 
            'department': 'Qualidade',
            'role': 'user'
        },
        {
            'name': 'Teste Administracao',
            'email': 'admin@teste.com',
            'password': 'teste123',
            'department': 'Administração', 
            'role': 'user'
        },
        {
            'name': 'Teste TI',
            'email': 'ti@teste.com',
            'password': 'teste123',
            'department': 'TI',
            'role': 'user'
        }
    ]
    
    print("👥 CRIANDO USUÁRIOS DE TESTE")
    print("=" * 50)
    
    for user in test_users:
        # Verificar se usuário já existe
        cursor.execute('SELECT id FROM users WHERE email = ?', (user['email'],))
        if cursor.fetchone():
            print(f"⚠️  {user['email']} já existe")
            continue
        
        # Hash da senha
        password_hash = hashlib.sha256(user['password'].encode()).hexdigest()
        
        # Inserir usuário
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, department, role, is_active, permissions)
            VALUES (?, ?, ?, ?, ?, 1, 'create_rnc,view_rnc,edit_rnc')
        ''', (user['name'], user['email'], password_hash, user['department'], user['role']))
        
        print(f"✅ Criado: {user['name']} ({user['department']}) - {user['email']}")
    
    conn.commit()
    conn.close()
    
    print("\n📋 DADOS DE LOGIN:")
    print("Senha para todos: teste123")
    print("\nEmails:")
    for user in test_users:
        print(f"• {user['department']}: {user['email']}")

if __name__ == '__main__':
    create_test_users()
