#!/usr/bin/env python3
"""
Teste direto no banco de dados para verificar dados de engenharia
"""
import sqlite3
from datetime import datetime

def test_engineering_data_direct():
    """Testa diretamente no banco os dados que seriam retornados pela API"""
    
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("🔍 Testando consulta da API de engenharia...")
        
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
        """)
        
        rncs_raw = cursor.fetchall()
        print(f"📊 Total RNCs encontradas: {len(rncs_raw)}")
        
        # Analisar os dados mensais
        monthly_data = {}
        total_value = 0
        count = 0
        
        for rnc in rncs_raw:
            count += 1
            if count > 10:  # Limitar a 10 registros para teste
                print("  ... (limitando output para teste)")
                break
            finalized_at = rnc[10]  # finalized_at
            created_at = rnc[11]    # created_at
            price_str = rnc[12] or "0"  # price
            
            # Converter preço string para float
            try:
                if isinstance(price_str, str):
                    # Remover R$, espaços e vírgulas, substituir vírgula por ponto
                    price_clean = price_str.replace('R$', '').replace(' ', '').replace(',', '.')
                    price = float(price_clean) if price_clean else 0.0
                else:
                    price = float(price_str) if price_str else 0.0
            except (ValueError, TypeError):
                price = 0.0
                
            total_value += price
            
            print(f"RNC {rnc[1]}: responsavel='{rnc[7]}', finalized_at='{finalized_at}', created_at='{created_at}', price={price}")
            
            # Usar finalized_at se disponível, senão usar created_at para RNCs ativas
            date_to_use = finalized_at or created_at
            if date_to_use and date_to_use != 'None':
                try:
                    date = datetime.strptime(date_to_use, '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        date = datetime.strptime(date_to_use.split(' ')[0], '%Y-%m-%d')
                    except:
                        print(f"  ❌ Não conseguiu processar data: '{date_to_use}'")
                        continue
                        
                month_key = date.strftime('%Y-%m')
                month_label = date.strftime('%b/%Y')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'label': month_label, 'count': 0, 'value': 0, 'finalized': 0, 'active': 0}
                
                monthly_data[month_key]['count'] += 1
                monthly_data[month_key]['value'] += price
                
                # Separar entre finalizadas e ativas
                if finalized_at and finalized_at != 'None':
                    monthly_data[month_key]['finalized'] += 1
                else:
                    monthly_data[month_key]['active'] += 1
                    
                print(f"  ✅ Adicionado ao mês {month_key}: total={monthly_data[month_key]['count']}")
        
        print(f"💰 Valor total: R$ {total_value:,.2f}")
        
        # Calcular RNCs finalizadas e ativas baseado nos dados reais
        finalized_count = 0
        active_count = 0
        for rnc in rncs_raw:
            if rnc[10] and rnc[10] != 'None':  # finalized_at
                finalized_count += 1
            else:
                active_count += 1
                
        print(f"✅ RNCs finalizadas: {finalized_count}")
        print(f"🔄 RNCs ativas: {active_count}")
        print(f"📅 Meses com dados: {len(monthly_data)}")
        
        # Mostrar tendência mensal
        sorted_months = sorted(monthly_data.keys())
        print("\n📈 Tendência mensal:")
        accumulated_count = 0
        for month_key in sorted_months:
            data = monthly_data[month_key]
            accumulated_count += data['count']
            print(f"  {month_key} ({data['label']}): {data['count']} RNCs (acum: {accumulated_count})")
        
        conn.close()
        
        # Estrutura que seria retornada pela API
        api_result = {
            'success': True,
            'stats': {
                'total_rncs': len(rncs_raw),
                'finalized_rncs': finalized_count,
                'total_value': total_value,
                'avg_value': total_value / max(len(rncs_raw), 1)
            },
            'monthly_trend': [
                {
                    'month': month_key,
                    'label': monthly_data[month_key]['label'],
                    'count': monthly_data[month_key]['count'],
                    'value': monthly_data[month_key]['value']
                }
                for month_key in sorted_months
            ],
            'rncs_count': len(rncs_raw)
        }
        
        print(f"\n🎯 API retornaria {len(api_result['monthly_trend'])} meses de dados")
        print(f"🎯 Estatísticas: {api_result['stats']}")
        
        if api_result['monthly_trend']:
            print("✅ DADOS VÁLIDOS PARA GRÁFICOS!")
        else:
            print("❌ SEM DADOS PARA GRÁFICOS")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_engineering_data_direct()