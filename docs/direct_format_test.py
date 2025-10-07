#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testar a formatação diretamente
def format_currency_test(value):
    """Teste da formatação monetária"""
    try:
        if value == 0:
            return "$ 0,00"
        
        # Formatar com separador de milhares (ponto) e decimais (vírgula)
        formatted = f"{value:,.2f}"
        # Trocar ponto por vírgula para decimais e vírgula por ponto para milhares (padrão brasileiro)
        parts = formatted.split('.')
        if len(parts) == 2:
            # Separar parte inteira e decimal
            integer_part = parts[0].replace(',', '.')  # Vírgulas viram pontos (separador de milhares)
            decimal_part = parts[1]
            formatted = f"{integer_part},{decimal_part}"  # Vírgula para decimais
        
        return f"$ {formatted}"
    except:
        return "$ 0,00"

print("=== TESTE DA FORMATAÇÃO MONETÁRIA ===")

# Valores dos dados anexados
test_values = [32070.25, 32482.62, 29266.67, 15708.17, 23394.53, 53466.2, 53888.16, 71222.07]

print("Formatação dos valores:")
for value in test_values:
    formatted = format_currency_test(value)
    print(f"  {value:>10.2f} → {formatted}")

print("\nComparação com dados originais:")
original_data = [
    ("01/19", 32070.25),
    ("02/19", 32482.62),
    ("03/19", 29266.67),
    ("04/19", 15708.17),
    ("05/19", 23394.53),
    ("06/19", 53466.2),
    ("07/19", 53888.16),
    ("08/19", 71222.07)
]

for date, value in original_data:
    formatted = format_currency_test(value)
    print(f"  {date}: {formatted}")

print("\n✅ Formatação aplicada com sucesso!")
