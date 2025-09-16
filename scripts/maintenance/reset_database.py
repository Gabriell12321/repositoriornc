import sqlite3
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('reset_database')

DB_PATH = 'ippel_system.db'

def reset_database_locks():
    """Libera locks do banco de dados e faz checkpoint completo do WAL"""
    logger.info("Iniciando reset do banco de dados")
    
    try:
        # Tentar abrir conexão exclusiva
        logger.info("Tentando obter acesso exclusivo ao banco...")
        connection = sqlite3.connect(DB_PATH, timeout=120.0)  # 2 minutos timeout
        cursor = connection.cursor()
        
        # Verificar status atual
        logger.info("Verificando status atual do banco:")
        cursor.execute("PRAGMA journal_mode;")
        journal_mode = cursor.fetchone()[0]
        logger.info(f"Journal mode: {journal_mode}")
        
        # Forçar checkpoint completo
        logger.info("Forçando checkpoint completo do WAL...")
        cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        checkpoint_result = cursor.fetchone()
        logger.info(f"Resultado do checkpoint: {checkpoint_result}")
        
        # Listar tabelas para verificar acesso
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
        table_count = cursor.fetchone()[0]
        logger.info(f"Número de tabelas: {table_count}")
        
        # Realizar vacuum para otimizar
        logger.info("Executando VACUUM para compactar banco...")
        cursor.execute("VACUUM;")
        
        # Forçar commit
        connection.commit()
        connection.close()
        
        logger.info("Reset concluído com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro durante reset: {e}")
        return False

def close_connections_to_database():
    """
    Não é possível fechar conexões de outros processos diretamente em Python,
    mas podemos verificar se o banco está acessível para operações de escrita.
    """
    logger.info("Testando se o banco está disponível para escrita...")
    
    try:
        # Tentar uma inserção e exclusão em uma tabela temporária
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        # Criar tabela temporária
        cursor.execute("CREATE TABLE IF NOT EXISTS _temp_test_table (id INTEGER PRIMARY KEY, timestamp TEXT);")
        
        # Inserir e excluir um registro
        cursor.execute("INSERT INTO _temp_test_table (timestamp) VALUES (datetime('now'));")
        test_id = cursor.lastrowid
        cursor.execute("DELETE FROM _temp_test_table WHERE id = ?", (test_id,))
        
        # Confirmar
        conn.commit()
        
        # Remover tabela temporária
        cursor.execute("DROP TABLE IF EXISTS _temp_test_table;")
        conn.commit()
        conn.close()
        
        logger.info("Banco disponível para operações de escrita!")
        return True
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            logger.error("O banco ainda está bloqueado por outros processos.")
            return False
        else:
            logger.error(f"Erro operacional: {e}")
            return False
    except Exception as e:
        logger.error(f"Erro ao testar escrita: {e}")
        return False

def create_indexes():
    """Cria índices para melhorar performance, especialmente no compartilhamento"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        # Índice para busca de compartilhamentos por usuário
        logger.info("Criando índice para rnc_shares...")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_rnc_shares_user_rnc ON rnc_shares(shared_with_user_id, rnc_id);"
        )
        
        # Outros índices úteis
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_rncs_status ON rncs(status);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_rncs_user ON rncs(user_id);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_rncs_assigned ON rncs(assigned_user_id);"
        )
        
        conn.commit()
        conn.close()
        logger.info("Índices criados com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar índices: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== MANUTENÇÃO COMPLETA DO BANCO DE DADOS ===")
    
    # Testar acesso
    if close_connections_to_database():
        # Reset
        if reset_database_locks():
            # Criar índices
            create_indexes()
            logger.info("Manutenção completa finalizada com sucesso!")
        else:
            logger.error("Falha no reset do banco.")
    else:
        logger.error("Banco ainda bloqueado, não foi possível continuar.")
