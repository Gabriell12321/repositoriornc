#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test engineering endpoint directly"""

import sqlite3
from datetime import datetime
import json

def test_engineering_endpoint():
    """Test the engineering endpoint logic"""
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        year = datetime.now().year
        meta_mensal = 30
        meses = ['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ']
        realizado_meses = []
        acumulado = 0
        acumulado_lista = []
        variacoes = []
        
        for idx in range(1,13):
            cursor.execute("""
                SELECT COUNT(*) FROM rncs
                WHERE is_deleted = 0
                  AND strftime('%Y', created_at) = ?
                  AND strftime('%m', created_at) = ?
            """, (str(year), f"{idx:02d}"))
            count = cursor.fetchone()[0]
            realizado_meses.append(count)
            acumulado += count
            acumulado_lista.append(acumulado)
            variacoes.append(count - meta_mensal)
        
        conn.close()
        
        result = {
            'success': True,
            'data': {
                'ano': year,
                'meta_mensal': meta_mensal,
                'meses': meses,
                'realizado': realizado_meses,
                'variacao': variacoes,
                'acumulado': acumulado_lista,
                'acumulado_total': acumulado,
                'meta_acumulada': meta_mensal * 12
            }
        }
        
        print("✅ Engineering endpoint test result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"❌ Engineering endpoint test error: {e}")
        return None

if __name__ == "__main__":
    test_engineering_endpoint()
