import sqlite3

def check_cause_action_fields():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar preenchimento dos campos de causa e a\u00e7\u00e3o
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(cause_rnc) as com_causa,
                COUNT(action_rnc) as com_acao,
                COUNT(CASE WHEN cause_rnc IS NOT NULL AND cause_rnc != '' THEN 1 END) as causa_preenchida,
                COUNT(CASE WHEN action_rnc IS NOT NULL AND action_rnc != '' THEN 1 END) as acao_preenchida
            FROM rncs
            WHERE is_deleted = 0 OR is_deleted IS NULL
        """)
        stats = cursor.fetchone()
        
        print("Estat\u00edsticas de preenchimento de causa e a\u00e7\u00e3o:")
        print(f"- Total de RNCs: {stats[0]}")
        print(f"- RNCs com campo causa: {stats[1]}")
        print(f"- RNCs com campo a\u00e7\u00e3o: {stats[2]}")
        print(f"- RNCs com causa preenchida: {stats[3]} ({stats[3]/stats[0]*100:.1f}%)")
        print(f"- RNCs com a\u00e7\u00e3o preenchida: {stats[4]} ({stats[4]/stats[0]*100:.1f}%)")
        
        # Verificar RNCs de engenharia com causa e a\u00e7\u00e3o
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN r.cause_rnc IS NOT NULL AND r.cause_rnc != '' THEN 1 END) as causa_preenchida,
                COUNT(CASE WHEN r.action_rnc IS NOT NULL AND r.action_rnc != '' THEN 1 END) as acao_preenchida
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE u.department = 'Engenharia'
              AND (r.is_deleted = 0 OR r.is_deleted IS NULL)
        """)
        eng_stats = cursor.fetchone()
        
        print("\nEstat\u00edsticas de Engenharia:")
        print(f"- Total de RNCs: {eng_stats[0]}")
        print(f"- RNCs com causa preenchida: {eng_stats[1]} ({eng_stats[1]/eng_stats[0]*100:.1f}%)")
        print(f"- RNCs com a\u00e7\u00e3o preenchida: {eng_stats[2]} ({eng_stats[2]/eng_stats[0]*100:.1f}%)")
        
        # Verificar amostra de causas e a\u00e7\u00f5es
        cursor.execute("""
            SELECT r.rnc_number, r.cause_rnc, r.action_rnc
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE u.department = 'Engenharia'
              AND (r.is_deleted = 0 OR r.is_deleted IS NULL)
              AND (r.cause_rnc IS NOT NULL AND r.cause_rnc != '')
              AND (r.action_rnc IS NOT NULL AND r.action_rnc != '')
            LIMIT 5
        """)
        samples = cursor.fetchall()
        
        print("\nAmostra de causas e a\u00e7\u00f5es de Engenharia:")
        for rnc_number, cause, action in samples:
            print(f"- RNC {rnc_number}:")
            print(f"  Causa: {cause[:100]}...")
            print(f"  A\u00e7\u00e3o: {action[:100]}...")
            print()
            
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar campos de causa e a\u00e7\u00e3o: {e}")

if __name__ == "__main__":
    check_cause_action_fields()