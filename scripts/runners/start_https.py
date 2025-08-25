#!/usr/bin/env python
"""Script simples para iniciar o servidor com HTTPS"""
import os
import sys

# Configurar HTTPS
os.environ['IPPEL_ENABLE_HTTPS'] = '1'

# Importar e executar o server_form
try:
    # Adicionar o diretório atual ao path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Importar o módulo server_form
    import server_form
    
    print("\n🔒 Iniciando servidor com HTTPS...")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ Erro ao iniciar servidor: {e}")
    import traceback
    traceback.print_exc()
    input("\nPressione ENTER para sair...")
