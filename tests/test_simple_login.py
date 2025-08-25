#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples de login
"""
import requests
import json

def test_simple_login():
    """Teste simples de login"""
    base_url = "http://192.168.3.11:5001"
    
    users = [
        ('admin@ippel.com.br', 'admin123'),
        ('ronaldo@ippel.com.br', 'teste123'),
        ('engenharia@1', 'teste123')
    ]
    
    for email, password in users:
        print(f"\n🔐 Testando login: {email}")
        
        try:
            session = requests.Session()
            response = session.post(f"{base_url}/api/login", json={
                'email': email,
                'password': password
            })
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Login bem-sucedido")
                
                # Testar informações do usuário
                user_info = session.get(f"{base_url}/api/user/info")
                if user_info.status_code == 200:
                    data = user_info.json()
                    if data['success']:
                        user = data['user']
                        print(f"   👤 Nome: {user['name']}")
                        print(f"   🏢 Grupo: {user.get('group', 'N/A')}")
                        print(f"   🔑 Permissões grupo: {len(user.get('groupPermissions', []))}")
                    else:
                        print(f"   ❌ Erro ao obter info: {data['message']}")
            else:
                print(f"   ❌ Falha no login")
                try:
                    error = response.json()
                    print(f"   📝 Erro: {error}")
                except:
                    print(f"   📝 Resposta: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    test_simple_login()
