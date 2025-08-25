#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Importar clientes a partir de um arquivo .txt (1 cliente por linha) para a tabela 'clients'.

Uso:
  python import_clients_from_txt.py --file "CAMINHO/para/clientescadastro.txt" --db ippel_system.db
"""

import argparse
import os
import sqlite3


def ensure_clients_table(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS clients (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT UNIQUE NOT NULL,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )'''
    )
    conn.commit()
    conn.close()


def load_clients_from_txt(file_path: str) -> list[str]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    # Tentar utf-8; se falhar, fallback para cp1252 (Windows-1252)
    encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']
    last_err = None
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                lines = [l.strip() for l in f.readlines()]
                break
        except Exception as e:  # pragma: no cover
            last_err = e
            lines = None
    if lines is None:
        raise RuntimeError(f"Falha ao ler arquivo em {encodings}: {last_err}")
    # Limpar e deduplicar mantendo ordem
    seen = set()
    clients: list[str] = []
    for line in lines:
        if not line:
            continue
        name = line.strip()
        # Ignorar cabeçalho comum
        if name.lower() == 'cliente':
            continue
        if name and name.lower() not in seen:
            seen.add(name.lower())
            clients.append(name)
    return clients


def insert_clients(db_path: str, names: list[str]) -> tuple[int, int]:
    ensure_clients_table(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    inserted = 0
    skipped = 0
    for name in names:
        try:
            cur.execute('INSERT INTO clients (name) VALUES (?)', (name,))
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1
    conn.commit()
    conn.close()
    return inserted, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description='Importar clientes do arquivo .txt para a tabela clients (SQLite).')
    parser.add_argument('--file', required=True, help='Caminho para clientescadastro.txt')
    parser.add_argument('--db', default='ippel_system.db', help='Caminho do banco SQLite (padrão: ippel_system.db)')
    args = parser.parse_args()

    names = load_clients_from_txt(args.file)
    ins, skip = insert_clients(args.db, names)
    print(f"Clientes processados: {len(names)} | Inseridos: {ins} | Já existiam: {skip}")


if __name__ == '__main__':
    main()


