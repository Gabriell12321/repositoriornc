#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("=== TESTE DA FORMATAÇÃO MONETÁRIA ===")

try:
    from scripts.extract_indicators_by_type import extract_indicators_by_type, format_currency, format_number
    
    # Testar funções de formatação
    print("\n🔍 Testando formatação:")
    test_values = [1234.56, 12345.67, 123456.78, 1234567.89, 0, 100]
    
    for value in test_values:
        formatted = format_currency(value)
        print(f"   {value:>10} → {formatted}")
    
    print("\n🔍 Testando extração de GARANTIA com formatação:")
    garantia_data = extract_indicators_by_type('garantia')
    
    if garantia_data and 'monthlyData' in garantia_data:
        print(f"   ✅ Dados mensais formatados:")
        for i, month_data in enumerate(garantia_data['monthlyData'][:3]):  # Primeiros 3 meses
            print(f"      {month_data['month']}: Meta={month_data['meta']}, Realizado={month_data['realizado']}")
        
        if 'departments' in garantia_data and garantia_data['departments']:
            print(f"   ✅ Dados departamentais formatados:")
            for dept in garantia_data['departments'][:2]:  # Primeiros 2 departamentos
                print(f"      {dept['name']}: Meta={dept['meta']}, Realizado={dept['realizado']}, Efficiency={dept['efficiency']}")
        
        if 'totals' in garantia_data:
            print(f"   ✅ Totais formatados:")
            totals = garantia_data['totals']
            print(f"      Acumulado: {totals.get('acumulado', 'N/A')}")
            print(f"      Meta Média: {totals.get('meta', 'N/A')}")
    
    print("\n✅ Teste da formatação concluído!")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
