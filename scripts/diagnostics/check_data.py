import sqlite3

def check_data():
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Verificar dados de 2014-2015
    cursor.execute("""
        SELECT COUNT(*) 
        FROM rncs 
        WHERE finalized_at IS NOT NULL 
        AND strftime('%Y', finalized_at) IN ('2014', '2015')
    """)
    count_2014_2015 = cursor.fetchone()[0]
    print(f'RNCs finalizados em 2014-2015: {count_2014_2015}')
    
    # Verificar todos os anos
    cursor.execute("""
        SELECT strftime('%Y', finalized_at) as year, COUNT(*) 
        FROM rncs 
        WHERE finalized_at IS NOT NULL 
        GROUP BY year 
        ORDER BY year
    """)
    years = cursor.fetchall()
    print('\nRNCs por ano:')
    for year, count in years:
        print(f'  {year}: {count}')
    
    # Verificar dados mensais de 2014-2015
    cursor.execute("""
        SELECT 
            strftime('%Y', finalized_at) as year,
            strftime('%m', finalized_at) as month,
            COUNT(*) as count
        FROM rncs 
        WHERE finalized_at IS NOT NULL 
        AND strftime('%Y', finalized_at) IN ('2014', '2015')
        GROUP BY year, month
        ORDER BY year, month
    """)
    monthly_data = cursor.fetchall()
    print('\nDados mensais 2014-2015:')
    for year, month, count in monthly_data:
        print(f'  {year}-{month}: {count} RNCs')
    
    # Verificar departamentos em 2014-2015
    cursor.execute("""
        SELECT 
            d.name as department,
            COUNT(*) as count
        FROM rncs r
        JOIN departments d ON r.department_id = d.id
        WHERE r.finalized_at IS NOT NULL 
        AND strftime('%Y', r.finalized_at) IN ('2014', '2015')
        GROUP BY d.name
        ORDER BY count DESC
    """)
    dept_data = cursor.fetchall()
    print('\nDados por departamento 2014-2015:')
    for dept, count in dept_data:
        print(f'  {dept}: {count} RNCs')
    
    conn.close()

if __name__ == "__main__":
    check_data()
