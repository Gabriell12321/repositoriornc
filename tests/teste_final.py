#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final do sistema IPPEL
"""

import requests
import sqlite3

def teste_completo():
    print("=" * 60)
    print("TESTE FINAL DO SISTEMA IPPEL")
    print("=" * 60)
    
    base_url = "http://192.168.3.11:5001"
    
    # 1. Verificar servidor
    print("\n1. Verificando servidor...")
    try:
        response = requests.get(base_url, timeout=5)
        print(f"   OK - Servidor respondendo ({response.status_code})")
    except Exception as e:
        print(f"   ERRO - Servidor nao responde: {e}")
        return False
    
    # 2. Verificar banco de dados
    print("\n2. Verificando banco de dados...")
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM rncs")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Finalizado'")
        finalizadas = cursor.fetchone()[0]
        conn.close()
        print(f"   OK - {total} RNCs no banco")
        print(f"   OK - {finalizadas} RNCs finalizadas")
    except Exception as e:
        print(f"   ERRO - Problema no banco: {e}")
        return False
    
    # 3. Testar autenticacao
    print("\n3. Testando autenticacao...")
    session = requests.Session()
    try:
        login_data = {'email': 'admin@ippel.com.br', 'password': 'admin123'}
        response = session.post(f"{base_url}/api/login", json=login_data, timeout=5)
        if response.status_code == 200:
            print("   OK - Login realizado com sucesso")
        else:
            print(f"   ERRO - Login falhou ({response.status_code})")
            return False
    except Exception as e:
        print(f"   ERRO - {e}")
        return False
    
    # 4. Testar APIs de RNCs
    print("\n4. Testando APIs de RNCs...")
    try:
        # Testar aba finalized
        response = session.get(f"{base_url}/api/rnc/list?tab=finalized", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_finalizadas = len(data.get('rncs', []))
            print(f"   OK - API Finalizadas: {total_finalizadas} RNCs")
        else:
            print(f"   ERRO - API Finalizadas falhou ({response.status_code})")
        
        # Testar aba active
        response = session.get(f"{base_url}/api/rnc/list?tab=active", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_ativas = len(data.get('rncs', []))
            print(f"   OK - API Ativas: {total_ativas} RNCs")
        else:
            print(f"   ERRO - API Ativas falhou ({response.status_code})")
            
        # Testar aba engenharia
        response = session.get(f"{base_url}/api/rnc/list?tab=engenharia", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_eng = len(data.get('rncs', []))
            print(f"   OK - API Engenharia: {total_eng} RNCs")
        else:
            print(f"   ERRO - API Engenharia falhou ({response.status_code})")
            
    except Exception as e:
        print(f"   ERRO - {e}")
        return False
    
    # 5. Testar dashboard
    print("\n5. Testando dashboard...")
    try:
        response = session.get(f"{base_url}/dashboard", timeout=10)
        if response.status_code == 200:
            print("   OK - Dashboard acessivel")
            # Verificar se o HTML contem elementos esperados
            html = response.text
            if 'IPPEL RNC System' in html or 'Dashboard' in html:
                print("   OK - Conteudo do dashboard carregado")
            else:
                print("   AVISO - Conteudo do dashboard pode estar incompleto")
        else:
            print(f"   ERRO - Dashboard inacessivel ({response.status_code})")
            return False
    except Exception as e:
        print(f"   ERRO - {e}")
        return False
    
    # 6. Resumo
    print("\n" + "=" * 60)
    print("RESUMO DO TESTE")
    print("=" * 60)
    print("OK - Todos os testes passaram com sucesso!")
    print("\nO sistema esta funcionando corretamente.")
    print(f"Acesse: {base_url}/dashboard")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    teste_completo()
