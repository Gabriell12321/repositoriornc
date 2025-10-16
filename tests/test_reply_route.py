#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a rota de resposta de RNC
"""

import requests
import sqlite3

def test_reply_route():
    """Testa a rota de resposta de RNC"""
    
    try:
        # Conectar ao banco para verificar RNCs disponíveis
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Buscar uma RNC para testar
        cursor.execute('SELECT id, rnc_number, title, status FROM rncs WHERE is_deleted = 0 LIMIT 1')
        rnc = cursor.fetchone()
        
        if not rnc:
            print("❌ Nenhuma RNC encontrada no banco")
            return
        
        rnc_id, rnc_number, title, status = rnc
        print(f"✅ RNC encontrada: ID={rnc_id}, Número={rnc_number}, Status={status}")
        
        conn.close()
        
        # Fazer login primeiro
        print("\n🔐 Fazendo login...")
        login_data = {
            'email': 'teste@1',
            'password': '123456'
        }
        
        session = requests.Session()
        login_response = session.post('http://localhost:5001/api/login', json=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login realizado com sucesso")
            
            # Testar a rota de resposta
            print(f"\n🔍 Testando rota de resposta: /rnc/{rnc_id}/reply")
            reply_url = f'http://localhost:5001/rnc/{rnc_id}/reply'
            
            reply_response = session.get(reply_url)
            
            print(f"Status Code: {reply_response.status_code}")
            print(f"Content-Type: {reply_response.headers.get('content-type', 'N/A')}")
            
            if reply_response.status_code == 200:
                print("✅ Rota de resposta funcionando!")
                if 'edit_rnc_form.html' in reply_response.text:
                    print("✅ Template edit_rnc_form.html carregado")
                else:
                    print("❌ Template edit_rnc_form.html NÃO encontrado na resposta")
            else:
                print(f"❌ Erro na rota de resposta: {reply_response.status_code}")
                print(f"Resposta: {reply_response.text[:500]}...")
                
        else:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"Resposta: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_reply_route()
