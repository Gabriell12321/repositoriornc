#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_engineering_correct():
    print('=== VERIFICANDO DADOS DE ENGENHARIA (COLUNAS CORRETAS) ===')
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Total de RNCs
    cursor.execute('SELECT COUNT(*) FROM rncs')
    count = cursor.fetchone()[0]
    print(f'Total de RNCs: {count}')
    
    # Verificar departamentos únicos
    cursor.execute('SELECT DISTINCT department FROM rncs WHERE department IS NOT NULL ORDER BY department')
    departments = cursor.fetchall()
    print(f'Total de departamentos: {len(departments)}')
    print('Departamentos encontrados:')
    for dept in departments:
        print(f'  - {dept[0]}')
    
    # Verificar se há engenharia (case insensitive)
    cursor.execute('SELECT COUNT(*) FROM rncs WHERE LOWER(department) LIKE "%engenharia%"')
    eng_count = cursor.fetchone()[0]
    print(f'\nRNCs com "engenharia" no departamento: {eng_count}')
    
    # Verificar variações
    cursor.execute('SELECT DISTINCT department FROM rncs WHERE LOWER(department) LIKE "%eng%" ORDER BY department')
    eng_depts = cursor.fetchall()
    print('Departamentos com "eng":')
    for dept in eng_depts:
        print(f'  - {dept[0]}')
    
    # Contar por departamento
    cursor.execute('''
        SELECT department, COUNT(*) as total
        FROM rncs 
        WHERE department IS NOT NULL
        GROUP BY department
        ORDER BY total DESC
        LIMIT 10
    ''')
    top_depts = cursor.fetchall()
    print('\nTop 10 departamentos por quantidade:')
    for dept in top_depts:
        print(f'  {dept[0]}: {dept[1]} RNCs')
    
    # Verificar status das RNCs de engenharia
    if eng_count > 0:
        cursor.execute('''
            SELECT status, COUNT(*) as total
            FROM rncs 
            WHERE LOWER(department) LIKE "%engenharia%"
            GROUP BY status
        ''')
        eng_status = cursor.fetchall()
        print('\nStatus das RNCs de Engenharia:')
        for status in eng_status:
            print(f'  {status[0]}: {status[1]}')
    
    # Últimas RNCs para debug
    cursor.execute('SELECT id, title, department, status FROM rncs ORDER BY id DESC LIMIT 5')
    ultimas = cursor.fetchall()
    print('\nÚltimas 5 RNCs:')
    for rnc in ultimas:
        print(f'  ID: {rnc[0]} | Dept: {rnc[2]} | Status: {rnc[3]} | Título: {rnc[1][:40]}...')
    
    conn.close()

if __name__ == "__main__":
    check_engineering_correct()
