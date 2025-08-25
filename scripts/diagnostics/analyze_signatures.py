#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import re
from collections import Counter

def analyze_signatures():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("=== ANALISANDO ASSINATURAS NAS RNCs ===")
        
        # Verificar campos de assinatura disponíveis
        cursor.execute('''
            SELECT 
                signature_inspection_name,
                signature_engineering_name,
                signature_inspection2_name,
                COUNT(*) as count
            FROM rncs 
            WHERE signature_inspection_name IS NOT NULL 
               OR signature_engineering_name IS NOT NULL 
               OR signature_inspection2_name IS NOT NULL
            GROUP BY signature_inspection_name, signature_engineering_name, signature_inspection2_name
            ORDER BY count DESC
            LIMIT 20
        ''')
        signatures = cursor.fetchall()
        
        print("Top 20 combinações de assinaturas:")
        for sig in signatures:
            print(f"Inspeção: {sig[0]} | Engenharia: {sig[1]} | Inspeção2: {sig[2]} | Count: {sig[3]}")
        
        # Analisar nomes únicos de inspeção
        print("\n=== NOMES DE INSPEÇÃO ÚNICOS ===")
        cursor.execute('''
            SELECT signature_inspection_name, COUNT(*) as count
            FROM rncs 
            WHERE signature_inspection_name IS NOT NULL 
              AND signature_inspection_name != ''
            GROUP BY signature_inspection_name
            ORDER BY count DESC
        ''')
        inspection_names = cursor.fetchall()
        for name, count in inspection_names:
            print(f"Inspeção: '{name}' - {count} RNCs")
        
        # Analisar nomes únicos de engenharia
        print("\n=== NOMES DE ENGENHARIA ÚNICOS ===")
        cursor.execute('''
            SELECT signature_engineering_name, COUNT(*) as count
            FROM rncs 
            WHERE signature_engineering_name IS NOT NULL 
              AND signature_engineering_name != ''
            GROUP BY signature_engineering_name
            ORDER BY count DESC
        ''')
        engineering_names = cursor.fetchall()
        for name, count in engineering_names:
            print(f"Engenharia: '{name}' - {count} RNCs")
        
        # Analisar nomes únicos de inspeção2
        print("\n=== NOMES DE INSPEÇÃO2 ÚNICOS ===")
        cursor.execute('''
            SELECT signature_inspection2_name, COUNT(*) as count
            FROM rncs 
            WHERE signature_inspection2_name IS NOT NULL 
              AND signature_inspection2_name != ''
            GROUP BY signature_inspection2_name
            ORDER BY count DESC
        ''')
        inspection2_names = cursor.fetchall()
        for name, count in inspection2_names:
            print(f"Inspeção2: '{name}' - {count} RNCs")
        
        # Coletar todos os nomes únicos
        all_names = set()
        for name, _ in inspection_names:
            if name and name.strip():
                all_names.add(name.strip())
        for name, _ in engineering_names:
            if name and name.strip():
                all_names.add(name.strip())
        for name, _ in inspection2_names:
            if name and name.strip():
                all_names.add(name.strip())
        
        print(f"\n=== TODOS OS NOMES ÚNICOS ENCONTRADOS ({len(all_names)}) ===")
        for name in sorted(all_names):
            print(f"  - '{name}'")
        
        # Estatísticas gerais
        cursor.execute('SELECT COUNT(*) FROM rncs')
        total_rncs = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM rncs 
            WHERE signature_inspection_name IS NOT NULL AND signature_inspection_name != ''
        ''')
        rncs_with_inspection = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM rncs 
            WHERE signature_engineering_name IS NOT NULL AND signature_engineering_name != ''
        ''')
        rncs_with_engineering = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM rncs 
            WHERE signature_inspection2_name IS NOT NULL AND signature_inspection2_name != ''
        ''')
        rncs_with_inspection2 = cursor.fetchone()[0]
        
        print(f"\n=== ESTATÍSTICAS ===")
        print(f"Total de RNCs: {total_rncs}")
        print(f"RNCs com assinatura de inspeção: {rncs_with_inspection} ({rncs_with_inspection/total_rncs*100:.1f}%)")
        print(f"RNCs com assinatura de engenharia: {rncs_with_engineering} ({rncs_with_engineering/total_rncs*100:.1f}%)")
        print(f"RNCs com assinatura de inspeção2: {rncs_with_inspection2} ({rncs_with_inspection2/total_rncs*100:.1f}%)")
        
        conn.close()
        return list(all_names)
        
    except Exception as e:
        print(f"❌ Erro durante a análise: {e}")
        return []

if __name__ == "__main__":
    analyze_signatures()
