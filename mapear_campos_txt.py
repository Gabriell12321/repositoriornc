#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mapear todos os campos do arquivo TXT original."""

import sqlite3

def mapear_campos_txt():
    """Mapear campos do arquivo TXT com campos do banco de dados."""
    
    # Campos do arquivo TXT original (baseado no cabecalho)
    campos_txt = [
        'N RNC',            # 0 -> rnc_number
        'DESENHO',          # 1 -> drawing  
        'MP',               # 2 -> mp
        'REVISAO',          # 3 -> revision
        'POS',              # 4 -> position
        'CV',               # 5 -> cv
        'EQUIPAMENTO',      # 6 -> equipment
        'CONJUNTO',         # 7 -> conjunto
        'MODELO',           # 8 -> modelo
        'DESCRICAO DO DESENHO', # 9 -> description_drawing
        'QUANTIDADE',       # 10 -> quantity
        'CLIENTE',          # 11 -> client
        'MATERIAL',         # 12 -> material
        'ORDEM DE COMPRA',  # 13 -> purchase_order
        'RESPONSAVEL',      # 14 -> responsavel
        'INSPETOR',         # 15 -> inspetor
        'DATA EMISSAO',     # 16 -> created_at
        'AREA RESPONSAVEL', # 17 -> area_responsavel
        'SETOR',            # 18 -> setor
        'DESCRICAO DA RNC', # 19 -> description
        'INSTRUCAO PARA RETRABALHO', # 20 -> instruction_retrabalho
        'CAUSA DA RNC',     # 21 -> cause_rnc
        'JUSTIFICATIVA',    # 22 -> justificativa
        'VALOR'             # 23 -> price
    ]
    
    # Verificar quais campos existem no banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(rncs)')
    campos_banco = [row[1] for row in cursor.fetchall()]
    
    print("CAMPOS DO ARQUIVO TXT ORIGINAL:")
    print("=" * 50)
    for i, campo in enumerate(campos_txt):
        print(f"{i:2d}: {campo}")
    
    print("\nCAMPOS NO BANCO DE DADOS:")
    print("=" * 50)
    for campo in sorted(campos_banco):
        print(f"  {campo}")
    
    print("\nMAPEAMENTO TXT -> BANCO:")
    print("=" * 50)
    mapeamento = {
        0: 'rnc_number',
        1: 'drawing',
        2: 'mp', 
        3: 'revision',
        4: 'position',
        5: 'cv',
        6: 'equipment',
        7: 'conjunto',
        8: 'modelo',
        9: 'description_drawing',
        10: 'quantity',
        11: 'client', 
        12: 'material',
        13: 'purchase_order',
        14: 'responsavel',
        15: 'inspetor',
        16: 'created_at',
        17: 'area_responsavel',
        18: 'setor',
        19: 'description',
        20: 'instruction_retrabalho',
        21: 'cause_rnc',
        22: 'justificativa',
        23: 'price'
    }
    
    # Verificar quais campos estão faltando no banco
    campos_faltando = []
    for idx, campo_banco in mapeamento.items():
        if campo_banco not in campos_banco:
            campos_faltando.append((idx, campos_txt[idx], campo_banco))
            print(f"FALTA: {idx:2d} {campos_txt[idx]:25} -> {campo_banco}")
        else:
            print(f"OK:    {idx:2d} {campos_txt[idx]:25} -> {campo_banco}")
    
    if campos_faltando:
        print(f"\nCAMPOS FALTANDO NO BANCO: {len(campos_faltando)}")
        for idx, campo_txt, campo_banco in campos_faltando:
            print(f"  {campo_txt} -> {campo_banco}")
    else:
        print("\nTodos os campos do TXT estao mapeados no banco!")
    
    conn.close()

if __name__ == "__main__":
    mapear_campos_txt()