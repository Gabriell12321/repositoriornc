#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a geração de PDFs
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pdf_generation():
    """Testa a geração de PDFs"""
    
    try:
        print("🧪 Testando geração de PDFs...")
        
        # Importar o serviço de PDF
        from services.pdf_generator import pdf_generator
        
        print("✅ Serviço de PDF importado com sucesso!")
        
        # Verificar se o banco existe
        if not os.path.exists('ippel_system.db'):
            print("❌ Banco de dados não encontrado!")
            return
        
        print("✅ Banco de dados encontrado!")
        
        # Testar conexão com o banco
        import sqlite3
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar se há RNCs no banco
        cursor.execute('SELECT id, rnc_number FROM rncs WHERE is_deleted = 0 LIMIT 1')
        rnc = cursor.fetchone()
        conn.close()
        
        if not rnc:
            print("❌ Nenhuma RNC encontrada no banco!")
            return
        
        rnc_id, rnc_number = rnc
        print(f"✅ RNC encontrada: {rnc_number} (ID: {rnc_id})")
        
        # Testar geração de PDF
        print("🔧 Gerando PDF...")
        pdf_path = pdf_generator.generate_pdf(rnc_id)
        
        if pdf_path:
            print(f"✅ PDF gerado com sucesso: {pdf_path}")
            
            # Verificar se o arquivo existe
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"📁 Arquivo criado: {file_size} bytes")
                
                # Limpar arquivo de teste
                os.remove(pdf_path)
                print("🧹 Arquivo de teste removido")
            else:
                print("❌ Arquivo PDF não foi criado")
        else:
            print("❌ Falha ao gerar PDF")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Verifique se as dependências estão instaladas")
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
