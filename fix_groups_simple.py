#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para corrigir nomes dos grupos no banco de dados
"""

import sqlite3

DB_PATH = 'ippel_system.db'

# Correções específicas por ID
FIXES = {
    22: 'Usinagem Cilíndrica CNC',
    23: 'Usinagem Cilíndrica Convencional',
    24: 'Não Definidos',
    25: 'Produção'
}

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Antes:")
    cursor.execute("SELECT id, name FROM groups WHERE id IN (22, 23, 24, 25) ORDER BY id")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    print("\nAplicando correções...")
    for group_id, correct_name in FIXES.items():
        cursor.execute("UPDATE groups SET name = ? WHERE id = ?", (correct_name, group_id))
        print(f"  ✓ ID {group_id}: {correct_name}")
    
    conn.commit()
    
    print("\nDepois:")
    cursor.execute("SELECT id, name FROM groups WHERE id IN (22, 23, 24, 25) ORDER BY id")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    print("\n✅ Correções aplicadas com sucesso!")
    conn.close()

if __name__ == '__main__':
    main()
