import sqlite3

print("=== SIMULAÇÃO DA FUNÇÃO VIEW_RNC ===")

# Simular exatamente a função view_rnc
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Query exata da função view_rnc
cursor.execute('''
    SELECT r.*,
           u.name as user_name,
           au.name as assigned_user_name,
           u.department as user_department,
           au.department as assigned_user_department
    FROM rncs r
    LEFT JOIN users u ON r.user_id = u.id
    LEFT JOIN users au ON r.assigned_user_id = au.id
    WHERE r.id = (SELECT id FROM rncs WHERE rnc_number = 'RNC-2025-08-28-104553')
''')
rnc_data = cursor.fetchone()

if rnc_data:
    # Obter colunas da tabela
    cursor.execute('PRAGMA table_info(rncs)')
    base_columns = [row[1] for row in cursor.fetchall()]
    
    # Mapear colunas exatamente como na função view_rnc
    columns = base_columns + ['user_name', 'assigned_user_name', 'user_department', 'assigned_user_department']
    
    # Ajustar tamanho dos dados se necessário
    if len(rnc_data) < len(columns):
        rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))
    
    # Criar dicionário
    rnc_dict = dict(zip(columns, rnc_data))
    
    print(f"✅ Dados carregados: {len(rnc_data)} campos, {len(columns)} colunas")
    
    # Verificar campos específicos
    print("\n=== VERIFICAÇÃO DOS CAMPOS ===")
    print(f"instruction_retrabalho: '{rnc_dict.get('instruction_retrabalho')}'")
    print(f"cause_rnc: '{rnc_dict.get('cause_rnc')}'")
    print(f"action_rnc: '{rnc_dict.get('action_rnc')}'")
    
    # Verificar se os campos existem no dicionário
    print(f"\n=== VERIFICAÇÃO DE EXISTÊNCIA ===")
    print(f"'instruction_retrabalho' in rnc_dict: {'instruction_retrabalho' in rnc_dict}")
    print(f"'cause_rnc' in rnc_dict: {'cause_rnc' in rnc_dict}")
    print(f"'action_rnc' in rnc_dict: {'action_rnc' in rnc_dict}")
    
    # Verificar valores booleanos
    print(f"\n=== VERIFICAÇÃO DE VALORES BOOLEANOS ===")
    print(f"rnc_dict.get('instruction_retrabalho') is not None: {rnc_dict.get('instruction_retrabalho') is not None}")
    print(f"rnc_dict.get('cause_rnc') is not None: {rnc_dict.get('cause_rnc') is not None}")
    print(f"rnc_dict.get('action_rnc') is not None: {rnc_dict.get('action_rnc') is not None}")
    
    # Verificar valores vazios
    print(f"\n=== VERIFICAÇÃO DE VALORES VAZIOS ===")
    print(f"rnc_dict.get('instruction_retrabalho') != '': {rnc_dict.get('instruction_retrabalho') != ''}")
    print(f"rnc_dict.get('cause_rnc') != '': {rnc_dict.get('cause_rnc') != ''}")
    print(f"rnc_dict.get('action_rnc') != '': {rnc_dict.get('action_rnc') != ''}")
    
    # Simular a lógica do template
    print(f"\n=== SIMULAÇÃO DO TEMPLATE ===")
    
    # Instrução
    if rnc_dict.get('instruction_retrabalho'):
        print(f"✅ Instrução (rnc.instruction_retrabalho): {rnc_dict.get('instruction_retrabalho')}")
    else:
        print(f"❌ Instrução não encontrada em rnc.instruction_retrabalho")
    
    # Causa
    if rnc_dict.get('cause_rnc'):
        print(f"✅ Causa (rnc.cause_rnc): {rnc_dict.get('cause_rnc')}")
    else:
        print(f"❌ Causa não encontrada em rnc.cause_rnc")
    
    # Ação
    if rnc_dict.get('action_rnc'):
        print(f"✅ Ação (rnc.action_rnc): {rnc_dict.get('action_rnc')}")
    else:
        print(f"❌ Ação não encontrada em rnc.action_rnc")
    
    # Verificar se há algum problema com valores None ou vazios
    print(f"\n=== VERIFICAÇÃO DE PROBLEMAS ===")
    for field in ['instruction_retrabalho', 'cause_rnc', 'action_rnc']:
        value = rnc_dict.get(field)
        print(f"{field}:")
        print(f"  Tipo: {type(value)}")
        print(f"  Valor: '{value}'")
        print(f"  É None: {value is None}")
        print(f"  É string vazia: {value == ''}")
        print(f"  É truthy: {bool(value)}")
        print()

else:
    print("❌ RNC não encontrada")

conn.close()
