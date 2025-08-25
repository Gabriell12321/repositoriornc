#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar diretamente no banco os dados das assinaturas de engenharia
"""

import sqlite3

# Configurações
DB_PATH = "ippel_system.db"

def check_signatures_data():
    """Verificar dados das assinaturas de engenharia no banco"""
    print("🔍 Verificando dados das assinaturas de engenharia...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Verificar se a coluna signature_engineering_name existe
        cursor.execute("PRAGMA table_info(rncs)")
        cols = {row[1] for row in cursor.fetchall()}
        
        if 'signature_engineering_name' not in cols:
            print("❌ Coluna 'signature_engineering_name' não existe na tabela rncs")
            return
        
        print("✅ Coluna 'signature_engineering_name' existe")
        
        # 2. Verificar quantas RNCs têm assinatura de engenharia preenchida
        cursor.execute("""
            SELECT COUNT(*) as total_rncs,
                   COUNT(CASE WHEN signature_engineering_name IS NOT NULL AND signature_engineering_name != '' THEN 1 END) as with_signature,
                   COUNT(CASE WHEN signature_engineering_name IS NULL OR signature_engineering_name = '' THEN 1 END) as without_signature
            FROM rncs 
            WHERE is_deleted = 0
        """)
        stats = cursor.fetchone()
        print(f"\n📊 Estatísticas das assinaturas:")
        print(f"   Total de RNCs: {stats[0]}")
        print(f"   Com assinatura de engenharia: {stats[1]}")
        print(f"   Sem assinatura de engenharia: {stats[2]}")
        
        # 3. Verificar RNCs finalizadas com assinatura
        cursor.execute("""
            SELECT COUNT(*) as finalized_with_signature
            FROM rncs 
            WHERE status IN ('Finalizado','finalized')
              AND is_deleted = 0
              AND signature_engineering_name IS NOT NULL 
              AND signature_engineering_name != ''
        """)
        finalized_with_signature = cursor.fetchone()[0]
        print(f"   RNCs finalizadas COM assinatura: {finalized_with_signature}")
        
        # 4. Verificar algumas RNCs com assinatura para entender o formato
        cursor.execute("""
            SELECT id, signature_engineering_name, status, created_at
            FROM rncs 
            WHERE signature_engineering_name IS NOT NULL 
              AND signature_engineering_name != ''
              AND is_deleted = 0
            ORDER BY created_at DESC
            LIMIT 10
        """)
        sample_rncs = cursor.fetchall()
        
        print(f"\n📝 Exemplos de RNCs com assinatura de engenharia:")
        for rnc_id, signature, status, created in sample_rncs:
            print(f"   RNC {rnc_id}: '{signature}' - Status: {status} - Criada: {created}")
        
        # 5. Verificar RNCs finalizadas especificamente
        cursor.execute("""
            SELECT id, signature_engineering_name, user_id, status
            FROM rncs 
            WHERE status IN ('Finalizado','finalized')
              AND is_deleted = 0
              AND signature_engineering_name IS NOT NULL 
              AND signature_engineering_name != ''
            ORDER BY created_at DESC
            LIMIT 10
        """)
        finalized_rncs = cursor.fetchall()
        
        print(f"\n✅ RNCs finalizadas COM assinatura de engenharia:")
        for rnc_id, signature, user_id, status in finalized_rncs:
            print(f"   RNC {rnc_id}: '{signature}' - User ID: {user_id} - Status: {status}")
        
        # 6. Verificar se há RNCs com assinatura mas sem user_id
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM rncs 
            WHERE signature_engineering_name IS NOT NULL 
              AND signature_engineering_name != ''
              AND user_id IS NULL
              AND is_deleted = 0
        """)
        rncs_with_signature_no_user = cursor.fetchone()[0]
        print(f"\n⚠️ RNCs com assinatura mas SEM user_id: {rncs_with_signature_no_user}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🚀 Verificando dados das assinaturas de engenharia...")
    print(f"🗄️ Banco de dados: {DB_PATH}")
    
    check_signatures_data()
    
    print("\n✨ Verificação concluída!")

if __name__ == "__main__":
    main()
