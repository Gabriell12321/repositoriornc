#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_field_locks_database():
    """Verifica o que está salvo no banco de dados"""
    
    # Caminho do banco
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ippel_system.db')
    
    print(f"🔍 Verificando banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela field_locks existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='field_locks'
        """)
        
        if not cursor.fetchone():
            print("❌ Tabela 'field_locks' não existe!")
            conn.close()
            return
        
        print("✅ Tabela 'field_locks' existe")
        
        # Verificar grupos
        cursor.execute("SELECT id, name FROM groups")
        groups = cursor.fetchall()
        print(f"\n📋 Grupos encontrados: {len(groups)}")
        for group_id, name in groups:
            print(f"   - {group_id}: {name}")
        
        # Verificar bloqueios salvos
        cursor.execute("""
            SELECT g.name, fl.field_name, fl.is_locked, fl.updated_at
            FROM field_locks fl
            JOIN groups g ON g.id = fl.group_id
            ORDER BY g.name, fl.field_name
        """)
        
        locks = cursor.fetchall()
        print(f"\n🔒 Bloqueios salvos: {len(locks)}")
        
        if locks:
            current_group = None
            for group_name, field_name, is_locked, updated_at in locks:
                if group_name != current_group:
                    print(f"\n📁 Grupo '{group_name}':")
                    current_group = group_name
                
                status = "🔒 BLOQUEADO" if is_locked else "🔓 LIBERADO"
                print(f"   {field_name}: {status} (atualizado: {updated_at})")
        else:
            print("   ⚠️ Nenhum bloqueio encontrado no banco!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")

if __name__ == "__main__":
    check_field_locks_database()