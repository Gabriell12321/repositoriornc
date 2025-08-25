#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import shutil
from datetime import datetime
from werkzeug.security import generate_password_hash

def backup_database():
    """Fazer backup do banco atual se existir"""
    if os.path.exists('ippel_system.db'):
        backup_name = f'ippel_system_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        try:
            shutil.copy2('ippel_system.db', backup_name)
            print(f"✅ Backup criado: {backup_name}")
            return True
        except Exception as e:
            print(f"⚠️ Erro ao criar backup: {e}")
            return False
    return True

def remove_database_files():
    """Remover arquivos do banco de dados"""
    files_to_remove = [
        'ippel_system.db',
        'ippel_system.db-shm',
        'ippel_system.db-wal'
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️ Removido: {file}")
            except Exception as e:
                print(f"⚠️ Erro ao remover {file}: {e}")

def create_database():
    """Criar novo banco de dados"""
    try:
        # Criar conexão
        conn = sqlite3.connect('ippel_system.db', timeout=30.0)
        cursor = conn.cursor()
        
        print("🔧 Criando banco de dados...")
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                department TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                permissions TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabela de RNCs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rncs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rnc_number TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                equipment TEXT,
                client TEXT,
                priority TEXT DEFAULT 'Média',
                status TEXT DEFAULT 'Pendente',
                user_id INTEGER,
                assigned_user_id INTEGER,
                is_deleted BOOLEAN DEFAULT 0,
                deleted_at TIMESTAMP,
                finalized_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                disposition_usar BOOLEAN DEFAULT 0,
                disposition_retrabalhar BOOLEAN DEFAULT 0,
                disposition_rejeitar BOOLEAN DEFAULT 0,
                disposition_sucata BOOLEAN DEFAULT 0,
                disposition_devolver_estoque BOOLEAN DEFAULT 0,
                disposition_devolver_fornecedor BOOLEAN DEFAULT 0,
                inspection_aprovado BOOLEAN DEFAULT 0,
                inspection_reprovado BOOLEAN DEFAULT 0,
                inspection_ver_rnc TEXT,
                signature_inspection_date TEXT,
                signature_engineering_date TEXT,
                signature_inspection2_date TEXT,
                signature_inspection_name TEXT,
                signature_engineering_name TEXT,
                signature_inspection2_name TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (assigned_user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de mensagens do chat
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rnc_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rnc_id) REFERENCES rncs (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de notificações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rnc_id INTEGER,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (rnc_id) REFERENCES rncs (id)
            )
        ''')
        
        # Tabela de mensagens privadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS private_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                recipient_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (recipient_id) REFERENCES users (id)
            )
        ''')
        
        # Criar usuário admin padrão
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, department, role, permissions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Administrador', 'admin@ippel.com.br', admin_password, 'TI', 'admin', '["all"]'))
        
        # Criar usuários de teste
        test_users = [
            ('Elvio Silva', 'elvio@ippel.com.br', 'elvio123', 'Produção', 'user', '["create_rnc"]'),
            ('Maria Santos', 'maria@ippel.com.br', 'maria123', 'Qualidade', 'user', '["create_rnc"]'),
            ('João Costa', 'joao@ippel.com.br', 'joao123', 'Manutenção', 'user', '["create_rnc"]'),
            ('Ana Oliveira', 'ana@ippel.com.br', 'ana123', 'Logística', 'user', '["create_rnc"]')
        ]
        
        for user_data in test_users:
            try:
                user_password = generate_password_hash(user_data[2])
                cursor.execute('''
                    INSERT INTO users (name, email, password_hash, department, role, permissions)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_data[0], user_data[1], user_password, user_data[3], user_data[4], user_data[5]))
                print(f"✅ Usuário criado: {user_data[0]} ({user_data[1]})")
            except sqlite3.IntegrityError:
                # Usuário já existe
                pass
        
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados criado com sucesso!")
        print("✅ Usuário Admin criado:")
        print("   Email: admin@ippel.com.br")
        print("   Senha: admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar banco de dados: {e}")
        return False

def test_database():
    """Testar conexão com o banco de dados"""
    try:
        conn = sqlite3.connect('ippel_system.db', timeout=30.0)
        cursor = conn.cursor()
        
        # Testar consulta simples
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM rncs')
        rnc_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Teste de conexão bem-sucedido!")
        print(f"   Usuários: {user_count}")
        print(f"   RNCs: {rnc_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de conexão: {e}")
        return False

def main():
    print("🔧 Corrigindo banco de dados...")
    print("=" * 50)
    
    # Fazer backup
    backup_database()
    
    # Remover arquivos do banco
    print("\n🗑️ Removendo arquivos do banco...")
    remove_database_files()
    
    # Criar novo banco
    print("\n🔧 Criando novo banco de dados...")
    if create_database():
        # Testar banco
        print("\n🧪 Testando banco de dados...")
        if test_database():
            print("\n✅ Banco de dados corrigido com sucesso!")
            print("🚀 Agora você pode executar o servidor normalmente.")
        else:
            print("\n❌ Falha no teste do banco de dados.")
    else:
        print("\n❌ Falha ao criar banco de dados.")

if __name__ == '__main__':
    main() 