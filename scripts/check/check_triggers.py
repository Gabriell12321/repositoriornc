import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

print("=== VERIFICANDO TRIGGERS CRIADOS ===")

# Verificar triggers existentes
cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'validate_rnc_data%'")
triggers = cursor.fetchall()

if triggers:
    print(f"✅ Triggers encontrados: {[t[0] for t in triggers]}")
    
    # Mostrar detalhes de cada trigger
    for trigger in triggers:
        trigger_name = trigger[0]
        print(f"\n--- Trigger: {trigger_name} ---")
        
        # Verificar se está funcionando tentando inserir dados de teste
        try:
            cursor.execute('''
                INSERT INTO rncs (
                    rnc_number, title, equipment, signature_engineering_name, 
                    signature_inspection2_name, instruction_retrabalho, cause_rnc, action_rnc
                ) VALUES (
                    'TESTE-TRIGGER-2', 'Teste', 'aaa', 'NOME', 'NOME', 
                    'TESTE: teste', 'TESTE: teste', 'TESTE: teste'
                )
            ''')
            print(f"❌ {trigger_name} não está funcionando")
            
            # Limpar dados inseridos incorretamente
            cursor.execute("DELETE FROM rncs WHERE rnc_number = 'TESTE-TRIGGER-2'")
            
        except Exception as e:
            if "Dados de teste não são permitidos" in str(e):
                print(f"✅ {trigger_name} funcionando corretamente")
            else:
                print(f"⚠️  Erro inesperado em {trigger_name}: {e}")
else:
    print("❌ Nenhum trigger de validação encontrado")

conn.close()
