import sqlite3

def check_disposition_fields():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar preenchimento dos campos de disposição
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN disposition_usar = 1 THEN 1 END) as usar,
                COUNT(CASE WHEN disposition_retrabalhar = 1 THEN 1 END) as retrabalhar,
                COUNT(CASE WHEN disposition_rejeitar = 1 THEN 1 END) as rejeitar,
                COUNT(CASE WHEN disposition_sucata = 1 THEN 1 END) as sucata,
                COUNT(CASE WHEN disposition_devolver_estoque = 1 THEN 1 END) as devolver_estoque,
                COUNT(CASE WHEN disposition_devolver_fornecedor = 1 THEN 1 END) as devolver_fornecedor
            FROM rncs
            WHERE is_deleted = 0 OR is_deleted IS NULL
        """)
        disposition_stats = cursor.fetchone()
        
        print("Estatísticas de disposição:")
        print(f"- Total de RNCs: {disposition_stats[0]}")
        print(f"- Usar: {disposition_stats[1]} ({disposition_stats[1]/disposition_stats[0]*100:.1f}%)")
        print(f"- Retrabalhar: {disposition_stats[2]} ({disposition_stats[2]/disposition_stats[0]*100:.1f}%)")
        print(f"- Rejeitar: {disposition_stats[3]} ({disposition_stats[3]/disposition_stats[0]*100:.1f}%)")
        print(f"- Sucata: {disposition_stats[4]} ({disposition_stats[4]/disposition_stats[0]*100:.1f}%)")
        print(f"- Devolver estoque: {disposition_stats[5]} ({disposition_stats[5]/disposition_stats[0]*100:.1f}%)")
        print(f"- Devolver fornecedor: {disposition_stats[6]} ({disposition_stats[6]/disposition_stats[0]*100:.1f}%)")
        
        # Verificar RNCs de engenharia por disposição
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN r.disposition_usar = 1 THEN 1 END) as usar,
                COUNT(CASE WHEN r.disposition_retrabalhar = 1 THEN 1 END) as retrabalhar,
                COUNT(CASE WHEN r.disposition_rejeitar = 1 THEN 1 END) as rejeitar,
                COUNT(CASE WHEN r.disposition_sucata = 1 THEN 1 END) as sucata,
                COUNT(CASE WHEN r.disposition_devolver_estoque = 1 THEN 1 END) as devolver_estoque,
                COUNT(CASE WHEN r.disposition_devolver_fornecedor = 1 THEN 1 END) as devolver_fornecedor
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE u.department = 'Engenharia'
              AND (r.is_deleted = 0 OR r.is_deleted IS NULL)
        """)
        eng_disposition_stats = cursor.fetchone()
        
        print("\nEstatísticas de disposição - Engenharia:")
        print(f"- Total de RNCs: {eng_disposition_stats[0]}")
        print(f"- Usar: {eng_disposition_stats[1]} ({eng_disposition_stats[1]/eng_disposition_stats[0]*100:.1f}%)")
        print(f"- Retrabalhar: {eng_disposition_stats[2]} ({eng_disposition_stats[2]/eng_disposition_stats[0]*100:.1f}%)")
        print(f"- Rejeitar: {eng_disposition_stats[3]} ({eng_disposition_stats[3]/eng_disposition_stats[0]*100:.1f}%)")
        print(f"- Sucata: {eng_disposition_stats[4]} ({eng_disposition_stats[4]/eng_disposition_stats[0]*100:.1f}%)")
        print(f"- Devolver estoque: {eng_disposition_stats[5]} ({eng_disposition_stats[5]/eng_disposition_stats[0]*100:.1f}%)")
        print(f"- Devolver fornecedor: {eng_disposition_stats[6]} ({eng_disposition_stats[6]/eng_disposition_stats[0]*100:.1f}%)")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar campos de disposição: {e}")

if __name__ == "__main__":
    check_disposition_fields()