#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para cadastrar setores no banco de dados
"""
import sqlite3

# Path do banco de dados
DB_PATH = 'database.db'

# Lista de setores para cadastrar
SETORES = [
    "Engenharia",
    "Cliente",
    "Montagem",
    "Corte",
    "Conformação",
    "Caldeiraria de Carbono",
    "Caldeiraria de Inox",
    "Jato de Granalha",
    "Pintura",
    "Usin. Cilíndrica Convencional",
    "Usin. Cilíndrica CNC",
    "Usinagem Plana",
    "Furação",
    "Célula de Secadores",
    "Balanceamento",
    "Embalagem",
]

def cadastrar_setores():
    """Cadastrar todos os setores no banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe e criar se necessário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cadastrados = 0
        duplicados = 0
        erros = 0
        
        print("🚀 Iniciando cadastro de setores...")
        print("=" * 60)
        
        for nome in SETORES:
            if not nome or nome.strip() == "":
                continue
                
            try:
                cursor.execute('''
                    INSERT INTO sectors (name)
                    VALUES (?)
                ''', (nome.strip(),))
                
                cadastrados += 1
                print(f"✅ {cadastrados:2d}. {nome}")
                
            except sqlite3.IntegrityError:
                duplicados += 1
                print(f"⚠️  {nome:50s} - JÁ EXISTE")
                
            except Exception as e:
                erros += 1
                print(f"❌ {nome:50s} - ERRO: {e}")
        
        conn.commit()
        conn.close()
        
        print("=" * 60)
        print(f"\n📊 RESUMO:")
        print(f"   ✅ Cadastrados com sucesso: {cadastrados}")
        print(f"   ⚠️  Duplicados (ignorados):  {duplicados}")
        print(f"   ❌ Erros:                    {erros}")
        print(f"   📝 Total processado:         {len(SETORES)}")
        print("\n✅ Processo concluído!")
        
        return cadastrados
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        return 0

if __name__ == '__main__':
    cadastrar_setores()
