#!/usr/bin/env python3
"""
Verificar se o servidor Flask está rodando
"""

import requests
import sys

def check_server():
    try:
        response = requests.get('http://localhost:5000', timeout=2)
        print(f'✅ Servidor Flask está rodando!')
        print(f'   Status: {response.status_code}')
        return True
    except requests.exceptions.ConnectionError:
        print(f'❌ Servidor Flask NÃO está rodando')
        print(f'   💡 Execute: python server.py')
        return False
    except Exception as e:
        print(f'❓ Erro ao verificar servidor: {e}')
        return False

if __name__ == "__main__":
    check_server()
