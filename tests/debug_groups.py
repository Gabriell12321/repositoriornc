#!/usr/bin/env python3
import sqlite3

def debug_groups():
    """Debugar estrutura de grupos e departamentos"""
    print("=== DEBUG DE GRUPOS E DEPARTAMENTOS ===\n")
    
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # 1. Verificar se existe tabela groups
        print("1. VERIFICANDO TABELAS:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   Tabelas encontradas: {tables}")
        
        if 'groups' in tables:
            print("\n2. CONTEÚDO DA TABELA GROUPS:")
            cursor.execute("SELECT * FROM groups LIMIT 10")
            groups = cursor.fetchall()
            print(f"   Grupos: {groups}")
        else:
            print("\n2. TABELA GROUPS NÃO ENCONTRADA!")
        
        # 3. Verificar departamentos dos usuários
        print("\n3. DEPARTAMENTOS DOS USUÁRIOS:")
        cursor.execute("SELECT DISTINCT department, COUNT(*) as count FROM users WHERE department IS NOT NULL AND department != '' GROUP BY department ORDER BY department")
        departments = cursor.fetchall()
        print("   Departamentos únicos:")
        for dept, count in departments:
            print(f"     - {dept}: {count} usuários")
        
        # 4. Verificar alguns usuários específicos
        print("\n4. EXEMPLOS DE USUÁRIOS:")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print(f"   Colunas da tabela users: {[col[1] for col in columns]}")
        
        cursor.execute("SELECT id, name, department FROM users WHERE department IS NOT NULL AND department != '' LIMIT 10")
        users = cursor.fetchall()
        for user_id, name, dept in users:
            print(f"   ID {user_id}: {name} -> {dept}")
        
        # 5. Verificar RNCs recentes e seus departamentos
        print("\n5. RNCs RECENTES E DEPARTAMENTOS:")
        cursor.execute("PRAGMA table_info(rncs)")
        rnc_columns = cursor.fetchall()
        print(f"   Colunas da tabela rncs: {[col[1] for col in rnc_columns]}")
        
        # Verificar se a coluna department existe na tabela rncs
        column_names = [col[1] for col in rnc_columns]
        if 'department' in column_names:
            cursor.execute("SELECT id, title, department, user_id FROM rncs ORDER BY id DESC LIMIT 10")
            rncs = cursor.fetchall()
            for rnc_id, title, dept, user_id in rncs:
                print(f"   RNC {rnc_id}: {title[:30]}... -> Depto: '{dept}' (User: {user_id})")
        else:
            print("   COLUNA 'department' NÃO EXISTE NA TABELA RNCS!")
            cursor.execute("SELECT id, title, user_id FROM rncs ORDER BY id DESC LIMIT 5")
            rncs = cursor.fetchall()
            for rnc_id, title, user_id in rncs:
                print(f"   RNC {rnc_id}: {title[:30]}... (User: {user_id})")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    debug_groups()
