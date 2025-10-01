#!/usr/bin/env python3
"""
Script para testar a exclusão permanente de RNCs
"""

import requests
import json

def test_delete_is_definitive():
    """Testar que a exclusão agora é definitiva (sem lixeira)."""

    base_url = "http://192.168.2.114:5001"

    login_data = {
        "email": "admin@ippel.com.br",
        "password": "admin123"
    }

    try:
        print("🔐 Fazendo login...")
        login_response = requests.post(f"{base_url}/api/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(login_response.text)
            return

        cookies = login_response.cookies

        # Escolher um RNC ativo para excluir: pegar o primeiro da aba active
        list_response = requests.get(f"{base_url}/api/rnc/list?tab=active", cookies=cookies)
        if list_response.status_code != 200:
            print(f"❌ Erro ao listar ativos: {list_response.status_code}")
            return

        rncs = list_response.json().get('rncs', [])
        if not rncs:
            print("ℹ️ Nenhum RNC ativo encontrado para exclusão de teste")
            return

        rnc_id = rncs[0]['id']
        print(f"🗑️ Excluindo definitivamente RNC {rnc_id}...")
        delete_response = requests.delete(f"{base_url}/api/rnc/{rnc_id}/delete", cookies=cookies)
        print("📊 Status Code:", delete_response.status_code)
        print("📝 Response:", delete_response.text)

        # Verificar se não aparece mais em active ou finalized
        verify_active = requests.get(f"{base_url}/api/rnc/list?tab=active", cookies=cookies)
        verify_finalized = requests.get(f"{base_url}/api/rnc/list?tab=finalized", cookies=cookies)

        ids_active = {r['id'] for r in verify_active.json().get('rncs', [])}
        ids_finalized = {r['id'] for r in verify_finalized.json().get('rncs', [])}
        if rnc_id in ids_active or rnc_id in ids_finalized:
            print("❌ RNC ainda aparece após exclusão")
        else:
            print("✅ Exclusão definitiva confirmada")

    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão: Servidor não está rodando ou não acessível")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_delete_is_definitive() 