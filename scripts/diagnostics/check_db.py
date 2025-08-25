#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_databases():
    print('=== VERIFICANDO BANCOS DE DADOS ===')
    
    # Testar database.db
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        print(f'database.db - Tabelas: {[t[0] for t in tables]}')
        
        if 'rncs' in [t[0] for t in tables]:
            cursor.execute('SELECT COUNT(*) FROM rncs')
            count = cursor.fetchone()[0]
            print(f'database.db - RNCs: {count}')
        conn.close()
    except Exception as e:
        print(f'database.db - Erro: {e}')
    
    # Testar ippel_system_new.db
    try:
        conn = sqlite3.connect('ippel_system_new.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        print(f'ippel_system_new.db - Tabelas: {[t[0] for t in tables]}')
        
        if 'rncs' in [t[0] for t in tables]:
            cursor.execute('SELECT COUNT(*) FROM rncs')
            count = cursor.fetchone()[0]
            print(f'ippel_system_new.db - RNCs: {count}')
        conn.close()
    except Exception as e:
        print(f'ippel_system_new.db - Erro: {e}')

if __name__ == "__main__":
    check_databases()
