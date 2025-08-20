import argparse
import csv
import os
import re
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, Tuple


TXT_DEFAULT_PATH = os.path.join(
    'ARQUIVOS PARA PUXAR INFORMAÇÕES PARA O PAINEL',
    'RNC FINALIZADAS PUXAR PARA O BANCO DE DADOS.txt'
)


def ensure_rncs_schema(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
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


def parse_brl_money(value: str) -> float:
    if value is None:
        return 0.0
    v = value.strip()
    if not v:
        return 0.0
    v = v.replace('R$', '').replace(' ', '')
    v = v.replace('.', '').replace(',', '.')
    try:
        return float(v)
    except ValueError:
        return 0.0


def parse_date_br(value: str) -> Optional[str]:
    if not value:
        return None
    v = value.strip()
    if not v:
        return None
    # Tentar dd/mm/yyyy
    for fmt in ('%d/%m/%Y', '%d/%m/%y'):
        try:
            dt = datetime.strptime(v, fmt)
            # Usar meio-dia para evitar problemas de fuso
            return dt.strftime('%Y-%m-%d 12:00:00')
        except ValueError:
            continue
    return None


def normalize_text(value: Any) -> str:
    if value is None:
        return ''
    return str(value).strip()


def build_title(row: Dict[str, str]) -> str:
    # Preferir descrição da RNC; se ausente, usar descrição do desenho
    desc_rnc = normalize_text(row.get('DESCRIÇÃO DA RNC'))
    desc_des = normalize_text(row.get('DESCRIÇÃO DO DESENHO'))
    title = desc_rnc or desc_des
    if not title:
        # fallback curto
        title = f"RNC {normalize_text(row.get('Nº RNC'))}"
    # Limitar tamanho exagerado (UI)
    return title[:200]


def build_description(row: Dict[str, str]) -> str:
    parts = []
    def add(label: str, key: str):
        val = normalize_text(row.get(key))
        if val:
            parts.append(f"{label}: {val}")

    add('Desenho', 'DESENHO')
    add('MP', 'MP')
    add('Revisão', 'REVISÃO')
    add('POS', 'POS')
    add('CV', 'CV')
    add('Conjunto', 'CONJUNTO')
    add('Modelo', 'MODELO')
    add('Descrição do desenho', 'DESCRIÇÃO DO DESENHO')
    add('Quantidade', 'QUANTIDADE')
    add('Material', 'MATERIAL')
    add('Ordem de Compra', 'ORDEM DE COMPRA')
    add('Área responsável', 'ÁREA RESPONSÁVEL')
    add('Setor', 'SETOR')
    add('Descrição da RNC', 'DESCRIÇÃO DA RNC')
    add('Instrução para retrabalho', 'INSTRUÇÃO PARA RETRABALHO')
    add('Causa da RNC', 'CAUSA DA RNC')
    add('Justificativa', 'JUSTIFICATIVA')

    # Preço textual também, para auditoria
    val_txt = normalize_text(row.get('VALOR'))
    if val_txt:
        parts.append(f"Valor (texto original): {val_txt}")

    return '\n'.join(parts)


def find_default_user_ids(conn: sqlite3.Connection) -> Tuple[Optional[int], Optional[int]]:
    cursor = conn.cursor()
    creator_id = None
    assigned_id = None
    try:
        cursor.execute("SELECT id FROM users WHERE role='admin' ORDER BY id LIMIT 1")
        row = cursor.fetchone()
        if row:
            creator_id = row[0]
        cursor.execute("SELECT id FROM users WHERE is_active=1 ORDER BY id LIMIT 1")
        row = cursor.fetchone()
        if row:
            assigned_id = row[0]
    except sqlite3.OperationalError:
        pass
    return creator_id, assigned_id


def upsert_rnc(conn: sqlite3.Connection, r: Dict[str, Any]) -> None:
    cursor = conn.cursor()
    sql = (
        """
        INSERT INTO rncs (
            rnc_number, title, description, equipment, client, priority,
            status, user_id, assigned_user_id, price,
            signature_inspection_name, signature_engineering_name,
            created_at, updated_at, finalized_at
        ) VALUES (
            :rnc_number, :title, :description, :equipment, :client, :priority,
            :status, :user_id, :assigned_user_id, :price,
            :signature_inspection_name, :signature_engineering_name,
            :created_at, :updated_at, :finalized_at
        )
        ON CONFLICT(rnc_number) DO UPDATE SET
            title=excluded.title,
            description=excluded.description,
            equipment=excluded.equipment,
            client=excluded.client,
            priority=excluded.priority,
            status=excluded.status,
            user_id=COALESCE(excluded.user_id, rncs.user_id),
            assigned_user_id=COALESCE(excluded.assigned_user_id, rncs.assigned_user_id),
            price=excluded.price,
            signature_inspection_name=COALESCE(rncs.signature_inspection_name, excluded.signature_inspection_name),
            signature_engineering_name=COALESCE(rncs.signature_engineering_name, excluded.signature_engineering_name),
            finalized_at=COALESCE(excluded.finalized_at, rncs.finalized_at),
            updated_at=excluded.updated_at
        """
    )
    cursor.execute(sql, r)


def main():
    parser = argparse.ArgumentParser(description='Importar RNCs finalizadas a partir de TXT tabulado')
    parser.add_argument('--db', default='ippel_system.db', help='Caminho do SQLite')
    parser.add_argument('--txt', default=TXT_DEFAULT_PATH, help='Caminho do arquivo TXT tabulado')
    args = parser.parse_args()

    if not os.path.exists(args.txt):
        raise SystemExit(f"Arquivo TXT não encontrado: {args.txt}")

    conn = sqlite3.connect(args.db)
    try:
        ensure_rncs_schema(conn)
        default_creator_id, default_assigned_id = find_default_user_ids(conn)

        inserted = 0
        updated = 0

        with open(args.txt, 'r', encoding='utf-8-sig', newline='') as f:
            # Detectar separador: parece tabulado
            sample = f.read(4096)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters='\t;,')
            reader = csv.DictReader(f, dialect=dialect)

            required = ['Nº RNC', 'CLIENTE', 'EQUIPAMENTO', 'INSPETOR', 'RESPONSÁVEL', 'DATA EMISSÃO', 'VALOR']
            missing = [c for c in required if c not in reader.fieldnames]
            if missing:
                raise SystemExit(f"Cabeçalhos ausentes no TXT: {missing}\nEncontrados: {reader.fieldnames}")

            for row in reader:
                rnc_num = normalize_text(row.get('Nº RNC'))
                if not rnc_num:
                    # pular linhas vazias
                    continue

                # Evitar caracteres problemáticos no número
                rnc_number = rnc_num

                created_ts = parse_date_br(normalize_text(row.get('DATA EMISSÃO')))
                finalized_ts = created_ts or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                record = {
                    'rnc_number': rnc_number,
                    'title': build_title(row),
                    'description': build_description(row),
                    'equipment': normalize_text(row.get('EQUIPAMENTO')),
                    'client': normalize_text(row.get('CLIENTE')),
                    'priority': 'Média',
                    'status': 'Finalizado',
                    'user_id': default_creator_id,
                    'assigned_user_id': default_assigned_id,
                    'price': parse_brl_money(normalize_text(row.get('VALOR'))),
                    'signature_inspection_name': normalize_text(row.get('INSPETOR')),
                    'signature_engineering_name': normalize_text(row.get('RESPONSÁVEL')),
                    'created_at': created_ts or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'finalized_at': finalized_ts,
                }

                # Determinar se já existe
                cur = conn.cursor()
                cur.execute('SELECT 1 FROM rncs WHERE rnc_number = ?', (record['rnc_number'],))
                exists = cur.fetchone() is not None

                upsert_rnc(conn, record)

                if exists:
                    updated += 1
                else:
                    inserted += 1

        conn.commit()
        print(f"Importação concluída. Inseridos: {inserted}, Atualizados: {updated}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()


