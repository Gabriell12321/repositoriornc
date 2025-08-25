import sqlite3

def check_rncs_distribution():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar distribuição de RNCs por departamento
        cursor.execute("""
            SELECT u.department, COUNT(*) as total
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE r.is_deleted = 0 OR r.is_deleted IS NULL
            GROUP BY u.department
            ORDER BY total DESC
        """)
        dept_distribution = cursor.fetchall()
        
        print("Distribuição de RNCs por departamento:")
        for dept, count in dept_distribution:
            print(f"- {dept}: {count} RNCs")
            
        # Verificar distribuição de RNCs por status
        cursor.execute("""
            SELECT status, COUNT(*) as total
            FROM rncs
            WHERE is_deleted = 0 OR is_deleted IS NULL
            GROUP BY status
            ORDER BY total DESC
        """)
        status_distribution = cursor.fetchall()
        
        print("\nDistribuição de RNCs por status:")
        for status, count in status_distribution:
            print(f"- {status}: {count} RNCs")
            
        # Verificar distribuição de RNCs por departamento e status
        cursor.execute("""
            SELECT u.department, r.status, COUNT(*) as total
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL)
              AND u.department IS NOT NULL
            GROUP BY u.department, r.status
            ORDER BY u.department, total DESC
        """)
        dept_status_distribution = cursor.fetchall()
        
        print("\nDistribuição de RNCs por departamento e status:")
        current_dept = None
        for dept, status, count in dept_status_distribution:
            if dept != current_dept:
                print(f"\n{dept}:")
                current_dept = dept
            print(f"  - {status}: {count} RNCs")
            
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar distribuição: {e}")

if __name__ == "__main__":
    check_rncs_distribution()