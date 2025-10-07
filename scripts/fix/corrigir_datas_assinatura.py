#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir datas de assinatura vazias
Popula as datas usando created_at como base
"""

import sqlite3
from datetime import datetime

def fix_signature_dates():
    """Corrige datas de assinatura vazias"""
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("🔧 CORRIGINDO DATAS DE ASSINATURA")
    print("=" * 80)
    
    # Verificar RNCs com datas vazias
    cursor.execute("""
        SELECT id, created_at, signature_inspection_date, signature_engineering_date, signature_inspection2_date
        FROM rncs
        WHERE (signature_inspection_date IS NULL OR signature_inspection_date = '')
           OR (signature_engineering_date IS NULL OR signature_engineering_date = '')
           OR (signature_inspection2_date IS NULL OR signature_inspection2_date = '')
    """)
    
    rncs_to_fix = cursor.fetchall()
    
    print(f"\n📊 Encontradas {len(rncs_to_fix)} RNCs com datas de assinatura vazias\n")
    
    if len(rncs_to_fix) == 0:
        print("✅ Todas as RNCs já têm datas de assinatura!")
        conn.close()
        return
    
    updated = 0
    
    for rnc_id, created_at, sig_insp, sig_eng, sig_insp2 in rncs_to_fix:
        # Usar created_at como base (pegar apenas a data, formato YYYY-MM-DD)
        if created_at:
            base_date = created_at[:10] if len(created_at) >= 10 else datetime.now().strftime('%Y-%m-%d')
        else:
            base_date = datetime.now().strftime('%Y-%m-%d')
        
        # Converter para formato brasileiro dd/mm/yyyy
        try:
            date_obj = datetime.strptime(base_date, '%Y-%m-%d')
            br_date = date_obj.strftime('%d/%m/%Y')
        except:
            br_date = datetime.now().strftime('%d/%m/%Y')
        
        # Atualizar apenas as datas vazias
        updates = []
        params = []
        
        if not sig_insp or sig_insp.strip() == '':
            updates.append("signature_inspection_date = ?")
            params.append(br_date)
        
        if not sig_eng or sig_eng.strip() == '':
            updates.append("signature_engineering_date = ?")
            params.append(br_date)
        
        if not sig_insp2 or sig_insp2.strip() == '':
            updates.append("signature_inspection2_date = ?")
            params.append(br_date)
        
        if updates:
            params.append(rnc_id)
            query = f"UPDATE rncs SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            updated += 1
            
            if updated <= 10:  # Mostrar apenas as primeiras 10
                print(f"  ✅ RNC {rnc_id}: Data base {br_date}")
    
    conn.commit()
    
    # Verificar resultado
    cursor.execute("""
        SELECT COUNT(*) FROM rncs
        WHERE (signature_inspection_date IS NOT NULL AND signature_inspection_date != '')
          AND (signature_engineering_date IS NOT NULL AND signature_engineering_date != '')
          AND (signature_inspection2_date IS NOT NULL AND signature_inspection2_date != '')
    """)
    total_ok = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rncs")
    total = cursor.fetchone()[0]
    
    print("\n" + "=" * 80)
    print("📊 RESULTADO")
    print("=" * 80)
    print(f"✅ RNCs atualizadas: {updated}")
    print(f"✅ RNCs com datas completas: {total_ok}/{total} ({(total_ok/total*100):.1f}%)")
    print("=" * 80)
    
    conn.close()

if __name__ == '__main__':
    fix_signature_dates()
