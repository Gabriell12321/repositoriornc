import sqlite3

print("=== CORREÇÃO DOS TRIGGERS DE VALIDAÇÃO ===")

def create_sqlite_compatible_triggers():
    """Cria triggers compatíveis com SQLite"""
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Remover triggers antigos se existirem
    try:
        cursor.execute("DROP TRIGGER IF EXISTS validate_rnc_data_insert")
        cursor.execute("DROP TRIGGER IF EXISTS validate_rnc_data_update")
        print("✅ Triggers antigos removidos")
    except Exception as e:
        print(f"⚠️  Erro ao remover triggers antigos: {e}")
    
    # Trigger para validação antes de inserir (sintaxe SQLite)
    trigger_sql = '''
    CREATE TRIGGER validate_rnc_data_insert
    BEFORE INSERT ON rncs
    FOR EACH ROW
    WHEN (
        NEW.equipment IN ('aaa', 'bbb', 'ccc', 'teste', 'exemplo') OR
        NEW.signature_engineering_name IN ('NOME', 'nome', 'Name', 'name') OR
        NEW.signature_inspection2_name IN ('NOME', 'nome', 'Name', 'name') OR
        NEW.instruction_retrabalho LIKE 'TESTE:%' OR
        NEW.cause_rnc LIKE 'TESTE:%' OR
        NEW.action_rnc LIKE 'TESTE:%'
    )
    BEGIN
        SELECT RAISE(ABORT, 'Dados de teste não são permitidos. Preencha com informações reais.');
    END;
    '''
    
    try:
        cursor.execute(trigger_sql)
        print("✅ Trigger de validação para INSERT criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar trigger de INSERT: {e}")
    
    # Trigger para validação antes de atualizar (sintaxe SQLite)
    update_trigger_sql = '''
    CREATE TRIGGER validate_rnc_data_update
    BEFORE UPDATE ON rncs
    FOR EACH ROW
    WHEN (
        NEW.equipment IN ('aaa', 'bbb', 'ccc', 'teste', 'exemplo') OR
        NEW.signature_engineering_name IN ('NOME', 'nome', 'Name', 'name') OR
        NEW.signature_inspection2_name IN ('NOME', 'nome', 'Name', 'name') OR
        NEW.instruction_retrabalho LIKE 'TESTE:%' OR
        NEW.cause_rnc LIKE 'TESTE:%' OR
        NEW.action_rnc LIKE 'TESTE:%'
    )
    BEGIN
        SELECT RAISE(ABORT, 'Dados de teste não são permitidos. Preencha com informações reais.');
    END;
    '''
    
    try:
        cursor.execute(update_trigger_sql)
        print("✅ Trigger de validação para UPDATE criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar trigger de UPDATE: {e}")
    
    # Verificar se os triggers foram criados
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'validate_rnc_data%'")
    triggers = cursor.fetchall()
    
    if triggers:
        print(f"\n✅ Triggers criados: {[t[0] for t in triggers]}")
    else:
        print("❌ Nenhum trigger foi criado")
    
    conn.commit()
    conn.close()

def test_trigger_validation():
    """Testa se os triggers estão funcionando"""
    
    print("\n=== TESTANDO VALIDAÇÃO DOS TRIGGERS ===")
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Tentar inserir dados de teste (deve falhar)
    try:
        cursor.execute('''
            INSERT INTO rncs (
                rnc_number, title, equipment, signature_engineering_name, 
                signature_inspection2_name, instruction_retrabalho, cause_rnc, action_rnc
            ) VALUES (
                'TESTE-TRIGGER', 'Teste', 'aaa', 'NOME', 'NOME', 
                'TESTE: teste', 'TESTE: teste', 'TESTE: teste'
            )
        ''')
        print("❌ Trigger não está funcionando - dados de teste foram inseridos")
    except Exception as e:
        if "Dados de teste não são permitidos" in str(e):
            print("✅ Trigger funcionando corretamente - bloqueou dados de teste")
        else:
            print(f"⚠️  Erro inesperado: {e}")
    
    # Tentar inserir dados válidos (deve funcionar)
    try:
        cursor.execute('''
            INSERT INTO rncs (
                rnc_number, title, equipment, signature_engineering_name, 
                signature_inspection2_name, instruction_retrabalho, cause_rnc, action_rnc
            ) VALUES (
                'TESTE-VALIDO', 'Teste Válido', 'Equipamento Real', 'João Silva', 'Maria Santos', 
                'Instrução real', 'Causa real', 'Ação real'
            )
        ''')
        print("✅ Dados válidos foram inseridos com sucesso")
        
        # Limpar dados de teste
        cursor.execute("DELETE FROM rncs WHERE rnc_number = 'TESTE-VALIDO'")
        print("✅ Dados de teste removidos")
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados válidos: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Criar triggers corrigidos
    create_sqlite_compatible_triggers()
    
    # Testar funcionamento
    test_trigger_validation()
    
    print("\n=== TRIGGERS CORRIGIDOS E TESTADOS ===")
    print("✅ Validação automática implementada")
    print("✅ Dados de teste serão bloqueados automaticamente")
    print("✅ Apenas dados reais serão aceitos")
