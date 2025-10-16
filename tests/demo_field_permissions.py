import sqlite3
import json

def demo_field_permissions():
    """Demonstração do sistema de permissões de campos"""
    db_path = 'ippel_system.db'
    
    print("🎭 DEMONSTRAÇÃO - Sistema de Permissões de Campos RNC")
    print("="*70)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar grupos existentes
        print("1️⃣ Grupos disponíveis:")
        cursor.execute("SELECT id, name, description FROM groups ORDER BY name")
        groups = cursor.fetchall()
        
        for group_id, name, desc in groups:
            print(f"   • {name} (ID: {group_id}) - {desc or 'Sem descrição'}")
        
        if not groups:
            print("   ❌ Nenhum grupo encontrado!")
            return
        
        # 2. Configurar exemplo de bloqueios
        print(f"\n2️⃣ Configurando bloqueios de exemplo...")
        
        # Exemplo: Bloquear campos financeiros para grupo 'teste'
        test_group_id = groups[0][0]  # Primeiro grupo
        
        financial_fields = ['price', 'purchase_order']
        sensitive_fields = ['assigned_user_id', 'responsavel']
        
        print(f"   Bloqueando campos financeiros para grupo {groups[0][1]}:")
        for field in financial_fields:
            cursor.execute("""
                INSERT INTO field_locks (group_id, field_name, is_locked)
                VALUES (?, ?, 1)
                ON CONFLICT(group_id, field_name) 
                DO UPDATE SET is_locked = 1, updated_at = CURRENT_TIMESTAMP
            """, (test_group_id, field))
            print(f"     🔒 {field}")
        
        print(f"   Bloqueando campos sensíveis:")
        for field in sensitive_fields:
            cursor.execute("""
                INSERT INTO field_locks (group_id, field_name, is_locked)
                VALUES (?, ?, 1)
                ON CONFLICT(group_id, field_name) 
                DO UPDATE SET is_locked = 1, updated_at = CURRENT_TIMESTAMP
            """, (test_group_id, field))
            print(f"     🔒 {field}")
        
        conn.commit()
        
        # 3. Mostrar configuração atual
        print(f"\n3️⃣ Configuração atual do grupo '{groups[0][1]}':")
        cursor.execute("""
            SELECT field_name, is_locked, is_required
            FROM field_locks
            WHERE group_id = ?
            ORDER BY is_locked DESC, field_name
        """, (test_group_id,))
        
        configs = cursor.fetchall()
        locked_count = 0
        unlocked_count = 0
        
        print("   📋 Campos bloqueados:")
        for field_name, is_locked, is_required in configs:
            if is_locked:
                req_marker = "⭐" if is_required else ""
                print(f"     🔒 {field_name} {req_marker}")
                locked_count += 1
        
        print("   📋 Campos liberados:")
        for field_name, is_locked, is_required in configs:
            if not is_locked:
                req_marker = "⭐" if is_required else ""
                print(f"     🔓 {field_name} {req_marker}")
                unlocked_count += 1
        
        print(f"\n   📊 Resumo: {locked_count} bloqueados, {unlocked_count} liberados")
        
        # 4. Simular verificação de usuário
        print(f"\n4️⃣ Simulando verificação para usuário do grupo '{groups[0][1]}':")
        
        # Buscar usuários do grupo
        cursor.execute("SELECT id, username FROM users WHERE group_id = ? LIMIT 1", (test_group_id,))
        user = cursor.fetchone()
        
        if user:
            user_id, username = user
            print(f"   👤 Usuário: {username} (ID: {user_id})")
            
            # Buscar campos bloqueados
            cursor.execute("""
                SELECT field_name FROM field_locks 
                WHERE group_id = ? AND is_locked = 1
            """, (test_group_id,))
            
            locked_fields = [row[0] for row in cursor.fetchall()]
            print(f"   🚫 Campos bloqueados para este usuário: {len(locked_fields)}")
            
            for field in locked_fields:
                print(f"     • {field}")
                
        else:
            print("   ⚠️ Nenhum usuário encontrado neste grupo")
        
        # 5. Demonstrar API calls
        print(f"\n5️⃣ Exemplos de consultas API:")
        
        # Simular chamada da API
        cursor.execute("""
            SELECT field_name, is_locked 
            FROM field_locks 
            WHERE group_id = ?
        """, (test_group_id,))
        
        api_response = {}
        for field_name, is_locked in cursor.fetchall():
            api_response[field_name] = {
                'is_locked': bool(is_locked),
                'field_label': field_name.replace('_', ' ').title()
            }
        
        print("   📡 GET /admin/field-locks/api/locks/1")
        print(f"   Response: {json.dumps(api_response, indent=2)[:200]}...")
        
        # 6. Estatísticas
        print(f"\n6️⃣ Estatísticas do sistema:")
        
        cursor.execute("SELECT COUNT(*) FROM field_locks WHERE is_locked = 1")
        total_locks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT group_id) FROM field_locks")
        configured_groups = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT field_name) FROM field_locks")
        configured_fields = cursor.fetchone()[0]
        
        print(f"   📊 Total de bloqueios ativos: {total_locks}")
        print(f"   👥 Grupos configurados: {configured_groups}")
        print(f"   📝 Campos configurados: {configured_fields}")
        
        # 7. Cenários de uso
        print(f"\n7️⃣ Cenários de uso demonstrados:")
        scenarios = [
            "🏢 Grupo 'Operadores' não pode alterar preços ou ordens de compra",
            "👥 Grupo 'Técnicos' não pode alterar responsáveis ou usuários atribuídos",
            "📊 Campos obrigatórios (título, descrição) sempre liberados",
            "🔄 Configurações podem ser alteradas dinamicamente pelo admin",
            "🚫 Validação automática no backend e frontend",
            "📱 Interface amigável para administração"
        ]
        
        for scenario in scenarios:
            print(f"   {scenario}")
        
        conn.close()
        
        print(f"\n✅ Demonstração concluída!")
        print(f"🌐 Acesse: http://localhost:5000/admin/field-locks/ para gerenciar")
        
    except sqlite3.Error as e:
        print(f"❌ Erro de banco: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def simulate_form_validation():
    """Simula validação de formulário com permissões"""
    print("\n" + "="*70)
    print("🧪 SIMULAÇÃO - Validação de Formulário")
    print("="*70)
    
    # Dados de exemplo de um formulário RNC
    form_examples = [
        {
            "name": "Formulário Válido (Operador)",
            "data": {
                "title": "Problema na máquina X",
                "description": "Descrição do problema",
                "equipment": "Máquina X",
                "client": "Cliente A"
                # Não inclui campos financeiros
            },
            "expected": "✅ APROVADO"
        },
        {
            "name": "Formulário Inválido (Operador tentando alterar preço)",
            "data": {
                "title": "Problema na máquina Y", 
                "description": "Descrição do problema",
                "equipment": "Máquina Y",
                "price": "1000.00",  # Campo bloqueado!
                "purchase_order": "PO-123"  # Campo bloqueado!
            },
            "expected": "❌ REJEITADO - Campos não permitidos: price, purchase_order"
        },
        {
            "name": "Formulário Parcial (apenas campos liberados)",
            "data": {
                "title": "Problema menor",
                "description": "Descrição simples",
                "priority": "baixa"
            },
            "expected": "✅ APROVADO"
        }
    ]
    
    # Simular campos bloqueados para grupo de exemplo
    blocked_fields = ['price', 'purchase_order', 'assigned_user_id', 'responsavel']
    
    for i, example in enumerate(form_examples, 1):
        print(f"\n{i}. {example['name']}:")
        print(f"   Dados enviados: {list(example['data'].keys())}")
        
        # Verificar se há campos bloqueados
        violations = []
        for field_name, value in example['data'].items():
            if field_name in blocked_fields and value:
                violations.append(field_name)
        
        if violations:
            print(f"   🚫 Violações: {violations}")
            print(f"   Resultado: ❌ REJEITADO")
        else:
            print(f"   ✅ Nenhuma violação encontrada")
            print(f"   Resultado: ✅ APROVADO")
        
        print(f"   Esperado: {example['expected']}")

def show_admin_interface_preview():
    """Mostra preview da interface de administração"""
    print("\n" + "="*70)
    print("🖥️ PREVIEW - Interface de Administração")
    print("="*70)
    
    interface_preview = """
    ┌─────────────────────────────────────────────────────────────────┐
    │  🔐 Gerenciamento de Permissões de Campos RNC                  │
    │  Configure quais campos cada grupo pode editar na criação      │
    └─────────────────────────────────────────────────────────────────┘
    
    📊 Estatísticas:  [1 Grupos]  [24 Campos]  [4 Bloqueios]
    
    ┌───────────────┐  ┌─────────────────────────────────────────────┐
    │ 👥 GRUPOS     │  │ 📝 CONFIGURAÇÃO DE CAMPOS                   │
    │               │  │                                             │
    │ • teste ◄     │  │ 🔍 Buscar campo...                          │
    │   Sem descr.  │  │                                             │
    │               │  │ 💾 Salvar   🔓 Liberar   🔒 Bloquear       │
    │               │  │                                             │
    │               │  │ ┌─────────────────┐ ┌─────────────────┐     │
    │               │  │ │ 📝 Título       │ │ 📝 Descrição    │     │
    │               │  │ │ 🔓 Liberado     │ │ 🔓 Liberado     │     │
    │               │  │ │ Toggle: [ OFF ] │ │ Toggle: [ OFF ] │     │
    │               │  │ └─────────────────┘ └─────────────────┘     │
    │               │  │                                             │
    │               │  │ ┌─────────────────┐ ┌─────────────────┐     │
    │               │  │ │ 💰 Preço        │ │ 📋 Ordem Compra │     │
    │               │  │ │ 🔒 Bloqueado    │ │ 🔒 Bloqueado    │     │
    │               │  │ │ Toggle: [ ON  ] │ │ Toggle: [ ON  ] │     │
    │               │  │ └─────────────────┘ └─────────────────┘     │
    └───────────────┘  └─────────────────────────────────────────────┘
    """
    
    print(interface_preview)
    
    print("\n🎯 Recursos da Interface:")
    features = [
        "✨ Interface visual intuitiva com toggles",
        "🔍 Busca em tempo real de grupos e campos", 
        "📊 Estatísticas em tempo real",
        "💾 Salvamento em lote de alterações",
        "🔄 Ações rápidas (liberar/bloquear tudo)",
        "🗑️ Reset completo de grupo",
        "📱 Design responsivo para mobile",
        "⚠️ Avisos visuais para campos bloqueados"
    ]
    
    for feature in features:
        print(f"   {feature}")

if __name__ == "__main__":
    demo_field_permissions()
    simulate_form_validation()
    show_admin_interface_preview()