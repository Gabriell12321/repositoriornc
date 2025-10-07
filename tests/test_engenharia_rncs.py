#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se as RNCs da Engenharia estão sendo exibidas
"""

import sqlite3

def test_engenharia_rncs():
    """Testa o filtro de RNCs por departamento"""
    print("=" * 80)
    print("TESTE: RNCs DA ENGENHARIA")
    print("=" * 80)
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # 1. Verificar usuários e seus departamentos
    print("\n1. USUÁRIOS E DEPARTAMENTOS:")
    cursor.execute('SELECT id, name, email, department FROM users')
    users = cursor.fetchall()
    for user in users:
        print(f"   ID {user[0]}: {user[1]} ({user[2]}) - Departamento: {user[3]}")
    
    # 2. Verificar quantas RNCs existem por área responsável
    print("\n2. RNCs POR ÁREA RESPONSÁVEL:")
    cursor.execute('''
        SELECT area_responsavel, COUNT(*) as total
        FROM rncs
        WHERE (is_deleted = 0 OR is_deleted IS NULL)
        GROUP BY area_responsavel
        ORDER BY total DESC
    ''')
    areas = cursor.fetchall()
    for area in areas:
        area_name = area[0] if area[0] else 'Não definida'
        print(f"   {area_name}: {area[1]} RNCs")
    
    # 3. Verificar RNCs específicas da Engenharia
    print("\n3. RNCs DA ENGENHARIA (primeiras 10):")
    cursor.execute('''
        SELECT id, rnc_number, title, area_responsavel, setor, status
        FROM rncs
        WHERE (is_deleted = 0 OR is_deleted IS NULL)
          AND (LOWER(area_responsavel) = 'engenharia' OR LOWER(setor) = 'engenharia')
        LIMIT 10
    ''')
    eng_rncs = cursor.fetchall()
    if eng_rncs:
        for rnc in eng_rncs:
            print(f"   RNC #{rnc[0]}: {rnc[1]} - {rnc[2][:50]}")
            print(f"            Área: {rnc[3]} | Setor: {rnc[4]} | Status: {rnc[5]}")
    else:
        print("   ⚠️ Nenhuma RNC da Engenharia encontrada!")
    
    # 4. Simular query que seria executada para um usuário da Engenharia
    print("\n4. SIMULAÇÃO DE QUERY PARA USUÁRIO DA ENGENHARIA:")
    user_department = 'Engenharia'
    user_id = 1  # Exemplo
    
    # Query similar à que será executada no código corrigido
    cursor.execute('''
        SELECT DISTINCT
            r.id, r.rnc_number, r.title, r.area_responsavel, r.setor, r.status
        FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        LEFT JOIN users au ON r.assigned_user_id = au.id
        LEFT JOIN rnc_shares rs ON rs.rnc_id = r.id
        WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL)
          AND r.status NOT IN ('Finalizado')
          AND (
              r.user_id = ? 
              OR r.assigned_user_id = ? 
              OR rs.shared_with_user_id = ?
              OR LOWER(r.area_responsavel) = LOWER(?)
              OR LOWER(r.setor) = LOWER(?)
          )
        LIMIT 10
    ''', (user_id, user_id, user_id, user_department, user_department))
    
    result_rncs = cursor.fetchall()
    print(f"   Total de RNCs que seriam exibidas: {len(result_rncs)}")
    if result_rncs:
        for rnc in result_rncs:
            print(f"   RNC #{rnc[0]}: {rnc[1]} - Área: {rnc[3]} | Setor: {rnc[4]}")
    
    # 5. Verificar total por status
    print("\n5. TOTAL DE RNCs DA ENGENHARIA POR STATUS:")
    cursor.execute('''
        SELECT status, COUNT(*) as total
        FROM rncs
        WHERE (is_deleted = 0 OR is_deleted IS NULL)
          AND (LOWER(area_responsavel) = 'engenharia' OR LOWER(setor) = 'engenharia')
        GROUP BY status
        ORDER BY total DESC
    ''')
    status_counts = cursor.fetchall()
    for status in status_counts:
        print(f"   {status[0]}: {status[1]} RNCs")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 80)

if __name__ == "__main__":
    test_engenharia_rncs()
