#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar senhas para usuários de teste
"""
import sqlite3
from werkzeug.security import generate_password_hash

def create_test_passwords():
    """Criar senhas para usuários de teste"""
    print("🔐 Criando senhas para usuários de teste...")
    
    # Usuários para definir senhas
    test_users = [
        ('ronaldo@ippel.com.br', 'teste123'),
        ('engenharia@1', 'teste123'),
        ('elvio@1', 'teste123'),
        ('claudio.brandao@ippel.com.br', 'teste123'),
        ('luiz.guilherme.souza@ippel.com.br', 'teste123')
    ]
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    try:
        for email, password in test_users:
            # Verificar se o usuário existe
            cursor.execute("SELECT id, name FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if user:
                user_id, name = user
                
                # Hash da senha usando Werkzeug
                hashed_password = generate_password_hash(password)
                
                # Atualizar senha
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (hashed_password, user_id)
                )
                
                print(f"✅ Senha definida para {name} ({email})")
            else:
                print(f"⚠️ Usuário não encontrado: {email}")
        
        conn.commit()
        print(f"\n✅ Senhas criadas com sucesso!")
        print("\n📋 Credenciais de teste:")
        print("   👤 admin@ippel.com.br / admin123")
        for email, password in test_users:
            cursor.execute("SELECT name FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if user:
                print(f"   👤 {email} / {password}")
    
    except Exception as e:
        print(f"❌ Erro ao criar senhas: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_passwords()
