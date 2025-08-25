import sqlite3

def check_engineering_details():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar RNCs de engenharia por status
        cursor.execute("""
            SELECT r.status, COUNT(*) as total
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE u.department = 'Engenharia'
              AND (r.is_deleted = 0 OR r.is_deleted IS NULL)
            GROUP BY r.status
            ORDER BY total DESC
        """)
        eng_status = cursor.fetchall()
        
        print("RNCs de Engenharia por status:")
        for status, count in eng_status:
            print(f"- {status}: {count} RNCs")
            
        # Verificar usuários de engenharia
        cursor.execute("""
            SELECT name, COUNT(r.id) as rnc_count
            FROM users u
            LEFT JOIN rncs r ON u.id = r.user_id AND (r.is_deleted = 0 OR r.is_deleted IS NULL)
            WHERE u.department = 'Engenharia'
            GROUP BY u.id, u.name
            ORDER BY rnc_count DESC
        """)
        eng_users = cursor.fetchall()
        
        print("\nUsuários de Engenharia:")
        for name, count in eng_users:
            print(f"- {name}: {count} RNCs")
            
        # Verificar amostra de RNCs de engenharia
        cursor.execute("""
            SELECT r.rnc_number, r.title, r.status, r.created_at
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE u.department = 'Engenharia'
              AND (r.is_deleted = 0 OR r.is_deleted IS NULL)
            ORDER BY r.created_at DESC
            LIMIT 10
        """)
        recent_eng_rncs = cursor.fetchall()
        
        print("\nAmostra de RNCs de Engenharia recentes:")
        for rnc_number, title, status, created_at in recent_eng_rncs:
            print(f"- {rnc_number}: {title[:50]}... ({status}) - {created_at}")
            
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar dados de engenharia: {e}")

if __name__ == "__main__":
    check_engineering_details()