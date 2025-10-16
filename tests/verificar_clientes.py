#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar clientes cadastrados no banco
"""

import sqlite3

def verify_clients():
    """Mostra estatísticas e lista de clientes cadastrados"""
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("📋 CADASTRO DE CLIENTES - VERIFICAÇÃO")
    print("=" * 80)
    
    # Total de clientes
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE ativo = 1")
    total = cursor.fetchone()[0]
    
    print(f"\n✅ Total de clientes ativos: {total}")
    
    # Listar todos os clientes em ordem alfabética
    cursor.execute("SELECT id, nome, created_at FROM clientes WHERE ativo = 1 ORDER BY nome")
    clientes = cursor.fetchall()
    
    print(f"\n📝 Lista completa de clientes (A-Z):")
    print("-" * 80)
    
    for i, (id, nome, created_at) in enumerate(clientes, 1):
        data = created_at[:10] if created_at else 'N/A'
        print(f"{i:3d}. {nome:<40} (ID: {id}, Cadastrado: {data})")
    
    # Verificar uso nas RNCs
    cursor.execute("""
        SELECT c.nome, COUNT(r.id) as total_rncs
        FROM clientes c
        LEFT JOIN rncs r ON r.client = c.nome
        WHERE c.ativo = 1
        GROUP BY c.nome
        HAVING total_rncs > 0
        ORDER BY total_rncs DESC
        LIMIT 10
    """)
    top_clients = cursor.fetchall()
    
    if top_clients:
        print(f"\n📊 Top 10 clientes com mais RNCs:")
        print("-" * 80)
        for nome, total in top_clients:
            print(f"  {nome:<40} {total:>5} RNCs")
    
    print("\n" + "=" * 80)
    
    conn.close()

if __name__ == '__main__':
    verify_clients()
