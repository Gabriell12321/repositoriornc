#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificar se as atualizacoes funcionaram."""

import sqlite3

def verificar_dados():
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Verificar total de RNCs
    total = cursor.execute('SELECT COUNT(*) FROM rncs').fetchone()[0]
    print(f"Total de RNCs: {total}")
    
    # Verificar RNCs com area responsavel
    com_area = cursor.execute('SELECT COUNT(*) FROM rncs WHERE area_responsavel IS NOT NULL AND area_responsavel != ""').fetchone()[0]
    print(f"RNCs com area responsavel: {com_area}")
    
    # Mostrar alguns exemplos
    exemplos = cursor.execute("""
        SELECT rnc_number, area_responsavel, setor, responsavel 
        FROM rncs 
        WHERE area_responsavel IS NOT NULL AND area_responsavel != ""
        LIMIT 5
    """).fetchall()
    
    print("\nEXEMPLOS:")
    print("=" * 60)
    for rnc in exemplos:
        print(f"RNC: {rnc[0]}")
        print(f"  Area Responsavel: {rnc[1]}")
        print(f"  Setor: {rnc[2]}")
        print(f"  Responsavel: {rnc[3]}")
        print("-" * 40)
    
    conn.close()

if __name__ == "__main__":
    verificar_dados()