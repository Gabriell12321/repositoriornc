#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar diretamente a query SQL da API
"""

import sqlite3

# Configurações
DB_PATH = "ippel_system.db"

def test_direct_query():
    """Testar a query SQL diretamente no banco"""
    print("🔍 Testando query SQL diretamente no banco...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Query exata que está sendo usada na API
        base_query = """
            SELECT 
                CASE 
                    WHEN r.signature_engineering_name IS NOT NULL AND r.signature_engineering_name != '' 
                    THEN r.signature_engineering_name
                    ELSE r.user_id
                END as owner_id,
                COUNT(r.id) as rnc_count
            FROM rncs r
            WHERE r.status IN ('Finalizado','finalized')
              AND r.is_deleted = 0
            GROUP BY owner_id
            ORDER BY rnc_count DESC
        """
        
        print("🔍 Executando query:")
        print(base_query)
        
        cursor.execute(base_query)
        rnc_rows = cursor.fetchall()
        
        print(f"\n📊 Resultados da query:")
        print(f"   Total de linhas retornadas: {len(rnc_rows)}")
        
        # Mostrar as primeiras 20 linhas
        print(f"\n📋 Primeiras 20 linhas:")
        for i, (owner_id, count) in enumerate(rnc_rows[:20]):
            print(f"   {i+1:2d}. Owner ID: '{owner_id}' - RNCs: {count}")
        
        # Verificar se há owner_id NULL ou vazio
        null_owners = [row for row in rnc_rows if row[0] is None or row[0] == '']
        if null_owners:
            print(f"\n⚠️ Encontrados {len(null_owners)} owner_id NULL ou vazios")
        
        # Verificar se há owner_id com números (user_id)
        numeric_owners = [row for row in rnc_rows if isinstance(row[0], int)]
        if numeric_owners:
            print(f"\n🔢 Encontrados {len(numeric_owners)} owner_id numéricos (user_id)")
            print("   Exemplos:")
            for owner_id, count in numeric_owners[:5]:
                print(f"      User ID {owner_id}: {count} RNCs")
        
        # Verificar se há owner_id com strings (assinaturas)
        string_owners = [row for row in rnc_rows if isinstance(row[0], str) and row[0].strip()]
        if string_owners:
            print(f"\n📝 Encontrados {len(string_owners)} owner_id com strings (assinaturas)")
            print("   Exemplos:")
            for owner_id, count in string_owners[:10]:
                print(f"      '{owner_id}': {count} RNCs")
        
        # Verificar se a query está retornando dados corretos
        total_rncs_from_query = sum(row[1] for row in rnc_rows)
        print(f"\n📊 Total de RNCs retornadas pela query: {total_rncs_from_query}")
        
        # Verificar total real de RNCs finalizadas
        cursor.execute("""
            SELECT COUNT(*) FROM rncs 
            WHERE status IN ('Finalizado','finalized') AND is_deleted = 0
        """)
        total_real = cursor.fetchone()[0]
        print(f"📊 Total real de RNCs finalizadas: {total_real}")
        
        if total_rncs_from_query == total_real:
            print("✅ Query está retornando o número correto de RNCs!")
        else:
            print(f"❌ Query está retornando {total_rncs_from_query} RNCs, mas deveria retornar {total_real}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao testar query: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🚀 Testando query SQL diretamente no banco...")
    print(f"🗄️ Banco de dados: {DB_PATH}")
    
    test_direct_query()
    
    print("\n✨ Teste concluído!")

if __name__ == "__main__":
    main()
