#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar clientes dos dados RNC
"""

import sqlite3
import os
import re
from datetime import datetime

# Configuração do banco
DB_PATH = 'database.db'

def create_clients_table():
    """Criar tabela de clientes se não existir"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            contact_info TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def extract_clients_from_rnc_data():
    """Extrair clientes únicos dos dados RNC"""
    clients_set = set()
    
    try:
        with open('DADOS PUXAR RNC/DADOS PUXAR RNC.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            # Pular o cabeçalho
            for line in lines[1:]:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 12:  # Verificar se tem colunas suficientes
                        cliente = parts[11].strip()  # Coluna CLIENTE
                        if cliente and cliente != 'CLIENTE':
                            # Limpar o nome do cliente
                            cliente = re.sub(r'\s+', ' ', cliente).strip()
                            if cliente:
                                clients_set.add(cliente)
                                
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return []
    
    return sorted(list(clients_set))

def insert_clients_to_db(clients):
    """Inserir clientes no banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted_count = 0
    updated_count = 0
    
    for client_name in clients:
        try:
            # Verificar se cliente já existe
            cursor.execute("SELECT id FROM clients WHERE name = ?", (client_name,))
            existing = cursor.fetchone()
            
            if existing:
                # Atualizar cliente existente
                cursor.execute("""
                    UPDATE clients 
                    SET updated_at = CURRENT_TIMESTAMP,
                        active = 1
                    WHERE name = ?
                """, (client_name,))
                updated_count += 1
            else:
                # Inserir novo cliente
                cursor.execute("""
                    INSERT INTO clients (name, description, active, created_at, updated_at)
                    VALUES (?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (client_name, f"Cliente importado dos dados RNC"))
                inserted_count += 1
                
        except sqlite3.IntegrityError:
            print(f"Cliente '{client_name}' já existe no banco")
        except Exception as e:
            print(f"Erro ao inserir cliente '{client_name}': {e}")
    
    conn.commit()
    conn.close()
    
    return inserted_count, updated_count

def main():
    """Função principal"""
    print("🔄 Iniciando importação de clientes...")
    
    # Criar tabela se não existir
    create_clients_table()
    print("✅ Tabela de clientes verificada/criada")
    
    # Extrair clientes dos dados
    print("📊 Extraindo clientes dos dados RNC...")
    clients = extract_clients_from_rnc_data()
    
    if not clients:
        print("❌ Nenhum cliente encontrado nos dados")
        return
    
    print(f"📋 Encontrados {len(clients)} clientes únicos:")
    for i, client in enumerate(clients[:10], 1):
        print(f"   {i}. {client}")
    if len(clients) > 10:
        print(f"   ... e mais {len(clients) - 10} clientes")
    
    # Inserir no banco
    print("\n💾 Inserindo clientes no banco de dados...")
    inserted, updated = insert_clients_to_db(clients)
    
    print(f"\n✅ Importação concluída!")
    print(f"   📝 {inserted} novos clientes inseridos")
    print(f"   🔄 {updated} clientes existentes atualizados")
    print(f"   📊 Total de clientes únicos: {len(clients)}")

if __name__ == "__main__":
    main()