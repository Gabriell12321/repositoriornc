#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo: verificar se as RNCs da Engenharia estão aparecendo corretamente
"""

import sqlite3

def test_engenharia_complete():
    """Testa todos os aspectos das RNCs da Engenharia"""
    print("=" * 80)
    print("TESTE COMPLETO: RNCs DA ENGENHARIA")
    print("=" * 80)
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # 1. Verificar total de RNCs da Engenharia
    print("\n1️⃣ TOTAL DE RNCs DA ENGENHARIA:")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM rncs 
        WHERE (is_deleted = 0 OR is_deleted IS NULL)
        AND (
            LOWER(TRIM(area_responsavel)) LIKE '%engenharia%'
            OR LOWER(TRIM(setor)) LIKE '%engenharia%'
        )
    """)
    total_eng = cursor.fetchone()[0]
    print(f"   Total: {total_eng} RNCs")
    
    # 2. Verificar por status
    print("\n2️⃣ RNCs DA ENGENHARIA POR STATUS:")
    cursor.execute("""
        SELECT status, COUNT(*) as total
        FROM rncs 
        WHERE (is_deleted = 0 OR is_deleted IS NULL)
        AND (
            LOWER(TRIM(area_responsavel)) LIKE '%engenharia%'
            OR LOWER(TRIM(setor)) LIKE '%engenharia%'
        )
        GROUP BY status
        ORDER BY total DESC
    """)
    status_data = cursor.fetchall()
    for status in status_data:
        print(f"   {status[0]}: {status[1]} RNCs")
    
    # 3. Verificar variações de "Engenharia" no campo area_responsavel
    print("\n3️⃣ VARIAÇÕES DO CAMPO 'area_responsavel':")
    cursor.execute("""
        SELECT DISTINCT area_responsavel, COUNT(*) as total
        FROM rncs 
        WHERE (is_deleted = 0 OR is_deleted IS NULL)
        AND LOWER(TRIM(area_responsavel)) LIKE '%engenharia%'
        GROUP BY area_responsavel
        ORDER BY total DESC
    """)
    area_variations = cursor.fetchall()
    for var in area_variations:
        print(f"   '{var[0]}': {var[1]} RNCs")
    
    # 4. Verificar variações do campo setor
    print("\n4️⃣ VARIAÇÕES DO CAMPO 'setor':")
    cursor.execute("""
        SELECT DISTINCT setor, COUNT(*) as total
        FROM rncs 
        WHERE (is_deleted = 0 OR is_deleted IS NULL)
        AND LOWER(TRIM(setor)) LIKE '%engenharia%'
        GROUP BY setor
        ORDER BY total DESC
    """)
    setor_variations = cursor.fetchall()
    if setor_variations:
        for var in setor_variations:
            setor_val = var[0] if var[0] else '(vazio)'
            print(f"   '{setor_val}': {var[1]} RNCs")
    else:
        print("   Nenhuma RNC com 'engenharia' no campo 'setor'")
    
    # 5. Simular query da API de indicadores
    print("\n5️⃣ SIMULAÇÃO DA API /api/indicadores/engenharia:")
    cursor.execute("""
        SELECT COUNT(*)
        FROM rncs 
        WHERE status = 'Finalizado'
        AND (
            LOWER(TRIM(area_responsavel)) LIKE '%engenharia%'
            OR LOWER(TRIM(setor)) LIKE '%engenharia%'
        )
        AND (is_deleted = 0 OR is_deleted IS NULL)
    """)
    api_count = cursor.fetchone()[0]
    print(f"   RNCs que a API retornaria: {api_count}")
    
    # 6. Simular query da listagem (aba Finalizados) para usuário da Engenharia
    print("\n6️⃣ SIMULAÇÃO DA LISTAGEM (aba Finalizados):")
    user_id = 3  # ID do usuário engenharia@ippel.com.br
    user_department = 'Engenharia'
    
    cursor.execute("""
        SELECT COUNT(DISTINCT r.id)
        FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        LEFT JOIN users au ON r.assigned_user_id = au.id
        LEFT JOIN rnc_shares rs ON rs.rnc_id = r.id
        WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL)
        AND r.status = 'Finalizado'
        AND (
            r.user_id = ? 
            OR r.assigned_user_id = ? 
            OR rs.shared_with_user_id = ?
            OR LOWER(TRIM(r.area_responsavel)) LIKE LOWER(TRIM(?))
            OR LOWER(TRIM(r.setor)) LIKE LOWER(TRIM(?))
        )
    """, (user_id, user_id, user_id, f'%{user_department.strip()}%', f'%{user_department.strip()}%'))
    
    list_count = cursor.fetchone()[0]
    print(f"   RNCs visíveis na listagem: {list_count}")
    
    # 7. Primeiras 5 RNCs que seriam exibidas
    print("\n7️⃣ PRIMEIRAS 5 RNCs QUE SERIAM EXIBIDAS:")
    cursor.execute("""
        SELECT DISTINCT r.id, r.rnc_number, r.title, r.area_responsavel, r.setor, r.status
        FROM rncs r
        LEFT JOIN rnc_shares rs ON rs.rnc_id = r.id
        WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL)
        AND r.status = 'Finalizado'
        AND (
            r.user_id = ? 
            OR r.assigned_user_id = ? 
            OR rs.shared_with_user_id = ?
            OR LOWER(TRIM(r.area_responsavel)) LIKE LOWER(TRIM(?))
            OR LOWER(TRIM(r.setor)) LIKE LOWER(TRIM(?))
        )
        ORDER BY r.id DESC
        LIMIT 5
    """, (user_id, user_id, user_id, f'%{user_department.strip()}%', f'%{user_department.strip()}%'))
    
    sample_rncs = cursor.fetchall()
    for rnc in sample_rncs:
        print(f"   • RNC #{rnc[0]}: {rnc[1]} - {rnc[2][:50]}")
        print(f"     Área: {rnc[3]} | Setor: {rnc[4]} | Status: {rnc[5]}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 80)
    
    # Resumo
    print("\n📊 RESUMO:")
    print(f"   • Total de RNCs da Engenharia: {total_eng}")
    print(f"   • RNCs que a API retorna: {api_count}")
    print(f"   • RNCs visíveis na listagem: {list_count}")
    
    if api_count > 0 and list_count > 0:
        print("\n✅ SUCESSO! As RNCs da Engenharia estão sendo puxadas corretamente!")
    else:
        print("\n⚠️ ATENÇÃO! Ainda há problemas com a query.")
    
    print("\n💡 INSTRUÇÕES:")
    print("   1. Faça login com: engenharia@ippel.com.br / engenharia123")
    print("   2. Clique na aba 'Finalizados'")
    print(f"   3. Você deve ver {list_count} RNCs da Engenharia")
    print("\n")

if __name__ == "__main__":
    test_engenharia_complete()
