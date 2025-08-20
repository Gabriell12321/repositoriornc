#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar especificamente a criação do unique_signatures na API
"""

import sqlite3

# Configurações
DB_PATH = "ippel_system.db"

def test_unique_signatures():
    """Testar a criação do unique_signatures como na API"""
    print("🔍 Testando criação do unique_signatures como na API...")
    
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
        
        # 3. Criar unique_signatures EXATAMENTE como na API
        unique_signatures = set()
        for owner_id, count in rnc_rows:
            if isinstance(owner_id, str) and owner_id:
                unique_signatures.add(owner_id)  # SEM .strip()
            elif isinstance(owner_id, int):
                # Se for ID, buscar nome do usuário
                cursor.execute("SELECT name FROM users WHERE id = ?", (owner_id,))
                user_result = cursor.fetchone()
                if user_result:
                    unique_signatures.add(user_result[0])
        
        print(f"\n🔍 unique_signatures criado com {len(unique_signatures)} assinaturas")
        
        # 4. Mostrar algumas assinaturas únicas
        print(f"\n📝 Primeiras 20 assinaturas únicas:")
        for i, signature in enumerate(list(unique_signatures)[:20]):
            print(f"   {i+1:2d}. '{signature}'")
        
        # 5. Testar o processamento de cada assinatura
        print(f"\n🧪 Testando processamento de cada assinatura:")
        meta_mensal = 5
        result = []
        
        for signature in sorted(list(unique_signatures)[:20]):  # Primeiras 20 para teste
            rncs = rnc_data.get(signature, 0)
            percentage = (rncs / meta_mensal * 100) if meta_mensal > 0 else 0
            status = 'Acima da Meta' if rncs >= meta_mensal else 'Abaixo da Meta'
            
            print(f"   👤 '{signature}' -> {rncs} RNCs ({percentage}%) - {status}")
            
            result.append({
                'id': signature,
                'name': signature,
                'rncs': rncs,
                'meta': meta_mensal,
                'percentage': round(percentage, 1),
                'status': status,
                'department': 'Engenharia'
            })
        
        # 6. Verificar se há problemas de espaços
        print(f"\n🔍 Verificando problemas de espaços:")
        for signature in list(unique_signatures)[:5]:
            print(f"   Assinatura: '{signature}'")
            print(f"   Length: {len(signature)}")
            print(f"   rnc_data.get('{signature}', 0): {rnc_data.get(signature, 0)}")
            print()
        
        # 7. Verificar se há problemas de case sensitivity
        print(f"\n🔍 Verificando case sensitivity:")
        for signature in list(unique_signatures)[:5]:
            print(f"   Original: '{signature}'")
            print(f"   Lower: '{signature.lower()}'")
            print(f"   Upper: '{signature.upper()}'")
            print()
        
        # 8. Verificar se há problemas de caracteres especiais
        print(f"\n🔍 Verificando caracteres especiais:")
        for signature in list(unique_signatures)[:5]:
            print(f"   Assinatura: '{signature}'")
            print(f"   Bytes: {signature.encode('utf-8')}")
            print(f"   Repr: {repr(signature)}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🚀 Testando criação do unique_signatures como na API...")
    print(f"🗄️ Banco de dados: {DB_PATH}")
    
    test_unique_signatures()
    
    print("\n✨ Teste concluído!")

if __name__ == "__main__":
    main()
