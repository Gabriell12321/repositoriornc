#!/usr/bin/env python3
"""
Teste rápido para verificar se o valor está aparecendo nas RNCs
"""

import sqlite3
import sys
import os

# Definir o caminho do banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'ippel_system.db')

def test_rnc_with_value():
    """Testa se conseguimos encontrar RNCs com valor"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar RNCs com valor > 0
        cursor.execute('''
            SELECT id, rnc_number, price, title, created_at
            FROM rncs 
            WHERE price > 0 
            ORDER BY created_at DESC 
            LIMIT 5
        ''')
        
        rncs_with_value = cursor.fetchall()
        
        print("=" * 60)
        print("🔍 TESTE: RNCs com Valor > 0")
        print("=" * 60)
        
        if rncs_with_value:
            print(f"✅ Encontradas {len(rncs_with_value)} RNCs com valor:")
            print()
            
            for rnc in rncs_with_value:
                id_rnc, numero, preco, titulo, criado = rnc
                
                # Formatação brasileira do valor
                valor_formatado = f"R$ {preco:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                
                print(f"📋 RNC ID: {id_rnc}")
                print(f"   Número: {numero}")
                print(f"   💰 Valor: {valor_formatado}")
                print(f"   Título: {titulo[:50]}...")
                print(f"   🔗 URL: http://localhost:5000/rnc/{id_rnc}")
                print("-" * 40)
                
        else:
            print("❌ Nenhuma RNC com valor encontrada")
            
        # Verificar total de RNCs
        cursor.execute('SELECT COUNT(*) FROM rncs')
        total = cursor.fetchone()[0]
        
        # Verificar RNCs com valor = 0 ou NULL
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE price IS NULL OR price = 0')
        sem_valor = cursor.fetchone()[0]
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total de RNCs: {total}")
        print(f"   RNCs com valor > 0: {len(rncs_with_value)}")
        print(f"   RNCs sem valor (0 ou NULL): {sem_valor}")
        
        conn.close()
        
        print(f"\n✅ Teste concluído!")
        print(f"   💡 Para verificar se o valor aparece, acesse uma das URLs acima")
        print(f"   🔧 Certifique-se que o servidor Flask está rodando (python server.py)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    test_rnc_with_value()
