#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar índices da tabela RNCs
"""
import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

print("📋 Estrutura da tabela RNCs:")
cursor.execute("PRAGMA table_info(rncs)")
columns = cursor.fetchall()

user_id_index = None
for i, col in enumerate(columns):
    col_name = col[1]
    print(f"   [{i}] {col_name}")
    if col_name == 'user_id':
        user_id_index = i   

print(f"\n👤 user_id está no índice: {user_id_index}")

conn.close()
