import pyodbc
import sqlite3

# Conectar ao Access
try:
    access_conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=Lancamento RNC.accdb;'
    access_conn = pyodbc.connect(access_conn_str)
    access_cursor = access_conn.cursor()
    
    # Listar todas as tabelas
    print("📋 TABELAS NO ACCESS:")
    tables = access_cursor.tables(tableType='TABLE')
    for table in tables:
        if not table.table_name.startswith('MSys'):  # Ignorar tabelas do sistema
            print(f"  - {table.table_name}")
    
    # Tentar ler dados da tabela principal
    print("\n🔍 TENTANDO LER DADOS...")
    
    # Procurar tabelas que podem conter RNCs
    access_cursor.execute("SELECT Name FROM MSysObjects WHERE Type=1 AND Flags=0")
    user_tables = [row.Name for row in access_cursor.fetchall() if not row.Name.startswith('~') and not row.Name.startswith('MSys')]
    
    print(f"\nTabelas de usuário encontradas: {len(user_tables)}")
    for table in user_tables[:10]:  # Mostrar primeiras 10
        print(f"  - {table}")
        try:
            access_cursor.execute(f"SELECT TOP 1 * FROM [{table}]")
            row = access_cursor.fetchone()
            if row:
                print(f"    Colunas: {[col[0] for col in access_cursor.description]}")
        except:
            pass
    
    access_conn.close()
    
except Exception as e:
    print(f"❌ Erro ao conectar ao Access: {e}")
    print("\nVerificando se o driver do Access está instalado...")
    print("Drivers disponíveis:")
    for driver in pyodbc.drivers():
        print(f"  - {driver}")
