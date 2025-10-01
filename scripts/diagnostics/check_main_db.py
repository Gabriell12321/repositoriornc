#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_main_database():
    print('=== VERIFICANDO ippel_system.db ===')
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Verificar tabelas
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    print('Tabelas:', [t[0] for t in tables])
    
    if 'rncs' in [t[0] for t in tables]:
        # Total de RNCs
        cursor.execute('SELECT COUNT(*) FROM rncs')
        count = cursor.fetchone()[0]
        print(f'Total de RNCs: {count}')
        
        # Verificar setores únicos
        cursor.execute('SELECT DISTINCT setor FROM rncs WHERE setor IS NOT NULL ORDER BY setor')
        setores = cursor.fetchall()
        print(f'Total de setores: {len(setores)}')
        print('Primeiros 15 setores:', [s[0] for s in setores[:15]])
        
        # Verificar se há engenharia (case insensitive)
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE LOWER(setor) LIKE "%engenharia%"')
        eng_count = cursor.fetchone()[0]
        print(f'RNCs com "engenharia" no setor: {eng_count}')
        
        # Verificar variações
        cursor.execute('SELECT DISTINCT setor FROM rncs WHERE LOWER(setor) LIKE "%eng%" ORDER BY setor')
        eng_setores = cursor.fetchall()
        print('Setores com "eng":', [s[0] for s in eng_setores])
        
        # Últimas RNCs para debug
        cursor.execute('SELECT id, titulo, setor, status FROM rncs ORDER BY id DESC LIMIT 5')
        ultimas = cursor.fetchall()
        print('\nÚltimas 5 RNCs:')
        for rnc in ultimas:
            print(f'  ID: {rnc[0]} | Setor: {rnc[2]} | Status: {rnc[3]} | Título: {rnc[1][:40]}...')
    
    conn.close()

if __name__ == "__main__":
    check_main_database()
