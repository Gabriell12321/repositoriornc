import sqlite3

def check_equipment_data():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar preenchimento dos campos de equipamento
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(equipment) as com_equipamento,
                COUNT(CASE WHEN equipment IS NOT NULL AND equipment != '' THEN 1 END) as equipamento_preenchido
            FROM rncs
            WHERE is_deleted = 0 OR is_deleted IS NULL
        """)
        equipment_stats = cursor.fetchone()
        
        print("Estatísticas de equipamento:")
        print(f"- Total de RNCs: {equipment_stats[0]}")
        print(f"- RNCs com campo equipamento: {equipment_stats[1]}")
        print(f"- RNCs com equipamento preenchido: {equipment_stats[2]} ({equipment_stats[2]/equipment_stats[0]*100:.1f}%)")
        
        # Verificar RNCs de engenharia com equipamento
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN r.equipment IS NOT NULL AND r.equipment != '' THEN 1 END) as equipamento_preenchido
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE u.department = 'Engenharia'
              AND (r.is_deleted = 0 OR r.is_deleted IS NULL)
        """)
        eng_equipment_stats = cursor.fetchone()
        
        print("\nEstatísticas de equipamento - Engenharia:")
        print(f"- Total de RNCs: {eng_equipment_stats[0]}")
        print(f"- RNCs com equipamento preenchido: {eng_equipment_stats[1]} ({eng_equipment_stats[1]/eng_equipment_stats[0]*100:.1f}%)")
        
        # Verificar equipamentos mais comuns
        cursor.execute("""
            SELECT equipment, COUNT(*) as total
            FROM rncs
            WHERE equipment IS NOT NULL AND equipment != ''
              AND (is_deleted = 0 OR is_deleted IS NULL)
            GROUP BY equipment
            ORDER BY total DESC
            LIMIT 10
        """)
        top_equipment = cursor.fetchall()
        
        print("\nEquipamentos mais comuns:")
        for equipment, count in top_equipment:
            print(f"- {equipment}: {count} RNCs")
            
        # Verificar equipamentos em RNCs de engenharia
        cursor.execute("""
            SELECT equipment, COUNT(*) as total
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE u.department = 'Engenharia'
              AND r.equipment IS NOT NULL AND r.equipment != ''
              AND (r.is_deleted = 0 OR r.is_deleted IS NULL)
            GROUP BY equipment
            ORDER BY total DESC
            LIMIT 10
        """)
        eng_top_equipment = cursor.fetchall()
        
        print("\nEquipamentos mais comuns em Engenharia:")
        for equipment, count in eng_top_equipment:
            print(f"- {equipment}: {count} RNCs")
            
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar dados de equipamento: {e}")

if __name__ == "__main__":
    check_equipment_data()