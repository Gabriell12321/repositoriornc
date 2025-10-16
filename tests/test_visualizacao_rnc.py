#!/usr/bin/env python3
"""Testar se a visualização da RNC está exibindo todos os dados do TXT."""

import sqlite3

def test_rnc_data():
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Pegar uma RNC específica para teste
    cursor.execute("""
        SELECT 
            id, rnc_number, responsavel, setor, inspetor, material, quantity, drawing,
            equipment, client, price, instruction_retrabalho, cause_rnc, action_rnc,
            description, title, created_at,
            signature_inspection_name, signature_engineering_name, signature_inspection2_name,
            disposition_usar, disposition_retrabalhar, disposition_rejeitar, 
            disposition_sucata, disposition_devolver_estoque, disposition_devolver_fornecedor,
            inspection_aprovado, inspection_reprovado, inspection_ver_rnc
        FROM rncs 
        WHERE id = 1  -- RNC-30264
    """)
    
    rnc = cursor.fetchone()
    
    if rnc:
        print("🔍 DADOS DA RNC PARA VISUALIZAÇÃO:")
        print("=" * 50)
        print(f"📝 ID: {rnc[0]}")
        print(f"📋 Número: {rnc[1]}")
        print(f"👤 Responsável: {rnc[2]}")
        print(f"🏢 Setor: {rnc[3] or 'N/A'}")
        print(f"🔍 Inspetor: {rnc[4]}")
        print(f"📦 Material: {rnc[5] or 'N/A'}")
        print(f"🔢 Quantidade: {rnc[6]}")
        print(f"📐 Desenho: {rnc[7]}")
        print(f"⚙️ Equipamento: {rnc[8]}")
        print(f"🏭 Cliente: {rnc[9]}")
        print(f"💰 Preço: R$ {rnc[10]:,.2f}" if rnc[10] else "N/A")
        print(f"🔧 Instrução Retrabalho: {rnc[11] or 'N/A'}")
        print(f"⚠️ Causa RNC: {rnc[12] or 'N/A'}")
        print(f"✅ Ação RNC: {rnc[13] or 'N/A'}")
        print(f"📄 Descrição: {rnc[14] or 'N/A'}")
        print(f"📅 Data Criação: {rnc[16]}")
        
        print("\n🔏 ASSINATURAS:")
        print(f"   Inspeção: {rnc[17] or 'N/A'}")
        print(f"   Engenharia: {rnc[18] or 'N/A'}")
        print(f"   Inspeção 2: {rnc[19] or 'N/A'}")
        
        print("\n✅ DISPOSIÇÕES:")
        print(f"   Usar: {'✓' if rnc[20] else '✗'}")
        print(f"   Retrabalhar: {'✓' if rnc[21] else '✗'}")
        print(f"   Rejeitar: {'✓' if rnc[22] else '✗'}")
        print(f"   Sucata: {'✓' if rnc[23] else '✗'}")
        print(f"   Devolver Estoque: {'✓' if rnc[24] else '✗'}")
        print(f"   Devolver Fornecedor: {'✓' if rnc[25] else '✗'}")
        
        print("\n🔍 INSPEÇÕES:")
        print(f"   Aprovado: {'✓' if rnc[26] else '✗'}")
        print(f"   Reprovado: {'✓' if rnc[27] else '✗'}")
        print(f"   Ver RNC: {rnc[28] or 'N/A'}")
        
    else:
        print("❌ RNC não encontrada")
    
    conn.close()

if __name__ == "__main__":
    test_rnc_data()