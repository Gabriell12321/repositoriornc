#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("=== TESTE DO SISTEMA DE FILTROS RNC/GARANTIA ===")

try:
    from scripts.extract_indicators_by_type import extract_indicators_by_type
    print("✅ Importação bem-sucedida")
    
    print("\n1. Testando filtro RNC...")
    result_rnc = extract_indicators_by_type('rnc')
    print(f"   Tipo do resultado: {type(result_rnc)}")
    if isinstance(result_rnc, dict):
        print(f"   Chaves disponíveis: {list(result_rnc.keys())}")
    
    print("\n2. Testando filtro Garantia...")
    result_garantia = extract_indicators_by_type('garantia')
    print(f"   Tipo do resultado: {type(result_garantia)}")
    if isinstance(result_garantia, dict):
        print(f"   Chaves disponíveis: {list(result_garantia.keys())}")
    
    print("\n✅ Teste concluído com sucesso!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
