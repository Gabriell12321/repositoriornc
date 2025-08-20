import sqlite3

def check_instruction_fields():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar preenchimento dos campos de instrução
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(instruction_retrabalho) as com_instrucao,
                COUNT(CASE WHEN instruction_retrabalho IS NOT NULL AND instruction_retrabalho != '' THEN 1 END) as instrucao_preenchida
            FROM rncs
            WHERE is_deleted = 0 OR is_deleted IS NULL
        """)
        instruction_stats = cursor.fetchone()
        
        print("Estatísticas de instrução de retrabalho:")
        print(f"- Total de RNCs: {instruction_stats[0]}")
        print(f"- RNCs com campo instrução: {instruction_stats[1]}")
        print(f"- RNCs com instrução preenchida: {instruction_stats[2]} ({instruction_stats[2]/instruction_stats[0]*100:.1f}%)")
        
        # Verificar RNCs de engenharia com instrução
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN r.instruction_retrabalho IS NOT NULL AND r.instruction_retrabalho != '' THEN 1 END) as instrucao_preenchida
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE u.department = 'Engenharia'
              AND (r.is_deleted = 0 OR r.is_deleted IS NULL)
        """)
        eng_instruction_stats = cursor.fetchone()
        
        print("\nEstatísticas de instrução - Engenharia:")
        print(f"- Total de RNCs: {eng_instruction_stats[0]}")
        print(f"- RNCs com instrução preenchida: {eng_instruction_stats[1]} ({eng_instruction_stats[1]/eng_instruction_stats[0]*100:.1f}%)")
        
        # Verificar amostra de instruções
        cursor.execute("""
            SELECT r.rnc_number, r.instruction_retrabalho
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE u.department = 'Engenharia'
              AND (r.is_deleted = 0 OR r.is_deleted IS NULL)
              AND (r.instruction_retrabalho IS NOT NULL AND r.instruction_retrabalho != '')
            LIMIT 3
        """)
        samples = cursor.fetchall()
        
        print("\nAmostra de instruções de Engenharia:")
        for rnc_number, instruction in samples:
            print(f"- RNC {rnc_number}: {instruction[:100]}...")
            
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar campos de instrução: {e}")

if __name__ == "__main__":
    check_instruction_fields()