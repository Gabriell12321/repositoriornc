import sqlite3
import os

def test_field_locks_system():
    """Testa o sistema de permissões de campos"""
    db_path = 'ippel_system.db'
    
    print("🧪 Testando Sistema de Permissões de Campos RNC")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar se a tabela existe
        print("1️⃣ Verificando estrutura da tabela...")
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='field_locks'")
        table_exists = cursor.fetchone()[0] > 0
        print(f"   ✅ Tabela field_locks existe: {table_exists}")
        
        if not table_exists:
            print("   ❌ Tabela não encontrada! Execute a migração primeiro.")
            return
        
        # 2. Verificar estrutura da tabela
        print("\n2️⃣ Verificando colunas da tabela...")
        cursor.execute("PRAGMA table_info(field_locks)")
        columns = cursor.fetchall()
        expected_columns = ['id', 'group_id', 'field_name', 'is_locked', 'is_required', 'created_at', 'updated_at']
        
        found_columns = [col[1] for col in columns]
        for col in expected_columns:
            status = "✅" if col in found_columns else "❌"
            print(f"   {status} Coluna: {col}")
        
        # 3. Verificar dados iniciais
        print("\n3️⃣ Verificando dados iniciais...")
        cursor.execute("SELECT COUNT(*) FROM field_locks")
        total_records = cursor.fetchone()[0]
        print(f"   📊 Total de registros: {total_records}")
        
        cursor.execute("SELECT COUNT(DISTINCT group_id) FROM field_locks")
        groups_count = cursor.fetchone()[0]
        print(f"   👥 Grupos configurados: {groups_count}")
        
        cursor.execute("SELECT COUNT(DISTINCT field_name) FROM field_locks")
        fields_count = cursor.fetchone()[0]
        print(f"   📝 Campos configurados: {fields_count}")
        
        # 4. Verificar grupos existentes
        print("\n4️⃣ Listando grupos...")
        cursor.execute("""
            SELECT g.id, g.name, COUNT(fl.id) as config_count
            FROM groups g
            LEFT JOIN field_locks fl ON g.id = fl.group_id
            GROUP BY g.id, g.name
            ORDER BY g.name
        """)
        
        groups = cursor.fetchall()
        for group_id, name, config_count in groups:
            print(f"   • {name} (ID: {group_id}) - {config_count} configurações")
        
        # 5. Verificar campos disponíveis
        print("\n5️⃣ Campos configurados...")
        cursor.execute("""
            SELECT field_name, COUNT(*) as group_count,
                   SUM(is_locked) as locked_count
            FROM field_locks
            GROUP BY field_name
            ORDER BY field_name
        """)
        
        fields = cursor.fetchall()
        print(f"   📋 Total de campos: {len(fields)}")
        
        for field_name, group_count, locked_count in fields[:10]:  # Mostrar apenas os primeiros 10
            print(f"   • {field_name}: {group_count} grupos, {locked_count} bloqueados")
        
        if len(fields) > 10:
            print(f"   ... e mais {len(fields) - 10} campos")
        
        # 6. Testar consulta de exemplo
        print("\n6️⃣ Teste de consulta...")
        if groups:
            test_group_id = groups[0][0]
            cursor.execute("""
                SELECT field_name, is_locked, is_required
                FROM field_locks
                WHERE group_id = ?
                ORDER BY field_name
                LIMIT 5
            """, (test_group_id,))
            
            test_results = cursor.fetchall()
            print(f"   🔍 Testando grupo ID {test_group_id}:")
            for field_name, is_locked, is_required in test_results:
                status = "🔒" if is_locked else "🔓"
                required = "⭐" if is_required else ""
                print(f"     {status} {field_name} {required}")
        
        # 7. Verificar triggers
        print("\n7️⃣ Verificando triggers...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='trigger' AND name LIKE '%field_locks%'
        """)
        triggers = cursor.fetchall()
        for trigger in triggers:
            print(f"   ✅ Trigger: {trigger[0]}")
        
        # 8. Verificar foreign keys
        print("\n8️⃣ Verificando foreign keys...")
        cursor.execute("PRAGMA foreign_key_list(field_locks)")
        fks = cursor.fetchall()
        for fk in fks:
            print(f"   🔗 FK: {fk[2]} -> {fk[3]} ({fk[4]})")
        
        conn.close()
        
        print("\n✅ Teste concluído com sucesso!")
        print(f"💾 Sistema pronto para uso com {total_records} configurações em {groups_count} grupos")
        
    except sqlite3.Error as e:
        print(f"❌ Erro de banco: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def show_sample_api_calls():
    """Mostra exemplos de chamadas da API"""
    print("\n" + "="*60)
    print("📡 EXEMPLOS DE USO DA API")
    print("="*60)
    
    examples = [
        {
            "title": "Listar grupos",
            "method": "GET",
            "url": "/admin/field-locks/api/groups",
            "description": "Retorna todos os grupos disponíveis"
        },
        {
            "title": "Listar campos",
            "method": "GET", 
            "url": "/admin/field-locks/api/fields",
            "description": "Retorna todos os campos configuráveis"
        },
        {
            "title": "Ver bloqueios de um grupo",
            "method": "GET",
            "url": "/admin/field-locks/api/locks/1",
            "description": "Retorna configurações do grupo ID 1"
        },
        {
            "title": "Atualizar bloqueios",
            "method": "POST",
            "url": "/admin/field-locks/api/locks/1",
            "description": "Atualiza configurações do grupo",
            "body": {
                "locks": {
                    "title": False,
                    "description": False,
                    "price": True,
                    "equipment": True
                }
            }
        },
        {
            "title": "Verificar campo específico",
            "method": "GET",
            "url": "/admin/field-locks/api/check/1/title",
            "description": "Verifica se campo 'title' está bloqueado para grupo 1"
        },
        {
            "title": "Resetar grupo",
            "method": "POST",
            "url": "/admin/field-locks/api/locks/1/reset",
            "description": "Remove todos os bloqueios do grupo"
        },
        {
            "title": "Campos bloqueados do usuário",
            "method": "GET",
            "url": "/admin/field-locks/api/user/locked-fields",
            "description": "Retorna campos bloqueados para o usuário logado"
        },
        {
            "title": "Estatísticas",
            "method": "GET",
            "url": "/admin/field-locks/api/stats",
            "description": "Estatísticas do sistema de bloqueios"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print(f"   {example['method']} {example['url']}")
        print(f"   {example['description']}")
        if 'body' in example:
            print(f"   Body: {example['body']}")

def show_integration_examples():
    """Mostra exemplos de integração"""
    print("\n" + "="*60)
    print("🔧 EXEMPLOS DE INTEGRAÇÃO")
    print("="*60)
    
    print("""
1. VERIFICAR SE CAMPO ESTÁ BLOQUEADO (JavaScript):
   
   async function isFieldLocked(fieldName) {
       try {
           const response = await fetch(`/admin/field-locks/api/user/locked-fields`);
           const data = await response.json();
           return data.locked_fields.includes(fieldName);
       } catch (error) {
           console.error('Erro:', error);
           return false;
       }
   }

2. DESABILITAR CAMPOS NO FORMULÁRIO:
   
   async function configureFormFields() {
       const lockedFields = await getUserLockedFields();
       lockedFields.forEach(fieldName => {
           const input = document.querySelector(`[name="${fieldName}"]`);
           if (input) {
               input.disabled = true;
               input.style.backgroundColor = '#f5f5f5';
           }
       });
   }

3. VALIDAÇÃO NO BACKEND (Python):
   
   from routes.field_locks import get_user_locked_fields
   
   def validate_form_submission(user_id, form_data):
       locked_fields = get_user_locked_fields(user_id)
       
       for field_name in locked_fields:
           if field_name in form_data:
               return False, f"Campo '{field_name}' não permitido"
       
       return True, "OK"
""")

if __name__ == "__main__":
    test_field_locks_system()
    show_sample_api_calls()
    show_integration_examples()