#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se a API de RNCs está funcionando
"""

import requests
import json
import sys

def test_api_connection():
    """Testa a conexão com a API"""
    base_url = "http://192.168.3.11:5001"
    
    print("Testando conexao com a API...")
    
    try:
        # Teste de conexão básica
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"OK Conexao basica: {response.status_code}")
    except Exception as e:
        print(f"ERRO de conexao: {e}")
        return False
    
    try:
        # Teste da API de status
        response = requests.get(f"{base_url}/api/status", timeout=5)
        print(f"✅ API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Dados: {data}")
    except Exception as e:
        print(f"⚠️ API Status não disponível: {e}")
    
    try:
        # Teste da API de RNCs (sem autenticação - deve retornar 401)
        response = requests.get(f"{base_url}/api/rnc/list", timeout=5)
        print(f"🔒 API RNC List (sem auth): {response.status_code}")
        if response.status_code == 401:
            print("✅ Autenticação funcionando corretamente")
        else:
            print(f"⚠️ Resposta inesperada: {response.text}")
    except Exception as e:
        print(f"❌ Erro na API RNC: {e}")
    
    return True

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print("\n🗄️ Testando conexão com o banco de dados...")
    
    try:
        import sqlite3
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar se a tabela rncs existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rncs'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ Tabela 'rncs' existe")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM rncs")
            count = cursor.fetchone()[0]
            print(f"📊 Total de RNCs: {count}")
            
            # Verificar estrutura da tabela
            cursor.execute("PRAGMA table_info(rncs)")
            columns = cursor.fetchall()
            print(f"📋 Colunas da tabela: {len(columns)}")
            for col in columns[:5]:  # Mostrar apenas as primeiras 5
                print(f"   - {col[1]} ({col[2]})")
                
        else:
            print("❌ Tabela 'rncs' não encontrada")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        return False

def test_user_authentication():
    """Testa a autenticação de usuário"""
    print("\n👤 Testando autenticação...")
    
    base_url = "http://192.168.3.11:5001"
    
    try:
        # Dados de login
        login_data = {
            'email': 'admin@ippel.com.br',
            'password': 'admin123'
        }
        
        # Fazer login
        session = requests.Session()
        response = session.post(f"{base_url}/api/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            print("✅ Login realizado com sucesso")
            
            # Testar API de RNCs com autenticação
            rnc_response = session.get(f"{base_url}/api/rnc/list", timeout=5)
            print(f"📋 API RNC List (com auth): {rnc_response.status_code}")
            
            if rnc_response.status_code == 200:
                data = rnc_response.json()
                print(f"📊 Dados recebidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True
            else:
                print(f"❌ Erro na API RNC: {rnc_response.text}")
                return False
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes do sistema IPPEL...")
    print("=" * 50)
    
    # Teste 1: Conexão com API
    api_ok = test_api_connection()
    
    # Teste 2: Banco de dados
    db_ok = test_database_connection()
    
    # Teste 3: Autenticação
    auth_ok = test_user_authentication()
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES:")
    print(f"🔗 API Connection: {'✅' if api_ok else '❌'}")
    print(f"🗄️ Database: {'✅' if db_ok else '❌'}")
    print(f"👤 Authentication: {'✅' if auth_ok else '❌'}")
    
    if api_ok and db_ok and auth_ok:
        print("\n🎉 Todos os testes passaram! O sistema está funcionando.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")
        sys.exit(1)
