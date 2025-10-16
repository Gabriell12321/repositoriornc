import sqlite3
import requests
import json

def debug_dashboard():
    print("🔍 Debugando problema do Dashboard...")
    
    # 1. Verificar banco de dados
    print("\n📊 Verificando banco de dados...")
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ Tabelas encontradas: {[table[0] for table in tables]}")
        
        # Verificar usuários
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        user_count = cursor.fetchone()[0]
        print(f"👥 Usuários ativos: {user_count}")
        
        # Verificar RNCs
        cursor.execute("SELECT COUNT(*) FROM rncs")
        rnc_count = cursor.fetchone()[0]
        print(f"📋 Total de RNCs: {rnc_count}")
        
        # Verificar RNCs por status
        cursor.execute("SELECT is_deleted, finalized_at, COUNT(*) FROM rncs GROUP BY is_deleted, finalized_at")
        status_counts = cursor.fetchall()
        print(f"📊 Status dos RNCs:")
        for status in status_counts:
            is_deleted, finalized_at, count = status
            if is_deleted:
                print(f"  - Deletados: {count}")
            elif finalized_at:
                print(f"  - Finalizados: {count}")
            else:
                print(f"  - Ativos: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
    
    # 2. Verificar servidor
    print("\n🌐 Verificando servidor...")
    try:
        response = requests.get("http://localhost:5001/")
        print(f"✅ Servidor respondendo - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Servidor não está rodando: {e}")
        return
    
    # 3. Testar APIs
    print("\n🔌 Testando APIs...")
    
    # Testar login (se necessário)
    try:
        response = requests.get("http://localhost:5001/api/user/info")
        print(f"📊 API user/info - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Usuário logado: {data.get('user', {}).get('name', 'N/A')}")
        else:
            print(f"⚠️ Usuário não logado ou erro de autenticação")
    except Exception as e:
        print(f"❌ Erro na API user/info: {e}")
    
    # Testar listagem de RNCs
    for tab in ['active', 'finalized', 'deleted']:
        try:
            response = requests.get(f"http://localhost:5001/api/rnc/list?tab={tab}")
            print(f"📋 API rnc/list?tab={tab} - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    rncs = data.get('rncs', [])
                    print(f"  ✅ {len(rncs)} RNCs encontrados")
                else:
                    print(f"  ❌ Erro: {data.get('message', 'Erro desconhecido')}")
            else:
                print(f"  ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    print("\n💡 Sugestões:")
    print("1. Verifique se o servidor está rodando: python server_form.py")
    print("2. Faça login no sistema primeiro")
    print("3. Abra o console do navegador (F12) para ver logs detalhados")
    print("4. Verifique se há dados no banco de dados")

if __name__ == "__main__":
    debug_dashboard() 