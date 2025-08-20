#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_users_and_rncs():
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()

    print('=== VERIFICANDO USUÁRIOS ===')
    cursor.execute('SELECT id, name, department FROM users WHERE name IN ("engenharia", "Ronaldo")')
    for row in cursor.fetchall():
        print(f'User {row[0]}: {row[1]} -> Dept: {row[2]}')

    print('\n=== VERIFICANDO RNCs ESPECÍFICAS ===')
    cursor.execute('SELECT id, title, department, user_id FROM rncs WHERE id IN (10255, 18550, 18229)')
    for row in cursor.fetchall():
        print(f'RNC {row[0]}: Dept na RNC: {row[2]}, User ID: {row[3]}')

    print('\n=== ATUALIZANDO RNCs SEM DEPARTAMENTO ===')
    cursor.execute('''
        UPDATE rncs 
        SET department = COALESCE(
            (SELECT u.department FROM users u WHERE u.id = rncs.user_id),
            'N/A'
        )
        WHERE department IS NULL OR department = ''
    ''')
    
    affected = cursor.rowcount
    conn.commit()
    print(f'✅ {affected} RNCs atualizadas')

    print('\n=== VERIFICANDO NOVAMENTE ===')
    cursor.execute('SELECT id, title, department, user_id FROM rncs WHERE id IN (10255, 18550, 18229)')
    for row in cursor.fetchall():
        print(f'RNC {row[0]}: Dept na RNC: {row[2]}, User ID: {row[3]}')

    conn.close()

if __name__ == '__main__':
    check_users_and_rncs()
