#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Importa setores embutidos para a tabela `sectors` no SQLite.
Uso:
  python import_sectors_embedded.py --db ippel_system.db
"""

import argparse
import sqlite3

SECTORS = [
    'engenharia',
    'Cliente',
    'Montagem',
    'Corte',
    'Conformação',
    'Caldeiraria de Carbono',
    'Caldeiraria de Inox',
    'Jato de Granalha',
    'Pintura',
    'Usin. Cilíndrica Convencional',
    'Usin. Cilíndrica CNC',
    'Usinagem Plana',
    'Furação',
    'Célula de Secadores',
    'Balanceamento',
    'Embalagem',
]

def ensure_table(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS sectors (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT UNIQUE NOT NULL,
               description TEXT DEFAULT '',
               color TEXT DEFAULT '#5b21b6',
               is_active BOOLEAN DEFAULT 1,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )'''
    )
    conn.commit(); conn.close()

def import_sectors(db_path: str) -> tuple[int, int]:
    ensure_table(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    inserted = 0
    skipped = 0
    for name in SECTORS:
        try:
            cur.execute('INSERT OR IGNORE INTO sectors (name) VALUES (?)', (name.strip(),))
            inserted += 1 if cur.rowcount == 1 else 0
            skipped += 0 if cur.rowcount == 1 else 1
        except Exception:
            skipped += 1
    conn.commit(); conn.close()
    return inserted, skipped

def main():
    ap = argparse.ArgumentParser(description='Importar setores embutidos para SQLite')
    ap.add_argument('--db', default='ippel_system.db', help='Caminho do SQLite (padrão: ippel_system.db)')
    args = ap.parse_args()
    ins, skip = import_sectors(args.db)
    print(f'Setores inseridos: {ins} | existentes/ignorados: {skip}')

if __name__ == '__main__':
    main()


