#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# Adicionar o diretório scripts ao path
script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
if script_path not in sys.path:
    sys.path.append(script_path)

from extract_indicators_by_type import format_currency

print("=== TESTE DA FORMATAÇÃO ===")

# Testar valores baseados nos dados anexados
test_values = [32070.25, 32482.62, 29266.67, 15708.17, 23394.53]

for value in test_values:
    formatted = format_currency(value)
    print(f"{value:>10.2f} → {formatted}")

print("\nExemplo de formatação aplicada aos dados:")
print("01/19: $ 32.070,25")
print("02/19: $ 32.482,62") 
print("03/19: $ 29.266,67")
