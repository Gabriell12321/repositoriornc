#!/usr/bin/env python3
"""Atualizar dados existentes com ÁREA RESPONSÁVEL do arquivo original."""

import sqlite3
import csv

def atualizar_area_responsavel():
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Ler arquivo original
    arquivo_path = 'DADOS PUXAR RNC/DADOS PUXAR RNC.txt'
    
    print("📋 ATUALIZANDO ÁREA RESPONSÁVEL...")
    print("=" * 50)
    
    updates_count = 0
    
    try:
        with open(arquivo_path, 'r', encoding='latin-1') as file:
            # Pular cabeçalho
            next(file)
            
            for linha_num, linha in enumerate(file, 2):
                try:
                    campos = linha.strip().split('\t')
                    
                    if len(campos) >= 19:  # Garantir que tem área responsável
                        rnc_number = f"RNC-{campos[0].strip()}"
                        area_responsavel = campos[17].strip()  # Coluna 18 (índice 17)
                        setor = campos[18].strip()  # Coluna 19 (índice 18)
                        
                        # Atualizar no banco
                        cursor.execute("""
                            UPDATE rncs 
                            SET area_responsavel = ?, setor = ? 
                            WHERE rnc_number = ?
                        """, (area_responsavel, setor, rnc_number))
                        
                        if cursor.rowcount > 0:
                            updates_count += 1
                            if updates_count <= 5:  # Mostrar apenas os primeiros 5
                                print(f"✅ {rnc_number}: Área='{area_responsavel}', Setor='{setor}'")
                            elif updates_count == 6:
                                print("...")
                                
                except Exception as e:
                    print(f"❌ Erro na linha {linha_num}: {e}")
                    continue
    
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return
    
    conn.commit()
    conn.close()
    
    print(f"\n🎯 RESULTADO: {updates_count} RNCs atualizadas com área responsável!")

if __name__ == "__main__":
    atualizar_area_responsavel()