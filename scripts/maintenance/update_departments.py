#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def update_rnc_departments():
    """Atualiza RNCs que não possuem departamento com o departamento do usuário"""
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()

    print('=== ATUALIZANDO RNCs SEM DEPARTAMENTO ===')

    # Atualizar RNCs que não possuem departamento
    cursor.execute('''
        UPDATE rncs 
        SET department = (
            SELECT u.department 
            FROM users u 
            WHERE u.id = rncs.user_id
        )
        WHERE (department IS NULL OR department = '')
    ''')

    affected = cursor.rowcount
    conn.commit()

    print(f'✅ {affected} RNCs atualizadas com departamento do usuário')

    # Verificar alguns exemplos
    cursor.execute('SELECT id, title, department, user_id FROM rncs WHERE status = "Finalizado" LIMIT 5')
    for row in cursor.fetchall():
        title = row[1][:30] + '...' if len(row[1]) > 30 else row[1]
        print(f'RNC {row[0]}: {title} -> Setor: {row[2]} (user: {row[3]})')

    conn.close()
    print('✅ Atualização concluída!')

if __name__ == '__main__':
    update_rnc_departments()
