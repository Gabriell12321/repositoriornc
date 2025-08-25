#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Importador de dados do Access (.accdb) para o banco SQLite do sistema IPPEL.

Recursos:
- Conecta no arquivo .accdb via ODBC (requer driver do Access instalado)
- Lista colunas e exporta amostra para CSV para validação
- Prepara mapeamento de campos para inserir em rncs (ou rnc_reports)

Uso (exemplos):
  python import_access_to_sqlite.py --access "ARQUIVOS PARA PUXAR INFORMAÇÕES PARA O PAINEL/Lancamento RNC.accdb" \
    --table "CADASTRO RNC" --export-sample sample_cadastro_rnc.csv --limit 50

  python import_access_to_sqlite.py --access ".../Lancamento RNC.accdb" --table "CADASTRO RNC" \
    --dest rncs --commit --limit 100

Observação: no Windows, instale o driver ODBC do Access (ACE OLEDB/ODBC 2016+).
"""

import argparse
import csv
import os
import sqlite3
from typing import Dict, Any, Iterable, List, Optional

# pyodbc é usado para conectar no Access via ODBC
try:
    import pyodbc  # type: ignore
except Exception as e:  # pragma: no cover
    pyodbc = None


DEFAULT_SQLITE_DB = 'ippel_system.db'


def connect_access_db(access_path: str):
    if pyodbc is None:
        raise RuntimeError(
            'pyodbc não está instalado. Adicione pyodbc ao seu ambiente e instale o "Microsoft Access Database Engine".'
        )
    if not os.path.exists(access_path):
        raise FileNotFoundError(f"Arquivo Access não encontrado: {access_path}")

    conn_str = (
        r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
        rf'DBQ={os.path.abspath(access_path)};'
    )
    return pyodbc.connect(conn_str)


def fetch_rows(conn, table: str, limit: Optional[int] = None) -> Iterable[Dict[str, Any]]:
    cursor = conn.cursor()
    top_clause = f"TOP {int(limit)} " if (limit and limit > 0) else ""
    sql = f"SELECT {top_clause}* FROM [{table}]"
    cursor.execute(sql)
    columns = [col[0] for col in cursor.description]
    for row in cursor.fetchall():
        yield {columns[i]: row[i] for i in range(len(columns))}


def export_sample(rows: Iterable[Dict[str, Any]], out_csv: str, max_rows: int = 100) -> int:
    count = 0
    rows = list(rows)
    if not rows:
        with open(out_csv, 'w', newline='', encoding='utf-8') as f:
            pass
        return 0
    fieldnames = list(rows[0].keys())
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows[:max_rows]:
            writer.writerow({k: ('' if row[k] is None else row[k]) for k in fieldnames})
            count += 1
    return count


def ensure_rncs_schema(sqlite_path: str) -> None:
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    # Garantir tabela rncs e colunas essenciais
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS rncs (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               rnc_number TEXT UNIQUE,
               title TEXT,
               description TEXT,
               equipment TEXT,
               client TEXT,
               priority TEXT DEFAULT 'Média',
               status TEXT DEFAULT 'Pendente',
               user_id INTEGER,
               assigned_user_id INTEGER,
               is_deleted BOOLEAN DEFAULT 0,
               deleted_at TIMESTAMP,
               finalized_at TIMESTAMP,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )'''
    )
    # Colunas adicionais usadas no sistema
    for col_def in [
        ('price', 'REAL DEFAULT 0'),
        ('signature_inspection_name', 'TEXT'),
        ('signature_engineering_name', 'TEXT'),
        ('signature_inspection2_name', 'TEXT'),
    ]:
        try:
            cursor.execute(f'ALTER TABLE rncs ADD COLUMN {col_def[0]} {col_def[1]}')
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()


def infer_priority(value: Any) -> str:
    if value is None:
        return 'Média'
    text = str(value).strip().lower()
    if text.startswith('bai'):
        return 'Baixa'
    if text.startswith('alt'):
        return 'Alta'
    if text.startswith('cr'):
        return 'Crítica'
    return 'Média'


def default_mapping() -> Dict[str, str]:
    """Mapeamento padrão (ajustaremos juntos conforme os campos reais do Access).

    Chave = campo SQLite rncs; Valor = nome da coluna no Access.
    """
    return {
        'rnc_number': 'NUMERO',        # ex.: campo no Access com o número da RNC
        'title': 'TITULO',             # título/assunto
        'description': 'DESCRICAO',    # descrição
        'equipment': 'EQUIPAMENTO',
        'client': 'CLIENTE',
        'priority': 'PRIORIDADE',
        'status': 'STATUS',
        'price': 'PRECO',
        'signature_inspection_name': 'ASSINATURA1',
        'signature_engineering_name': 'ASSINATURA2',
        'signature_inspection2_name': 'ASSINATURA3',
    }


def transform_row(row: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for dest, src in mapping.items():
        val = row.get(src)
        if dest == 'priority':
            out[dest] = infer_priority(val)
        elif dest == 'price':
            try:
                out[dest] = float(val) if val not in (None, '') else 0.0
            except Exception:
                out[dest] = 0.0
        else:
            out[dest] = val
    # Defaults
    out.setdefault('status', 'Pendente')
    return out


def insert_into_rncs(sqlite_path: str, rows: List[Dict[str, Any]], user_id: int = 1) -> int:
    ensure_rncs_schema(sqlite_path)
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    inserted = 0
    for r in rows:
        cur.execute(
            '''INSERT OR IGNORE INTO rncs (
                   rnc_number, title, description, equipment, client, priority, status,
                   user_id, assigned_user_id, price,
                   signature_inspection_name, signature_engineering_name, signature_inspection2_name
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                r.get('rnc_number') or None,
                r.get('title') or '',
                r.get('description') or '',
                r.get('equipment') or '',
                r.get('client') or '',
                r.get('priority') or 'Média',
                r.get('status') or 'Pendente',
                user_id,
                None,
                r.get('price') or 0,
                r.get('signature_inspection_name') or '',
                r.get('signature_engineering_name') or '',
                r.get('signature_inspection2_name') or '',
            ),
        )
        inserted += cur.rowcount > 0
    conn.commit()
    conn.close()
    return inserted


def main():
    parser = argparse.ArgumentParser(description='Importar dados do Access para SQLite (IPPEL).')
    parser.add_argument('--access', required=True, help='Caminho do arquivo .accdb')
    parser.add_argument('--table', required=True, help='Tabela do Access (ex.: "CADASTRO RNC")')
    parser.add_argument('--sqlite', default=DEFAULT_SQLITE_DB, help='Caminho do banco SQLite de destino')
    parser.add_argument('--export-sample', help='Exportar amostra para CSV')
    parser.add_argument('--limit', type=int, default=100, help='Limite de linhas para leitura (0 = tudo)')
    parser.add_argument('--commit', action='store_true', help='Inserir no SQLite (sem este flag, apenas mostra)')

    args = parser.parse_args()

    acc = connect_access_db(args.access)
    rows = list(fetch_rows(acc, args.table, limit=args.limit if args.limit > 0 else None))
    print(f"Lidas {len(rows)} linhas da tabela {args.table}")

    if args.export_sample:
        exported = export_sample(rows, args.export_sample, max_rows=max(args.limit, 1))
        print(f"Amostra exportada para: {args.export_sample} ({exported} linhas)")

    # Transformar dados conforme mapeamento padrão (ajustaremos juntos)
    mapping = default_mapping()
    transformed = [transform_row(r, mapping) for r in rows]

    if args.commit:
        inserted = insert_into_rncs(args.sqlite, transformed)
        print(f"Inseridos {inserted} registros em {args.sqlite} -> tabela rncs")
    else:
        # Mostrar algumas linhas transformadas para conferência
        for i, r in enumerate(transformed[:5]):
            print(f"Exemplo {i+1}: {r}")
        print("(Execute novamente com --commit para gravar no SQLite)")


if __name__ == '__main__':
    main()


