#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para debugar o processamento das assinaturas
"""

import sqlite3

# Configurações
DB_PATH = "ippel_system.db"

def debug_processing():
    """Debugar o processamento das assinaturas"""
    print("🔍 Debugando o processamento das assinaturas...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Executar a query exata da API
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
        
        cursor.execute(base_query)
        rnc_rows = cursor.fetchall()
        
        print(f"📊 Query retornou {len(rnc_rows)} linhas")
        
        # 2. Criar rnc_data como na API
        rnc_data = {row[0]: row[1] for row in rnc_rows}
        print(f"📊 rnc_data criado com {len(rnc_data)} chaves")
        
        # 3. Mostrar algumas chaves de rnc_data
        print(f"\n🔑 Primeiras 10 chaves de rnc_data:")
        for i, key in enumerate(list(rnc_data.keys())[:10]):
            print(f"   {i+1:2d}. '{key}' -> {rnc_data[key]} RNCs")
        
        # 4. Criar unique_signatures como na API (SEM .strip())
        unique_signatures = set()
        for owner_id, count in rnc_rows:
            if isinstance(owner_id, str) and owner_id:
                unique_signatures.add(owner_id)  # SEM .strip()
            elif isinstance(owner_id, int):
                cursor.execute("SELECT name FROM users WHERE id = ?", (owner_id,))
                user_result = cursor.fetchone()
                if user_result:
                    unique_signatures.add(user_result[0])
        
        print(f"\n🔍 unique_signatures criado com {len(unique_signatures)} assinaturas")
        
        # 5. Mostrar algumas assinaturas únicas
        print(f"\n📝 Primeiras 10 assinaturas únicas:")
        for i, signature in enumerate(list(unique_signatures)[:10]):
            print(f"   {i+1:2d}. '{signature}'")
        
        # 6. Testar o processamento de cada assinatura
        print(f"\n🧪 Testando processamento de cada assinatura:")
        meta_mensal = 5
        result = []
        
        for signature in sorted(list(unique_signatures)[:10]):  # Primeiras 10 para teste
            rncs = rnc_data.get(signature, 0)
            percentage = (rncs / meta_mensal * 100) if meta_mensal > 0 else 0
            status = 'Acima da Meta' if rncs >= meta_mensal else 'Abaixo da Meta'
            
            print(f"   👤 '{signature}' -> rnc_data.get('{signature}', 0) = {rncs}")
            
            result.append({
                'id': signature,
                'name': signature,
                'rncs': rncs,
                'meta': meta_mensal,
                'percentage': round(percentage, 1),
                'status': status,
                'department': 'Engenharia'
            })
        
        # 7. Verificar se há problemas de espaços
        print(f"\n🔍 Verificando problemas de espaços:")
        for signature in list(unique_signatures)[:5]:
            print(f"   Assinatura: '{signature}'")
            print(f"   Com aspas: '{signature}'")
            print(f"   Length: {len(signature)}")
            print(f"   rnc_data.get('{signature}', 0): {rnc_data.get(signature, 0)}")
            print(f"   rnc_data.get('{signature.strip()}', 0): {rnc_data.get(signature.strip(), 0)}")
            print()
        
        # 8. Verificar se há problemas de case sensitivity
        print(f"\n🔍 Verificando case sensitivity:")
        for signature in list(unique_signatures)[:5]:
            print(f"   Original: '{signature}'")
            print(f"   Lower: '{signature.lower()}'")
            print(f"   Upper: '{signature.upper()}'")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao debugar: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🚀 Debugando processamento das assinaturas...")
    print(f"🗄️ Banco de dados: {DB_PATH}")
    
    debug_processing()
    
    print("\n✨ Debug concluído!")

if __name__ == "__main__":
    main()
