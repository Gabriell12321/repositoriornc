import sqlite3
import queue
import threading
import time
import os
import logging

logger = logging.getLogger('ippel.services.db')

DB_PATH = 'ippel_system.db'

# Global connection pool
_db_pool_size = 150
_db_pool: 'queue.Queue[sqlite3.Connection]' = queue.Queue(maxsize=_db_pool_size)
_pool_lock = threading.Lock()


def _new_connection() -> sqlite3.Connection:
    # Aumentando timeout e adicionando configurações robustas para lidar com locks
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=60.0)
    # Performance pragmas
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=10000')
    conn.execute('PRAGMA temp_store=MEMORY')
    conn.execute('PRAGMA mmap_size=268435456')
    # Timeout maior para operações - evita erros de locked
    conn.execute('PRAGMA busy_timeout=30000')  # 30 segundos de espera
    return conn


def warm_pool(size: int = _db_pool_size) -> None:
    """Pré-aquece pool de conexões de forma otimizada."""
    with _pool_lock:
        try:
            current = _db_pool.qsize()
        except Exception:
            current = 0
        
        # Limitar a um máximo razoável para inicialização rápida
        target = min(size, min(_db_pool_size, 10))  # Máximo 10 conexões iniciais
        needed = max(0, target - current)
        
        if needed == 0:
            return
            
        created = 0
        for i in range(needed):
            try:
                conn = _new_connection()
                _db_pool.put_nowait(conn)
                created += 1
            except Exception as e:
                print(f"⚠️ Erro ao criar conexão {i+1}: {e}")
                break
        
        if created > 0:
            print(f"✅ Pool aquecido: {created} conexões criadas")


def get_db_connection() -> sqlite3.Connection:
    try:
        return _db_pool.get_nowait()
    except queue.Empty:
        return _new_connection()


def return_db_connection(conn: sqlite3.Connection) -> None:
    try:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
            _db_pool.put_nowait(conn)
    except queue.Full:
        try:
            conn.close()
        except Exception:
            pass
