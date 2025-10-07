#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples dos dados de engenharia
"""
import sqlite3
from datetime import datetime

def test_data():
    """Testa diretamente no banco os dados que seriam retornados pela API"""
    
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("Testando consulta da API de engenharia...")
        
        # A mesma consulta da API
        cursor.execute("""
            SELECT 
                id, rnc_number, title, equipment, client, priority, status,
                responsavel, setor, area_responsavel, finalized_at, created_at,
                price
            FROM rncs 
            WHERE (
                responsavel LIKE '%guilherme%' OR 
                responsavel LIKE '%cintia%' OR 
                responsavel LIKE '%cíntia%' OR
                area_responsavel LIKE '%engenharia%' OR
                finalized_at IS NOT NULL
            ) AND (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY finalized_at DESC, created_at DESC
            LIMIT 5
        """)
        
        rncs_raw = cursor.fetchall()
        print(f"Total RNCs encontradas (sample): {len(rncs_raw)}")
        
        # Verificar se temos dados com created_at
        for rnc in rncs_raw:
            created_at = rnc[11]    # created_at
            finalized_at = rnc[10]  # finalized_at
            responsavel = rnc[7]    # responsavel
            
            print(f"RNC {rnc[1]}:")
            print(f"  Responsavel: {responsavel}")
            print(f"  Created: {created_at}")
            print(f"  Finalized: {finalized_at}")
            
            # Testar parsing de data
            date_to_use = finalized_at or created_at
            if date_to_use and date_to_use != 'None':
                try:
                    date = datetime.strptime(date_to_use, '%Y-%m-%d %H:%M:%S')
                    print(f"  Data processada: {date.strftime('%Y-%m')}")
                except:
                    try:
                        date = datetime.strptime(date_to_use.split(' ')[0], '%Y-%m-%d')
                        print(f"  Data processada (sem hora): {date.strftime('%Y-%m')}")
                    except:
                        print(f"  ERRO ao processar data: {date_to_use}")
            else:
                print(f"  Nenhuma data válida disponível")
        
        conn.close()
        print("Teste concluído!")
            
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data()