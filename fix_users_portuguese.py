#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir erros de português nos nomes dos usuários
"""

import sqlite3

DB_PATH = 'ippel_system.db'

# Mapeamento de correções por ID
CORRECTIONS = {
    25: 'Alisson Moisés',
    31: 'André',
    35: 'Aço Korte',
    36: 'Aço corporal',
    37: 'AçoKorte',
    38: 'Açocorte',
    52: 'Cintia das Graças Kosiba',
    56: 'Cláudio Alves',
    57: 'Cláudio Brandão',
    59: 'Cícero Roberto Paz',
    74: 'Edison André Ferreira Diniz',
    92: 'Fundição Campos Gerais',
    93: 'Fusão',
    112: 'Jefferson Luis Gonçalves',
    115: 'José Assis',
    116: 'José Israel',
    117: 'José Josnei Pereira dos Santos',
    118: 'José Valdemir Martins Barbosa',
    120: 'João Felix',
    121: 'João Maria Carneiro',
    122: 'João Vitor Pucci',
    136: 'Luciano José Carneiro Stella',
    163: 'Mário Dolato Neto',
    185: 'Rômulo Emanuel Mainardes',
    203: 'Thiago Oliveira Guimarães',
    220: 'Vinícius',
    221: 'Virgílio'
}

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fazer backup
    print("💾 Fazendo backup da tabela users...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_backup_portuguese_fix AS 
        SELECT * FROM users
    """)
    conn.commit()
    
    print("\n🔧 Aplicando correções...\n")
    
    for user_id, correct_name in CORRECTIONS.items():
        # Buscar nome atual
        cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        if result:
            old_name = result[0]
            cursor.execute("UPDATE users SET name = ? WHERE id = ?", (correct_name, user_id))
            print(f"  ✏️  ID {user_id:3d}: '{old_name}' → '{correct_name}'")
        else:
            print(f"  ⚠️  ID {user_id:3d}: Usuário não encontrado")
    
    conn.commit()
    
    print(f"\n✅ Total de correções aplicadas: {len(CORRECTIONS)}")
    print(f"💾 Backup salvo em: users_backup_portuguese_fix")
    
    # Verificar se ainda há erros
    print("\n🔍 Verificando se ainda há erros...")
    cursor.execute("SELECT id, name FROM users WHERE name LIKE '%�%' OR name LIKE '%Ã%'")
    remaining_errors = cursor.fetchall()
    
    if remaining_errors:
        print(f"⚠️  Ainda há {len(remaining_errors)} usuários com erros:")
        for user_id, name in remaining_errors:
            print(f"  ID {user_id:3d}: {name}")
    else:
        print("✅ Todos os erros foram corrigidos!")
    
    conn.close()

if __name__ == '__main__':
    main()
