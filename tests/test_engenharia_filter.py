#!/usr/bin/env python3
"""
Script para testar se o filtro de Engenharia está funcionando corretamente
"""

import sqlite3
import json

def test_engineering_filter():
    print("🔧 Testando filtro de Engenharia...")
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect('ippel_system.db')
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        cursor = conn.cursor()
        
        # Buscar RNCs ativos com informações de departamento
        cursor.execute('''
            SELECT 
                r.id,
                r.rnc_number,
                r.title,
                r.status,
                u.name AS user_name,
                u.department AS user_department
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id
            WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL) 
            AND r.status NOT IN ('Finalizado')
            LIMIT 20
        ''')
        
        rncs = cursor.fetchall()
        
        print(f"\n📋 Total de RNCs ativos encontrados: {len(rncs)}")
        
        # Mostrar exemplos de cada departamento
        departments = {}
        for rnc in rncs:
            dept = rnc['user_department'] or 'Sem Departamento'
            if dept not in departments:
                departments[dept] = []
            departments[dept].append({
                'id': rnc['id'],
                'number': rnc['rnc_number'],
                'title': rnc['title'][:50] + '...' if rnc['title'] and len(rnc['title']) > 50 else rnc['title']
            })
        
        print(f"\n📊 Departamentos encontrados:")
        for dept, rnc_list in departments.items():
            print(f"  {dept}: {len(rnc_list)} RNCs")
            for rnc in rnc_list[:3]:  # Mostrar apenas os 3 primeiros
                print(f"    - {rnc['number']}: {rnc['title']}")
            if len(rnc_list) > 3:
                print(f"    ... e mais {len(rnc_list) - 3} RNCs")
        
        # Testar filtro específico de Engenharia
        engineering_rncs = [rnc for rnc in rncs if rnc['user_department'] and 'engenharia' in rnc['user_department'].lower()]
        
        print(f"\n🔧 RNCs de Engenharia encontrados: {len(engineering_rncs)}")
        for rnc in engineering_rncs[:5]:  # Mostrar os 5 primeiros
            print(f"  - {rnc['rnc_number']}: {rnc['title'][:50]}... (Dept: {rnc['user_department']})")
        
        # Verificar total de RNCs de Engenharia no banco todo
        cursor.execute('''
            SELECT COUNT(*) as total
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id
            WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL)
            AND r.status NOT IN ('Finalizado')
            AND u.department LIKE '%engenharia%'
        ''')
        
        total_eng = cursor.fetchone()['total']
        print(f"\n📈 Total de RNCs ativos de Engenharia no banco: {total_eng}")
        
        conn.close()
        
        return len(engineering_rncs) > 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    test_engineering_filter()
