#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Importa operadores a partir de um arquivo TSV (tab separado) com cabeçalho
"OPERADOR\tNÚMERO" e insere na tabela 'operators' do SQLite.

Uso:
  python import_operators_from_tsv.py --file operators.tsv --db ippel_system.db
"""

import argparse
import csv
import os
import sqlite3
from typing import Optional


def ensure_operators_table(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS operators (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT UNIQUE NOT NULL,
               number TEXT,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )'''
    )
    try:
        cur.execute('ALTER TABLE operators ADD COLUMN number TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_operators_number ON operators(number) WHERE number IS NOT NULL')
    except sqlite3.OperationalError:
        pass
    conn.commit(); conn.close()


def normalize_number(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    if s == '' or s == '-':
        return None
    return s


def insert_operator(conn: sqlite3.Connection, name: str, number: Optional[str]) -> bool:
    cur = conn.cursor()
    try:
        cur.execute('INSERT OR IGNORE INTO operators (name, number) VALUES (?, ?)', (name, number))
        if cur.rowcount == 0 and number is not None:
            # Se já existe com nome, atualiza o número quando vazio
            cur.execute('UPDATE operators SET number = COALESCE(number, ?) WHERE name = ? AND (number IS NULL OR number = "")', (number, name))
        return True
    except sqlite3.IntegrityError:
        return False


def import_tsv(tsv_path: str, db_path: str) -> tuple[int, int]:
    if not os.path.exists(tsv_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {tsv_path}")
    ensure_operators_table(db_path)
    conn = sqlite3.connect(db_path)
    inserted, updated = 0, 0
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        # normalizar headers
        field_map = {k.lower().strip(): k for k in reader.fieldnames or []}
        col_name = field_map.get('operador') or field_map.get('nome') or list(field_map.values())[0]
        col_number = field_map.get('número') or field_map.get('numero')
        for row in reader:
            name = (row.get(col_name) or '').strip()
            if not name:
                continue
            number = normalize_number(row.get(col_number)) if col_number else None
            before = conn.execute('SELECT number FROM operators WHERE name = ?', (name,)).fetchone()
            ok = insert_operator(conn, name, number)
            after = conn.execute('SELECT number FROM operators WHERE name = ?', (name,)).fetchone()
            if ok:
                if before is None:
                    inserted += 1
                elif before and before[0] in (None, '') and after and after[0]:
                    updated += 1
    conn.commit(); conn.close()
    return inserted, updated


def main() -> None:
    parser = argparse.ArgumentParser(description='Importar operadores (TSV) para SQLite.')
    parser.add_argument('--file', required=True, help='Caminho do TSV (OPERADOR\tNÚMERO)')
    parser.add_argument('--db', default='ippel_system.db', help='Caminho do SQLite')
    args = parser.parse_args()

    ins, upd = import_tsv(args.file, args.db)
    print(f"Operadores inseridos: {ins} | números atualizados: {upd}")


if __name__ == '__main__':
    main()


