import sqlite3

# Conectar ao banco
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Criar alguns grupos de exemplo para testar
grupos_exemplo = [
    ('Administradores', 'Acesso completo ao sistema'),
    ('Gerentes', 'Gerentes de área com permissões elevadas'),
    ('Supervisores', 'Supervisores de setor'),
    ('Operadores', 'Operadores de produção'),
    ('Qualidade', 'Equipe de controle de qualidade'),
    ('Engenharia', 'Equipe de engenharia')
]

# Inserir grupos (ignorar se já existir)
for nome, descricao in grupos_exemplo:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO groups (name, description, created_at)
            VALUES (?, ?, datetime('now'))
        """, (nome, descricao))
        print(f"Grupo '{nome}' inserido/verificado")
    except Exception as e:
        print(f"Erro ao inserir grupo '{nome}': {e}")

conn.commit()

# Verificar grupos inseridos
cursor.execute("SELECT id, name, description FROM groups ORDER BY name")
grupos = cursor.fetchall()

print("\nGrupos no banco:")
for grupo in grupos:
    print(f"  ID: {grupo[0]}, Nome: {grupo[1]}, Descrição: {grupo[2]}")

conn.close()