#!/usr/bin/env python3
"""Verificar setores no banco."""

import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Setores não vazios
cursor.execute("SELECT rnc_number, setor FROM rncs WHERE setor IS NOT NULL AND setor != '' LIMIT 10")
results = cursor.fetchall()

print("SETORES NÃO VAZIOS:")
for r in results:
    print(f'{r[0]}: "{r[1]}"')

print("\n" + "="*40)

# Contar setores vazios vs preenchidos
cursor.execute("SELECT COUNT(*) FROM rncs WHERE setor IS NULL OR setor = ''")
empty_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM rncs WHERE setor IS NOT NULL AND setor != ''")
filled_count = cursor.fetchone()[0]

print(f"Setores vazios: {empty_count}")
print(f"Setores preenchidos: {filled_count}")

conn.close()