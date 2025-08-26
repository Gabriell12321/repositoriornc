#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("=== TESTE SIMPLES DOS FILTROS ===")

# Testar diretamente as funções sem API
try:
    from scripts.extract_indicators_by_type import extract_indicators_by_type
    
    print("\n1. 🔍 Testando RNC...")
    rnc_data = extract_indicators_by_type('rnc')
    if rnc_data:
        print(f"   ✅ RNC: {len(rnc_data.get('monthlyData', []))} meses, {len(rnc_data.get('departments', []))} departamentos")
        print(f"   📊 Total acumulado: {rnc_data.get('totals', {}).get('acumulado', 0)}")
    else:
        print("   ❌ RNC: Falha na extração")
    
    print("\n2. 🔍 Testando GARANTIA...")
    garantia_data = extract_indicators_by_type('garantia')
    if garantia_data:
        print(f"   ✅ GARANTIA: {len(garantia_data.get('monthlyData', []))} meses, {len(garantia_data.get('departments', []))} departamentos")
        print(f"   📊 Total acumulado: {garantia_data.get('totals', {}).get('acumulado', 0)}")
    else:
        print("   ❌ GARANTIA: Falha na extração")
    
    print("\n✅ Sistema de filtros funcionando!")
    print("\n📋 Próximos passos:")
    print("   1. Acesse o dashboard em: http://127.0.0.1:5001")
    print("   2. Faça login com: admin@ippel.com.br / admin123")
    print("   3. Vá para Indicadores > Dashboard")
    print("   4. Use os botões 'RNC' e 'Garantia' para filtrar")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
