#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug da query de RNCs
"""

import sqlite3
import requests
import json

def debug_rnc_query():
    print("Debugando query de RNCs...")
    
    # Teste direto no banco
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Query simples para ver todas as RNCs
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE (is_deleted = 0 OR is_deleted IS NULL)")
        count = cursor.fetchone()[0]
        print(f"RNCs sem filtro: {count}")
        
        # Query com filtro de status
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE (is_deleted = 0 OR is_deleted IS NULL) AND status NOT IN ('Finalizado')")
        active_count = cursor.fetchone()[0]
        print(f"RNCs ativas: {active_count}")
        
        # Query com filtro de finalizadas
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE (is_deleted = 0 OR is_deleted IS NULL) AND status = 'Finalizado'")
        finalized_count = cursor.fetchone()[0]
        print(f"RNCs finalizadas: {finalized_count}")
        
        # Verificar se há campo is_deleted
        cursor.execute("PRAGMA table_info(rncs)")
        columns = cursor.fetchall()
        has_is_deleted = any(col[1] == 'is_deleted' for col in columns)
        print(f"Campo is_deleted existe: {has_is_deleted}")
        
        if has_is_deleted:
            cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 1")
            deleted_count = cursor.fetchone()[0]
            print(f"RNCs deletadas: {deleted_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro no banco: {e}")
    
    # Teste da API com diferentes parâmetros
    base_url = "http://192.168.3.11:5001"
    session = requests.Session()
    
    try:
        # Login
        login_data = {'email': 'admin@ippel.com.br', 'password': 'admin123'}
        response = session.post(f"{base_url}/api/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            print("Login realizado")
            
            # Testar diferentes abas
            tabs = ['active', 'finalized', 'engenharia']
            
            for tab in tabs:
                print(f"\nTestando aba: {tab}")
                rnc_response = session.get(f"{base_url}/api/rnc/list?tab={tab}", timeout=10)
                print(f"Status: {rnc_response.status_code}")
                
                if rnc_response.status_code == 200:
                    data = rnc_response.json()
                    print(f"Sucesso: {data.get('success', False)}")
                    print(f"Total RNCs: {len(data.get('rncs', []))}")
                else:
                    print(f"Erro: {rnc_response.text}")
                    
    except Exception as e:
        print(f"Erro na API: {e}")

if __name__ == "__main__":
    debug_rnc_query()
