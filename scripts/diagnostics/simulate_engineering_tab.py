#!/usr/bin/env python3
"""
Script para simular o filtro da aba Engenharia
"""

import sqlite3
import json

def simulate_engineering_tab():
    print("🔧 Simulando aba Engenharia...")
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect('ippel_system.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simular a consulta da API /api/rnc/list?tab=finalized
        cursor.execute('''
            SELECT 
                r.id,
                r.rnc_number,
                r.title,
                r.equipment,
                r.client,
                r.priority,
                r.status,
                r.user_id,
                r.assigned_user_id,
                r.created_at,
                r.updated_at,
                r.finalized_at,
                u.name AS user_name,
                u.department AS user_department,
                au.name AS assigned_user_name
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN users au ON r.assigned_user_id = au.id
            WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL) 
            AND r.status = 'Finalizado'
            ORDER BY r.id DESC
            LIMIT 20
        ''')
        
        finalized_rncs = cursor.fetchall()
        
        print(f"📋 Total de RNCs finalizados (amostra): {len(finalized_rncs)}")
        
        # Simular filtro JavaScript: rnc.user_department && rnc.user_department.toLowerCase().includes('engenharia')
        engineering_rncs = []
        for rnc in finalized_rncs:
            if rnc['user_department'] and 'engenharia' in rnc['user_department'].lower():
                engineering_rncs.append(rnc)
        
        print(f"🔧 RNCs de Engenharia filtrados: {len(engineering_rncs)}")
        
        for rnc in engineering_rncs:
            title = rnc['title'][:50] + '...' if rnc['title'] and len(rnc['title']) > 50 else rnc['title']
            print(f"  - {rnc['rnc_number']}: {title} (Dept: {rnc['user_department']})")
        
        # Verificar total completo de Engenharia
        cursor.execute('''
            SELECT COUNT(*) as total
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id
            WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL) 
            AND r.status = 'Finalizado'
            AND u.department LIKE '%engenharia%'
        ''')
        
        total_eng = cursor.fetchone()['total']
        print(f"\n📈 Total de RNCs de Engenharia no banco: {total_eng}")
        
        # Simular a estrutura JSON que seria retornada
        result_data = []
        for rnc in finalized_rncs[:5]:  # Primeiros 5 para exemplo
            if rnc['user_department'] and 'engenharia' in rnc['user_department'].lower():
                result_data.append({
                    'id': rnc['id'],
                    'rnc_number': rnc['rnc_number'],
                    'title': rnc['title'],
                    'user_department': rnc['user_department'],
                    'status': rnc['status']
                })
        
        print(f"\n📊 Exemplo de dados que apareceriam na aba:")
        print(json.dumps(result_data, indent=2, ensure_ascii=False))
        
        conn.close()
        
        return len(engineering_rncs) > 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    simulate_engineering_tab()
