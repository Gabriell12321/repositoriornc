#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migração do Banco de Dados para Sistema de Notificações
Executa todas as mudanças necessárias no banco de dados SQLite
"""

import sqlite3
import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_path():
    """Obter caminho do banco de dados"""
    # Assumir que o script está na raiz do projeto
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, 'rnc_system.db')
    
    if not os.path.exists(db_path):
        # Tentar outros caminhos possíveis
        alternative_paths = [
            os.path.join(project_root, 'database.db'),
            os.path.join(project_root, 'data', 'rnc_system.db'),
            os.path.join(project_root, 'db', 'rnc_system.db')
        ]
        
        for path in alternative_paths:
            if os.path.exists(path):
                db_path = path
                break
        else:
            logger.error("Banco de dados não encontrado!")
            logger.info("Caminhos verificados:")
            logger.info(f"  - {db_path}")
            for path in alternative_paths:
                logger.info(f"  - {path}")
            sys.exit(1)
    
    return db_path


def backup_database(db_path):
    """Criar backup do banco de dados"""
    try:
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Copiar arquivo
        import shutil
        shutil.copy2(db_path, backup_path)
        
        logger.info(f"Backup criado: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        return None


def check_table_exists(cursor, table_name):
    """Verificar se tabela existe"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    
    return cursor.fetchone() is not None


def check_column_exists(cursor, table_name, column_name):
    """Verificar se coluna existe em uma tabela"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def create_notifications_table(cursor):
    """Criar tabela de notificações"""
    logger.info("Criando tabela 'notifications'...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            to_user_id INTEGER NOT NULL,
            from_user_id INTEGER,
            rnc_id INTEGER,
            data TEXT NOT NULL,
            priority TEXT DEFAULT 'normal',
            channels TEXT NOT NULL,
            group_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            dismissed_at TIMESTAMP,
            clicked_at TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (to_user_id) REFERENCES users (id),
            FOREIGN KEY (from_user_id) REFERENCES users (id),
            FOREIGN KEY (rnc_id) REFERENCES rncs (id)
        )
    """)
    
    logger.info("Tabela 'notifications' criada com sucesso")


def create_notification_stats_table(cursor):
    """Criar tabela de estatísticas de notificações"""
    logger.info("Criando tabela 'notification_stats'...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            notification_type TEXT NOT NULL,
            channel TEXT NOT NULL,
            sent_count INTEGER DEFAULT 0,
            read_count INTEGER DEFAULT 0,
            click_count INTEGER DEFAULT 0,
            UNIQUE(date, notification_type, channel)
        )
    """)
    
    logger.info("Tabela 'notification_stats' criada com sucesso")


def create_notification_preferences_table(cursor):
    """Criar tabela de preferências de notificação"""
    logger.info("Criando tabela 'notification_preferences'...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            notification_type TEXT NOT NULL,
            in_app_enabled BOOLEAN DEFAULT 1,
            email_enabled BOOLEAN DEFAULT 1,
            browser_enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, notification_type)
        )
    """)
    
    logger.info("Tabela 'notification_preferences' criada com sucesso")


def create_indexes(cursor):
    """Criar índices para otimização"""
    logger.info("Criando índices...")
    
    indexes = [
        ("idx_notifications_user", "notifications", "to_user_id"),
        ("idx_notifications_rnc", "notifications", "rnc_id"),
        ("idx_notifications_read", "notifications", "read_at"),
        ("idx_notifications_created", "notifications", "created_at"),
        ("idx_notifications_type", "notifications", "type"),
        ("idx_notification_stats_date", "notification_stats", "date"),
        ("idx_notification_preferences_user", "notification_preferences", "user_id")
    ]
    
    for index_name, table_name, column_name in indexes:
        try:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {index_name} 
                ON {table_name} ({column_name})
            """)
            logger.info(f"Índice {index_name} criado")
        except sqlite3.Error as e:
            logger.warning(f"Erro ao criar índice {index_name}: {e}")


def add_notification_columns_to_users(cursor):
    """Adicionar colunas de configuração de notificação à tabela users"""
    logger.info("Verificando colunas de notificação na tabela 'users'...")
    
    columns_to_add = [
        ("notification_email", "BOOLEAN DEFAULT 1"),
        ("notification_browser", "BOOLEAN DEFAULT 1"),
        ("notification_sound", "BOOLEAN DEFAULT 1"),
        ("last_notification_check", "TIMESTAMP")
    ]
    
    for column_name, column_definition in columns_to_add:
        if not check_column_exists(cursor, 'users', column_name):
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_definition}")
                logger.info(f"Coluna '{column_name}' adicionada à tabela 'users'")
            except sqlite3.Error as e:
                logger.warning(f"Erro ao adicionar coluna {column_name}: {e}")
        else:
            logger.info(f"Coluna '{column_name}' já existe na tabela 'users'")


def insert_default_notification_preferences(cursor):
    """Inserir preferências padrão de notificação para usuários existentes"""
    logger.info("Inserindo preferências padrão de notificação...")
    
    # Buscar usuários existentes
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # Tipos de notificação padrão
    notification_types = [
        'rnc_created',
        'rnc_assigned', 
        'rnc_updated',
        'rnc_commented',
        'rnc_finalized',
        'system_maintenance',
        'user_message',
        'reminder'
    ]
    
    # Inserir preferências padrão para cada usuário e tipo
    for user_id in user_ids:
        for notification_type in notification_types:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO notification_preferences 
                    (user_id, notification_type, in_app_enabled, email_enabled, browser_enabled)
                    VALUES (?, ?, 1, 1, 1)
                """, (user_id, notification_type))
            except sqlite3.Error as e:
                logger.warning(f"Erro ao inserir preferência para usuário {user_id}, tipo {notification_type}: {e}")
    
    logger.info(f"Preferências padrão inseridas para {len(user_ids)} usuários")


def create_triggers(cursor):
    """Criar triggers para automatização"""
    logger.info("Criando triggers...")
    
    # Trigger para atualizar updated_at em notification_preferences
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_notification_preferences_timestamp
        AFTER UPDATE ON notification_preferences
        BEGIN
            UPDATE notification_preferences 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.id;
        END
    """)
    
    # Trigger para atualizar last_notification_check quando usuário lê notificação
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_last_notification_check
        AFTER UPDATE OF read_at ON notifications
        WHEN NEW.read_at IS NOT NULL AND OLD.read_at IS NULL
        BEGIN
            UPDATE users 
            SET last_notification_check = CURRENT_TIMESTAMP 
            WHERE id = NEW.to_user_id;
        END
    """)
    
    logger.info("Triggers criados com sucesso")


def migrate_existing_notifications(cursor):
    """Migrar notificações existentes se houver"""
    logger.info("Verificando notificações existentes para migração...")
    
    # Verificar se existe alguma tabela de notificações antiga
    old_tables = ['user_notifications', 'email_notifications', 'system_notifications']
    
    for table_name in old_tables:
        if check_table_exists(cursor, table_name):
            logger.info(f"Encontrada tabela antiga: {table_name}")
            # Aqui você pode implementar a lógica de migração específica
            # Por exemplo, converter notificações antigas para o novo formato
    
    logger.info("Migração de notificações existentes concluída")


def verify_migration(cursor):
    """Verificar se a migração foi bem-sucedida"""
    logger.info("Verificando migração...")
    
    # Verificar se todas as tabelas foram criadas
    required_tables = ['notifications', 'notification_stats', 'notification_preferences']
    
    for table_name in required_tables:
        if not check_table_exists(cursor, table_name):
            logger.error(f"Erro: Tabela '{table_name}' não foi criada!")
            return False
        else:
            logger.info(f"✓ Tabela '{table_name}' verificada")
    
    # Verificar colunas na tabela users
    required_columns = ['notification_email', 'notification_browser', 'notification_sound', 'last_notification_check']
    
    for column_name in required_columns:
        if not check_column_exists(cursor, 'users', column_name):
            logger.error(f"Erro: Coluna '{column_name}' não foi adicionada à tabela 'users'!")
            return False
        else:
            logger.info(f"✓ Coluna '{column_name}' verificada")
    
    # Verificar contagem de registros
    cursor.execute("SELECT COUNT(*) FROM notifications")
    notification_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM notification_preferences")
    preference_count = cursor.fetchone()[0]
    
    logger.info(f"✓ {notification_count} notificações na tabela")
    logger.info(f"✓ {preference_count} preferências na tabela")
    
    logger.info("Migração verificada com sucesso!")
    return True


def main():
    """Função principal de migração"""
    logger.info("=== Iniciando Migração do Sistema de Notificações ===")
    
    # Obter caminho do banco
    db_path = get_db_path()
    logger.info(f"Banco de dados: {db_path}")
    
    # Criar backup
    backup_path = backup_database(db_path)
    if not backup_path:
        logger.error("Falha ao criar backup. Abortando migração.")
        sys.exit(1)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Executar migração
        logger.info("Executando migração...")
        
        # 1. Criar tabelas
        create_notifications_table(cursor)
        create_notification_stats_table(cursor)
        create_notification_preferences_table(cursor)
        
        # 2. Modificar tabela users
        add_notification_columns_to_users(cursor)
        
        # 3. Criar índices
        create_indexes(cursor)
        
        # 4. Criar triggers
        create_triggers(cursor)
        
        # 5. Inserir dados padrão
        insert_default_notification_preferences(cursor)
        
        # 6. Migrar dados existentes
        migrate_existing_notifications(cursor)
        
        # Commit das mudanças
        conn.commit()
        
        # 7. Verificar migração
        if verify_migration(cursor):
            logger.info("=== Migração Concluída com Sucesso! ===")
            logger.info(f"Backup disponível em: {backup_path}")
        else:
            logger.error("=== Migração Falhou na Verificação ===")
            logger.info("Considere restaurar o backup se necessário")
            sys.exit(1)
        
    except sqlite3.Error as e:
        logger.error(f"Erro de banco de dados: {e}")
        conn.rollback()
        logger.info("Transação revertida")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        conn.rollback()
        logger.info("Transação revertida")
        sys.exit(1)
        
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("Conexão com banco de dados fechada")


if __name__ == "__main__":
    main()