#!/usr/bin/env python3
import sqlite3

def add_department_column():
    """Adicionar coluna department à tabela rncs"""
    print("=== ADICIONANDO COLUNA DEPARTMENT À TABELA RNCS ===\n")
    
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(rncs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'department' in columns:
            print("✅ Coluna 'department' já existe na tabela rncs")
        else:
            print("⚠️  Coluna 'department' não existe. Adicionando...")
            
            # Adicionar coluna department
            cursor.execute("ALTER TABLE rncs ADD COLUMN department TEXT DEFAULT ''")
            
            print("✅ Coluna 'department' adicionada com sucesso!")
            
            # Verificar se foi adicionada
            cursor.execute("PRAGMA table_info(rncs)")
            new_columns = [col[1] for col in cursor.fetchall()]
            print(f"📋 Colunas atuais: {new_columns}")
            
            # Atualizar RNCs existentes com base no departamento do usuário criador
            print("\n🔄 Atualizando RNCs existentes com departamento do usuário...")
            cursor.execute("""
                UPDATE rncs 
                SET department = (
                    SELECT users.department 
                    FROM users 
                    WHERE users.id = rncs.user_id
                ) 
                WHERE department = '' OR department IS NULL
            """)
            
            updated_rows = cursor.rowcount
            print(f"✅ {updated_rows} RNCs atualizados com departamento")
            
            # Verificar alguns exemplos
            print("\n📊 Exemplos de RNCs com departamento:")
            cursor.execute("SELECT id, title, department, user_id FROM rncs WHERE department != '' ORDER BY id DESC LIMIT 5")
            examples = cursor.fetchall()
            for rnc_id, title, dept, user_id in examples:
                print(f"   RNC {rnc_id}: {title[:30]}... -> {dept} (User: {user_id})")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    add_department_column()
