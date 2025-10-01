#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Otimizações de Performance de Banco de Dados - IPPEL RNC
Sistema avançado de otimização de queries, índices e cache
"""

import sqlite3
import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict
import threading
from services.db import DB_PATH, get_db_connection, return_db_connection

logger = logging.getLogger('ippel.performance')

class QueryOptimizer:
    """Otimizador de queries SQL"""
    
    def __init__(self):
        self.query_stats = defaultdict(list)
        self.slow_queries = []
        self.optimization_suggestions = []
        self._lock = threading.Lock()
    
    def log_query(self, query: str, execution_time: float, params: tuple = None):
        """Registra estatísticas de uma query"""
        with self._lock:
            self.query_stats[query].append({
                'execution_time': execution_time,
                'timestamp': datetime.now(),
                'params': params
            })
            
            # Queries lentas (> 100ms)
            if execution_time > 0.1:
                self.slow_queries.append({
                    'query': query,
                    'execution_time': execution_time,
                    'timestamp': datetime.now(),
                    'params': params
                })
                
                # Manter apenas últimas 100 queries lentas
                if len(self.slow_queries) > 100:
                    self.slow_queries = self.slow_queries[-100:]
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de queries"""
        with self._lock:
            stats = {}
            for query, executions in self.query_stats.items():
                times = [e['execution_time'] for e in executions]
                stats[query] = {
                    'count': len(times),
                    'avg_time': sum(times) / len(times),
                    'max_time': max(times),
                    'min_time': min(times),
                    'total_time': sum(times)
                }
            
            return {
                'query_stats': stats,
                'slow_queries': self.slow_queries[-20:],  # Últimas 20 queries lentas
                'total_queries': sum(len(executions) for executions in self.query_stats.values())
            }
    
    def suggest_optimizations(self) -> List[str]:
        """Sugere otimizações baseadas nas estatísticas"""
        suggestions = []
        
        with self._lock:
            # Analisar queries mais frequentes
            for query, executions in self.query_stats.items():
                avg_time = sum(e['execution_time'] for e in executions) / len(executions)
                count = len(executions)
                
                if count > 10 and avg_time > 0.05:  # Query frequente e lenta
                    if 'WHERE' in query.upper() and 'INDEX' not in query.upper():
                        suggestions.append(f"Considere criar índice para query: {query[:100]}...")
                    
                    if 'ORDER BY' in query.upper():
                        suggestions.append(f"Query com ORDER BY pode se beneficiar de índice: {query[:100]}...")
                    
                    if 'JOIN' in query.upper() and count > 50:
                        suggestions.append(f"Query com JOIN frequente: considere otimização: {query[:100]}...")
        
        return suggestions

# Instância global
query_optimizer = QueryOptimizer()

def monitor_query_performance(func):
    """Decorator para monitorar performance de queries"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Extrair query do contexto se possível
            query = kwargs.get('query', str(args[0]) if args else 'unknown')
            params = kwargs.get('params', args[1:] if len(args) > 1 else None)
            
            query_optimizer.log_query(query, execution_time, params)
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            query_optimizer.log_query(str(args[0]) if args else 'error', execution_time)
            raise
    
    return wrapper

class DatabaseOptimizer:
    """Otimizador de banco de dados"""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    def create_optimized_indexes(self):
        """Cria índices otimizados para o sistema"""
        indexes_sql = [
            # Índices para tabela users
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_department ON users(department)",
            "CREATE INDEX IF NOT EXISTS idx_users_group_id ON users(group_id)",
            "CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)",
            
            # Índices para tabela rncs
            "CREATE INDEX IF NOT EXISTS idx_rncs_number ON rncs(rnc_number)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_user_id ON rncs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_assigned_user_id ON rncs(assigned_user_id)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_status ON rncs(status)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_priority ON rncs(priority)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_department ON rncs(department)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_is_deleted ON rncs(is_deleted)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_created_at ON rncs(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_finalized_at ON rncs(finalized_at)",
            
            # Índices compostos para queries complexas
            "CREATE INDEX IF NOT EXISTS idx_rncs_status_deleted ON rncs(status, is_deleted)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_user_status ON rncs(user_id, status, is_deleted)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_dept_status ON rncs(department, status, is_deleted)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_created_status ON rncs(created_at, status, is_deleted)",
            "CREATE INDEX IF NOT EXISTS idx_rncs_finalized_status ON rncs(finalized_at, status, is_deleted)",
            
            # Índices para group_permissions
            "CREATE INDEX IF NOT EXISTS idx_group_permissions_group_id ON group_permissions(group_id)",
            "CREATE INDEX IF NOT EXISTS idx_group_permissions_permission ON group_permissions(permission_name)",
            
            # Índices para rnc_shares
            "CREATE INDEX IF NOT EXISTS idx_rnc_shares_rnc_id ON rnc_shares(rnc_id)",
            "CREATE INDEX IF NOT EXISTS idx_rnc_shares_user_id ON rnc_shares(user_id)",
            
            # Índices para chat_messages
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_rnc_id ON chat_messages(rnc_id)",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp)"
        ]
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            for sql in indexes_sql:
                try:
                    cursor.execute(sql)
                    logger.info(f"Índice criado: {sql}")
                except sqlite3.Error as e:
                    logger.warning(f"Erro ao criar índice: {sql} - {e}")
            
            conn.commit()
            return_db_connection(conn)
            logger.info("Todos os índices foram criados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao criar índices: {e}")
            raise
    
    def analyze_database_performance(self) -> Dict[str, Any]:
        """Analisa performance do banco de dados"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Informações básicas
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            active_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
            active_rncs = cursor.fetchone()[0]
            
            # Estatísticas de tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            table_stats = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_stats[table] = {'count': count}
            
            # Índices existentes
            cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
            indexes = cursor.fetchall()
            
            # Tamanho do banco
            import os
            db_size = os.path.getsize(self.db_path)
            
            return_db_connection(conn)
            
            return {
                'active_users': active_users,
                'active_rncs': active_rncs,
                'table_stats': table_stats,
                'indexes_count': len(indexes),
                'indexes': [{'name': idx[0], 'table': idx[1]} for idx in indexes],
                'database_size_mb': round(db_size / (1024 * 1024), 2),
                'database_file': self.db_path
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de performance: {e}")
            return {'error': str(e)}
    
    def vacuum_database(self):
        """Executa VACUUM para otimizar o banco"""
        try:
            # VACUUM requer conexão isolada
            conn = sqlite3.connect(self.db_path)
            conn.execute("VACUUM")
            conn.close()
            logger.info("VACUUM executado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao executar VACUUM: {e}")
            raise
    
    def analyze_table(self, table_name: str):
        """Executa ANALYZE em uma tabela específica"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"ANALYZE {table_name}")
            conn.commit()
            return_db_connection(conn)
            logger.info(f"ANALYZE executado na tabela {table_name}")
        except Exception as e:
            logger.error(f"Erro ao executar ANALYZE na tabela {table_name}: {e}")
            raise

class IntelligentCache:
    """Sistema de cache inteligente para queries"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.cache = OrderedDict()
        self.access_times = {}
        self.hit_counts = defaultdict(int)
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
    
    def _generate_key(self, query: str, params: tuple = None) -> str:
        """Gera chave única para a query"""
        return f"{hash(query)}_{hash(params) if params else 'none'}"
    
    def get(self, query: str, params: tuple = None) -> Optional[Any]:
        """Recupera resultado do cache"""
        key = self._generate_key(query, params)
        
        with self._lock:
            if key not in self.cache:
                return None
            
            # Verificar TTL
            cached_time = self.access_times.get(key, 0)
            if time.time() - cached_time > self.ttl_seconds:
                # Expirou, remover do cache
                del self.cache[key]
                del self.access_times[key]
                return None
            
            # Atualizar acesso (LRU)
            value = self.cache[key]
            del self.cache[key]
            self.cache[key] = value
            self.hit_counts[key] += 1
            
            return value
    
    def set(self, query: str, result: Any, params: tuple = None):
        """Armazena resultado no cache"""
        key = self._generate_key(query, params)
        
        with self._lock:
            # Remover mais antigos se necessário
            if len(self.cache) >= self.max_size:
                # Remove o menos recentemente usado
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.access_times.pop(oldest_key, None)
                self.hit_counts.pop(oldest_key, None)
            
            self.cache[key] = result
            self.access_times[key] = time.time()
    
    def clear(self):
        """Limpa todo o cache"""
        with self._lock:
            self.cache.clear()
            self.access_times.clear()
            self.hit_counts.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Estatísticas do cache"""
        with self._lock:
            total_hits = sum(self.hit_counts.values())
            return {
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'total_hits': total_hits,
                'unique_queries': len(self.hit_counts),
                'hit_rate': total_hits / max(1, len(self.cache)) * 100,
                'ttl_seconds': self.ttl_seconds
            }

# Instância global de cache
intelligent_cache = IntelligentCache()

def cached_query(ttl_seconds: int = 300):
    """Decorator para cachear resultados de queries"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extrair query e parâmetros
            query = kwargs.get('query', args[0] if args else '')
            params = kwargs.get('params', args[1:] if len(args) > 1 else None)
            
            # Tentar recuperar do cache
            cached_result = intelligent_cache.get(query, params)
            if cached_result is not None:
                return cached_result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            intelligent_cache.set(query, result, params)
            
            return result
        return wrapper
    return decorator

class OptimizedQueries:
    """Queries otimizadas mais usadas no sistema"""
    
    @staticmethod
    @cached_query(ttl_seconds=600)  # Cache por 10 minutos
    def get_dashboard_stats() -> Dict[str, Any]:
        """Estatísticas do dashboard com cache"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Query otimizada com índices
            stats_query = """
            SELECT 
                COUNT(*) as total_rncs,
                SUM(CASE WHEN status = 'Finalizado' THEN 1 ELSE 0 END) as finalized,
                SUM(CASE WHEN status != 'Finalizado' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN priority = 'Crítica' THEN 1 ELSE 0 END) as critical,
                AVG(price) as avg_price,
                SUM(price) as total_value
            FROM rncs 
            WHERE is_deleted = 0
            """
            
            cursor.execute(stats_query)
            result = cursor.fetchone()
            
            stats = {
                'total_rncs': result[0] or 0,
                'finalized': result[1] or 0,
                'active': result[2] or 0,
                'critical': result[3] or 0,
                'avg_price': result[4] or 0.0,
                'total_value': result[5] or 0.0
            }
            
            return_db_connection(conn)
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do dashboard: {e}")
            return {}
    
    @staticmethod
    @cached_query(ttl_seconds=300)  # Cache por 5 minutos
    def get_rncs_by_department() -> List[Dict[str, Any]]:
        """RNCs por departamento com cache"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Query otimizada
            query = """
            SELECT 
                department,
                COUNT(*) as count,
                SUM(CASE WHEN status = 'Finalizado' THEN 1 ELSE 0 END) as finalized,
                SUM(price) as total_value
            FROM rncs
            WHERE is_deleted = 0
            GROUP BY department
            ORDER BY count DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            data = []
            for row in results:
                data.append({
                    'department': row[0],
                    'count': row[1],
                    'finalized': row[2],
                    'total_value': row[3] or 0.0
                })
            
            return_db_connection(conn)
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter RNCs por departamento: {e}")
            return []
    
    @staticmethod
    @cached_query(ttl_seconds=60)  # Cache por 1 minuto (dados mais dinâmicos)
    def get_recent_rncs(limit: int = 10) -> List[Dict[str, Any]]:
        """RNCs recentes com cache"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Query otimizada com limite
            query = """
            SELECT 
                r.id, r.rnc_number, r.title, r.status, r.priority, 
                r.created_at, u.name as creator_name, r.department
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.is_deleted = 0
            ORDER BY r.created_at DESC
            LIMIT ?
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            
            data = []
            for row in results:
                data.append({
                    'id': row[0],
                    'rnc_number': row[1],
                    'title': row[2],
                    'status': row[3],
                    'priority': row[4],
                    'created_at': row[5],
                    'creator_name': row[6],
                    'department': row[7]
                })
            
            return_db_connection(conn)
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter RNCs recentes: {e}")
            return []

# Instâncias globais
db_optimizer = DatabaseOptimizer()
optimized_queries = OptimizedQueries()

def initialize_database_optimizations():
    """Inicializa otimizações do banco de dados"""
    try:
        # Criar índices otimizados
        db_optimizer.create_optimized_indexes()
        
        # Executar ANALYZE em tabelas principais
        for table in ['users', 'rncs', 'groups', 'group_permissions']:
            try:
                db_optimizer.analyze_table(table)
            except Exception as e:
                logger.warning(f"Erro ao analisar tabela {table}: {e}")
        
        logger.info("Otimizações de banco de dados inicializadas com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar otimizações: {e}")

def get_performance_report() -> Dict[str, Any]:
    """Gera relatório completo de performance"""
    try:
        return {
            'database_analysis': db_optimizer.analyze_database_performance(),
            'query_statistics': query_optimizer.get_query_statistics(),
            'optimization_suggestions': query_optimizer.suggest_optimizations(),
            'cache_statistics': intelligent_cache.get_stats(),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de performance: {e}")
        return {'error': str(e)}
