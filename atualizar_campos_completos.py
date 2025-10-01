#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualizar RNCs existentes com todos os campos do TXT."""

import sqlite3

def atualizar_campos_completos():
    """Atualizar todos os RNCs com campos completos do arquivo TXT."""
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Ler arquivo original
    arquivo_path = 'DADOS PUXAR RNC/DADOS PUXAR RNC.txt'
    
    print("Atualizando RNCs com todos os campos do TXT...")
    print("=" * 50)
    
    updates_count = 0
    
    try:
        with open(arquivo_path, 'r', encoding='latin-1') as file:
            # Pular cabecalho
            next(file)
            
            for linha_num, linha in enumerate(file, 2):
                try:
                    campos = linha.strip().split('\t')
                    
                    if len(campos) >= 24:  # Garantir que tem todos os campos
                        rnc_number = f"RNC-{campos[0].strip()}"
                        
                        # Extrair todos os campos
                        dados = {
                            'drawing': campos[1].strip(),
                            'mp': campos[2].strip(),
                            'revision': campos[3].strip(),
                            'position': campos[4].strip(),
                            'cv': campos[5].strip(),
                            'equipment': campos[6].strip(),
                            'conjunto': campos[7].strip(),
                            'modelo': campos[8].strip(),
                            'description_drawing': campos[9].strip(),
                            'quantity': campos[10].strip(),
                            'client': campos[11].strip(),
                            'material': campos[12].strip(),
                            'purchase_order': campos[13].strip(),
                            'responsavel': campos[14].strip(),
                            'inspetor': campos[15].strip(),
                            'area_responsavel': campos[17].strip(),
                            'setor': campos[18].strip(),
                            'description': campos[19].strip(),
                            'instruction_retrabalho': campos[20].strip(),
                            'cause_rnc': campos[21].strip(),
                            'justificativa': campos[22].strip(),
                            'price': campos[23].strip()
                        }
                        
                        # Atualizar no banco
                        cursor.execute("""
                            UPDATE rncs SET 
                                drawing = ?, mp = ?, revision = ?, position = ?, cv = ?,
                                equipment = ?, conjunto = ?, modelo = ?, description_drawing = ?,
                                quantity = ?, client = ?, material = ?, purchase_order = ?,
                                responsavel = ?, inspetor = ?, area_responsavel = ?, setor = ?,
                                description = ?, instruction_retrabalho = ?, cause_rnc = ?,
                                justificativa = ?, price = ?
                            WHERE rnc_number = ?
                        """, (
                            dados['drawing'], dados['mp'], dados['revision'], dados['position'], dados['cv'],
                            dados['equipment'], dados['conjunto'], dados['modelo'], dados['description_drawing'],
                            dados['quantity'], dados['client'], dados['material'], dados['purchase_order'],
                            dados['responsavel'], dados['inspetor'], dados['area_responsavel'], dados['setor'],
                            dados['description'], dados['instruction_retrabalho'], dados['cause_rnc'],
                            dados['justificativa'], dados['price'], rnc_number
                        ))
                        
                        if cursor.rowcount > 0:
                            updates_count += 1
                            if updates_count <= 3:  # Mostrar apenas os primeiros 3
                                print(f"Atualizado {rnc_number}")
                            elif updates_count == 4:
                                print("...")
                                
                except Exception as e:
                    print(f"Erro na linha {linha_num}: {e}")
                    continue
    
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return
    
    conn.commit()
    conn.close()
    
    print(f"\nResultado: {updates_count} RNCs atualizados com dados completos!")

if __name__ == "__main__":
    atualizar_campos_completos()