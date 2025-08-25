import sqlite3

try:
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Verificar se existem RNCs com dados nos campos
    cursor.execute("""
        SELECT id, rnc_number, title, instruction_retrabalho, cause_rnc, action_rnc 
        FROM rncs 
        WHERE instruction_retrabalho IS NOT NULL 
           OR cause_rnc IS NOT NULL 
           OR action_rnc IS NOT NULL
        LIMIT 5
    """)
    
    rncs_with_data = cursor.fetchall()
    
    if rncs_with_data:
        print("✅ RNCs com dados nos campos:")
        for rnc in rncs_with_data:
            print(f"  ID: {rnc[0]}, RNC: {rnc[1]}, Título: {rnc[2]}")
            print(f"     Instrução: {rnc[3] or 'N/A'}")
            print(f"     Causa: {rnc[4] or 'N/A'}")
            print(f"     Ação: {rnc[5] or 'N/A'}")
            print()
    else:
        print("❌ Nenhuma RNC encontrada com dados nesses campos")
    
    # Verificar todas as RNCs
    cursor.execute("SELECT id, rnc_number, title FROM rncs LIMIT 10")
    all_rncs = cursor.fetchall()
    
    if all_rncs:
        print(f"📊 Total de RNCs no sistema: {len(all_rncs)}")
        print("Primeiras RNCs:")
        for rnc in all_rncs:
            print(f"  ID: {rnc[0]}, RNC: {rnc[1]}, Título: {rnc[2]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
