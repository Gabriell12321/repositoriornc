#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adicionar campos faltantes do TXT no banco de dados."""

import sqlite3

def adicionar_campos_faltantes():
    """Adicionar todos os campos faltantes do arquivo TXT."""
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Campos que estao faltando no banco
    campos_novos = [
        ('mp', 'TEXT'),
        ('revision', 'TEXT'),
        ('position', 'TEXT'), 
        ('cv', 'TEXT'),
        ('conjunto', 'TEXT'),
        ('modelo', 'TEXT'),
        ('description_drawing', 'TEXT'),
        ('purchase_order', 'TEXT'),
        ('justificativa', 'TEXT')
    ]
    
    print("Adicionando campos faltantes no banco de dados...")
    print("=" * 50)
    
    for campo, tipo in campos_novos:
        try:
            cursor.execute(f'ALTER TABLE rncs ADD COLUMN {campo} {tipo}')
            print(f"Adicionado: {campo} ({tipo})")
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print(f"Ja existe: {campo}")
            else:
                print(f"Erro em {campo}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\nCampos adicionados com sucesso!")

if __name__ == "__main__":
    adicionar_campos_faltantes()