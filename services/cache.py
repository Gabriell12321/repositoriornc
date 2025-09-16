import threading
import time
import os
import json
import hashlib
from typing import Any, Optional, Union, Dict, List
from functools import wraps
from datetime import datetime, timedelta

# Try Redis; gracefully fall back to in-memory cache if unavailable
try:
    import redis  # type: ignore
except Exception:  # redis not installed
    redis = None  # type: ignore

_redis_client = None
_REDIS_PREFIX = os.getenv('REDIS_PREFIX', 'ippel:')

if redis is not None:
    try:
        url = os.getenv('REDIS_URL')
        if url:
            _redis_client = redis.from_url(url, decode_responses=True)
        else:
            _redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', '127.0.0.1'),
                port=int(os.getenv('REDIS_PORT', '6379')),
                db=int(os.getenv('REDIS_DB', '0')),
                decode_responses=True,
            )
        # Sanity check connection
        try:
            _redis_client.ping()
        except Exception:
            _redis_client = None
    except Exception:
        _redis_client = None


def _rkey(key: str) -> str:
    return f"{_REDIS_PREFIX}q:{key}"


# In-memory fallback store with enhanced metadata
query_cache: dict[str, dict[str, Any]] = {}
cache_stats = {
    'hits': 0,
    'misses': 0,
    'redis_errors': 0,
    'last_cleanup': time.time()
}
cache_lock = threading.Lock()

class CacheManager:
    """Gerenciador avançado de cache com métricas e otimizações"""
    
    def __init__(self):
        self.redis_client = _redis_client
        self.prefix = _REDIS_PREFIX
        
    def generate_cache_key(self, base_key: str, params: Dict = None, user_id: int = None) -> str:
        """Gera chave de cache consistente e única"""
        components = [base_key]
        
        if user_id:
            components.append(f"user:{user_id}")
            
        if params:
            # Ordenar parâmetros para consistência
            sorted_params = sorted(params.items())
            param_str = json.dumps(sorted_params, sort_keys=True, ensure_ascii=False)
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            components.append(f"params:{param_hash}")
            
        return ":".join(components)
    
    def cache_with_tags(self, key: str, data: Any, ttl: int = 300, tags: List[str] = None) -> None:
        """Cache com sistema de tags para invalidação seletiva"""
        cache_entry = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl,
            'tags': tags or []
        }
        
        # Tentar Redis primeiro
        if self.redis_client is not None:
            try:
                # Cache os dados
                self.redis_client.set(
                    _rkey(key), 
                    json.dumps(cache_entry, ensure_ascii=False), 
                    ex=int(ttl)
                )
                
                # Indexar por tags para invalidação
                if tags:
                    for tag in tags:
                        tag_key = f"{self.prefix}tags:{tag}"
                        self.redis_client.sadd(tag_key, key)
                        self.redis_client.expire(tag_key, ttl + 3600)  # Tags vivem mais tempo
                        
                return
            except Exception:
                cache_stats['redis_errors'] += 1
        
        # Fallback para memória
        with cache_lock:
            query_cache[key] = cache_entry
    
    def get_cached_with_stats(self, key: str) -> Optional[Any]:
        """Busca cache com coleta de estatísticas"""
        # Tentar Redis
        if self.redis_client is not None:
            try:
                raw = self.redis_client.get(_rkey(key))
                if raw is None:
                    cache_stats['misses'] += 1
                    return None
                    
                cache_entry = json.loads(raw)
                cache_stats['hits'] += 1
                return cache_entry.get('data')
            except Exception:
                cache_stats['redis_errors'] += 1
        
        # Fallback para memória
        with cache_lock:
            entry = query_cache.get(key)
            if not entry:
                cache_stats['misses'] += 1
                return None
                
            if time.time() - entry['timestamp'] < entry['ttl']:
                cache_stats['hits'] += 1
                return entry['data']
            else:
                # Expirado
                query_cache.pop(key, None)
                cache_stats['misses'] += 1
                return None
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalida entradas do cache por tags"""
        invalidated = 0
        
        if self.redis_client is not None:
            try:
                for tag in tags:
                    tag_key = f"{self.prefix}tags:{tag}"
                    keys_to_invalidate = self.redis_client.smembers(tag_key)
                    
                    if keys_to_invalidate:
                        # Adicionar prefixo para chaves Redis
                        redis_keys = [_rkey(k) for k in keys_to_invalidate]
                        self.redis_client.delete(*redis_keys)
                        invalidated += len(redis_keys)
                        
                    # Limpar o índice de tag
                    self.redis_client.delete(tag_key)
            except Exception:
                cache_stats['redis_errors'] += 1
        
        # Limpar também da memória
        with cache_lock:
            keys_to_remove = []
            for key, entry in query_cache.items():
                if any(tag in entry.get('tags', []) for tag in tags):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                query_cache.pop(key, None)
                invalidated += 1
                
        return invalidated
    
    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        total_requests = cache_stats['hits'] + cache_stats['misses']
        hit_rate = (cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            'hits': cache_stats['hits'],
            'misses': cache_stats['misses'],
            'hit_rate_percent': round(hit_rate, 2),
            'redis_errors': cache_stats['redis_errors'],
            'redis_available': self.redis_client is not None,
            'memory_entries': len(query_cache),
            'last_cleanup': cache_stats['last_cleanup']
        }
        
        # Informações do Redis se disponível
        if self.redis_client is not None:
            try:
                redis_info = self.redis_client.info('memory')
                stats['redis_memory_mb'] = round(redis_info['used_memory'] / 1024 / 1024, 2)
                stats['redis_keys'] = self.redis_client.dbsize()
            except:
                pass
                
        return stats

# Instância global do gerenciador
cache_manager = CacheManager()

def cached_query(ttl: int = 300, tags: List[str] = None, key_prefix: str = None):
    """Decorator para cache automático de funções com parâmetros"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave baseada na função e parâmetros
            func_name = f"{func.__module__}.{func.__name__}" if key_prefix is None else key_prefix
            
            # Incluir argumentos na chave
            cache_params = {
                'args': str(args) if args else None,
                'kwargs': kwargs if kwargs else None
            }
            
            cache_key = cache_manager.generate_cache_key(func_name, cache_params)
            
            # Tentar buscar no cache
            cached_result = cache_manager.get_cached_with_stats(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            cache_manager.cache_with_tags(cache_key, result, ttl, tags)
            
            return result
        return wrapper
    return decorator


def cache_query(key: str, data: Any, ttl: int = 300, tags: List[str] = None) -> None:
    """Cache query com sistema de tags melhorado"""
    cache_manager.cache_with_tags(key, data, ttl, tags)


def get_cached_query(key: str) -> Optional[Any]:
    """Busca cache com estatísticas"""
    return cache_manager.get_cached_with_stats(key)


def clear_expired_cache() -> None:
    """Limpa cache expirado e atualiza estatísticas"""
    now = time.time()
    
    # Redis se cuida sozinho, mas limpar memória
    with cache_lock:
        expired_keys = []
        for key, entry in query_cache.items():
            if now - entry['timestamp'] > entry['ttl']:
                expired_keys.append(key)
        
        for key in expired_keys:
            query_cache.pop(key, None)
            
        # Atualizar timestamp da limpeza
        cache_stats['last_cleanup'] = now
        
    # Limpeza periódica mais agressiva se muitas entradas
    if len(query_cache) > 1000:
        with cache_lock:
            # Manter apenas 500 entradas mais recentes
            sorted_entries = sorted(
                query_cache.items(), 
                key=lambda x: x[1]['timestamp'], 
                reverse=True
            )
            query_cache.clear()
            query_cache.update(dict(sorted_entries[:500]))


def clear_rnc_cache(user_id: int | None = None, tags: List[str] = None) -> None:
    """Limpa cache de RNCs com sistema de tags"""
    
    # Se tags especificadas, usar invalidação por tags
    if tags:
        cache_manager.invalidate_by_tags(tags)
        return
    
    # Sistema legado por padrão de chaves
    pattern = 'rncs_list_*' if user_id is None else f'rncs_list_{user_id}_*'
    
    if _redis_client is not None:
        try:
            full_pat = _rkey(pattern)
            to_del = []
            for k in _redis_client.scan_iter(match=full_pat, count=500):
                to_del.append(k)
                if len(to_del) >= 1000:
                    _redis_client.delete(*to_del)
                    to_del.clear()
            if to_del:
                _redis_client.delete(*to_del)
        except Exception:
            cache_stats['redis_errors'] += 1
    
    # Limpar também da memória
    with cache_lock:
        keys = list(query_cache.keys())
        for k in keys:
            if not k.startswith('rncs_list_'):
                continue
            if user_id is None or f"rncs_list_{user_id}_" in k:
                query_cache.pop(k, None)


def get_cache_stats() -> Dict:
    """Retorna estatísticas detalhadas do cache"""
    return cache_manager.get_cache_stats()


def redis_enabled() -> bool:
    return _redis_client is not None


# Funções de conveniência para invalidação por tags
def invalidate_user_cache(user_id: int):
    """Invalida todo cache relacionado a um usuário"""
    cache_manager.invalidate_by_tags([f'user:{user_id}'])


def invalidate_rnc_cache(rnc_id: int = None):
    """Invalida cache relacionado a RNCs"""
    tags = ['rnc:list', 'rnc:dashboard']
    if rnc_id:
        tags.append(f'rnc:{rnc_id}')
    cache_manager.invalidate_by_tags(tags)


def invalidate_dashboard_cache():
    """Invalida cache do dashboard"""
    cache_manager.invalidate_by_tags(['dashboard', 'metrics'])
