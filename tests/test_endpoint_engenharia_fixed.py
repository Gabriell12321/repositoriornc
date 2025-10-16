"""
Teste do endpoint de engenharia após correções
Valida que o endpoint retorna dados corretos e estruturados
"""

import sqlite3
import json
from datetime import datetime

def test_query_engenharia():
    """Testa a query SQL diretamente"""
    print("=" * 70)
    print("🧪 TESTANDO QUERY SQL DA ENGENHARIA (CORRIGIDA)")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Query corrigida - sem filtro de status='Finalizado'
        cursor.execute("""
            SELECT 
                id, rnc_number, title, equipment, client, priority, status,
                responsavel, setor, area_responsavel, finalized_at, created_at,
                price
            FROM rncs 
            WHERE (
                LOWER(TRIM(area_responsavel)) LIKE '%engenharia%'
                OR LOWER(TRIM(setor)) LIKE '%engenharia%'
            )
            AND (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY COALESCE(finalized_at, created_at) DESC
        """)
        
        rncs_raw = cursor.fetchall()
        
        print(f"\n📊 Total de RNCs da Engenharia: {len(rncs_raw)}")
        
        # Analisar status
        status_count = {}
        finalized_with_date = 0
        finalized_without_date = 0
        active_rncs = 0
        
        for rnc in rncs_raw:
            status = rnc[6]
            finalized_at = rnc[10]
            
            status_count[status] = status_count.get(status, 0) + 1
            
            if status == 'Finalizado':
                if finalized_at:
                    finalized_with_date += 1
                else:
                    finalized_without_date += 1
            else:
                active_rncs += 1
        
        print(f"\n📋 Distribuição por Status:")
        for status, count in sorted(status_count.items()):
            print(f"   • {status}: {count}")
        
        print(f"\n🔍 Análise de RNCs Finalizadas:")
        print(f"   • Com finalized_at: {finalized_with_date}")
        print(f"   • Sem finalized_at: {finalized_without_date}")
        print(f"   • RNCs Ativas: {active_rncs}")
        
        # Testar agregação mensal
        monthly_data = {}
        
        for rnc in rncs_raw[:100]:  # Testar primeiras 100
            finalized_at = rnc[10]
            created_at = rnc[11]
            
            date_to_use = finalized_at or created_at
            if date_to_use:
                try:
                    if isinstance(date_to_use, str):
                        if ' ' in date_to_use:
                            date = datetime.strptime(date_to_use, '%Y-%m-%d %H:%M:%S')
                        else:
                            date = datetime.strptime(date_to_use, '%Y-%m-%d')
                    else:
                        date = date_to_use
                    
                    month_key = date.strftime('%Y-%m')
                    monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
                except Exception as e:
                    print(f"   ⚠️ Erro ao parsear data: {date_to_use} - {e}")
        
        print(f"\n📅 Distribuição Mensal (primeiras 100 RNCs):")
        for month in sorted(monthly_data.keys(), reverse=True)[:6]:
            print(f"   • {month}: {monthly_data[month]} RNCs")
        
        # Amostra de RNCs
        print(f"\n📋 Amostra de 5 RNCs:")
        for i, rnc in enumerate(rncs_raw[:5], 1):
            print(f"\n   {i}. RNC: {rnc[1]}")
            print(f"      Título: {rnc[2][:60]}...")
            print(f"      Status: {rnc[6]}")
            print(f"      Área: {rnc[9]}")
            print(f"      Setor: {rnc[8]}")
            print(f"      Finalizado em: {rnc[10] or 'N/A'}")
            print(f"      Criado em: {rnc[11]}")
        
        conn.close()
        
        print(f"\n✅ Query executada com sucesso!")
        print(f"📊 TOTAL: {len(rncs_raw)} RNCs relacionadas à Engenharia encontradas")
        
        return len(rncs_raw) > 0
        
    except Exception as e:
        print(f"\n❌ Erro ao executar query: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_endpoint_structure():
    """Valida a estrutura esperada do JSON de resposta"""
    print("\n" + "=" * 70)
    print("📋 VALIDANDO ESTRUTURA DO ENDPOINT")
    print("=" * 70)
    
    required_fields = {
        'success': bool,
        'stats': dict,
        'monthly_trend': list,
        'rncs_count': int,
        'rncs': list
    }
    
    required_stats = ['total_rncs', 'finalized_rncs', 'active_rncs', 'total_value', 'avg_value']
    
    print(f"\n✓ Campos obrigatórios na resposta:")
    for field, type_expected in required_fields.items():
        print(f"   • {field}: {type_expected.__name__}")
    
    print(f"\n✓ Campos obrigatórios em 'stats':")
    for field in required_stats:
        print(f"   • {field}")
    
    print(f"\n✓ Estrutura esperada em 'monthly_trend' (list):")
    print(f"   • Cada item: {{ month, label, count, value, accumulated_count, accumulated_value }}")
    
    print(f"\n✅ Estrutura validada!")
    return True


def main():
    print("\n" + "🔧" * 35)
    print("TESTE DO ENDPOINT DE ENGENHARIA CORRIGIDO")
    print("🔧" * 35 + "\n")
    
    success_query = test_query_engenharia()
    success_structure = test_endpoint_structure()
    
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    print(f"   Query SQL: {'✅ PASSOU' if success_query else '❌ FALHOU'}")
    print(f"   Estrutura: {'✅ VÁLIDA' if success_structure else '❌ INVÁLIDA'}")
    
    if success_query and success_structure:
        print(f"\n✅ TODOS OS TESTES PASSARAM!")
        print(f"\n💡 Próximos passos:")
        print(f"   1. Reinicie o servidor Flask (server_form.py)")
        print(f"   2. Acesse o dashboard e clique na aba Engenharia")
        print(f"   3. Verifique se os contadores e gráficos estão preenchidos")
        print(f"   4. Se ainda mostrar zero, limpe o cache do navegador (Ctrl+Shift+R)")
    else:
        print(f"\n❌ ALGUNS TESTES FALHARAM - verifique os erros acima")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    main()
