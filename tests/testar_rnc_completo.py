#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testar dados completos de um RNC especifico."""

import sqlite3

def testar_rnc_completo():
    """Testar todos os campos de um RNC."""
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Buscar um RNC completo
    cursor.execute("""
        SELECT rnc_number, drawing, mp, revision, position, cv, equipment,
               conjunto, modelo, description_drawing, quantity, client, material,
               purchase_order, responsavel, inspetor, area_responsavel, setor,
               description, instruction_retrabalho, cause_rnc, justificativa, price
        FROM rncs 
        WHERE rnc_number = 'RNC-30264'
    """)
    
    rnc = cursor.fetchone()
    conn.close()
    
    if rnc:
        campos = [
            'RNC Number', 'Drawing', 'MP', 'Revision', 'Position', 'CV', 'Equipment',
            'Conjunto', 'Modelo', 'Description Drawing', 'Quantity', 'Client', 'Material',
            'Purchase Order', 'Responsavel', 'Inspetor', 'Area Responsavel', 'Setor',
            'Description', 'Instruction Retrabalho', 'Cause RNC', 'Justificativa', 'Price'
        ]
        
        print("DADOS COMPLETOS DO RNC-30264:")
        print("=" * 60)
        
        for i, campo in enumerate(campos):
            valor = rnc[i] if rnc[i] else "VAZIO"
            print(f"{campo:25}: {valor}")
        
        # Contar campos preenchidos
        preenchidos = sum(1 for v in rnc if v and str(v).strip())
        total = len(rnc)
        percentual = (preenchidos / total) * 100
        
        print(f"\nESCOPO: {preenchidos}/{total} campos preenchidos ({percentual:.1f}%)")
        
    else:
        print("RNC nao encontrado!")

if __name__ == "__main__":
    testar_rnc_completo()