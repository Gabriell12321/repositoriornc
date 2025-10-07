#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Contar total
cursor.execute('SELECT COUNT(*) FROM sectors')
total = cursor.fetchone()[0]
print(f"📊 Total de setores cadastrados: {total}")

# Listar todos ordenados
print("\n📝 Lista completa de setores:")
print("-" * 50)
cursor.execute('SELECT id, name FROM sectors ORDER BY name')
for row in cursor.fetchall():
    print(f"  {row[0]:2d}. {row[1]}")

conn.close()
