import threading
import time
from typing import Any, Optional

query_cache: dict[str, dict[str, Any]] = {}
cache_lock = threading.Lock()


def cache_query(key: str, data: Any, ttl: int = 300) -> None:
    with cache_lock:
        query_cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl,
        }


def get_cached_query(key: str) -> Optional[Any]:
    with cache_lock:
        entry = query_cache.get(key)
        if not entry:
            return None
        if time.time() - entry['timestamp'] < entry['ttl']:
            return entry['data']
        # expired
        query_cache.pop(key, None)
        return None


def clear_expired_cache() -> None:
    now = time.time()
    with cache_lock:
        expired = [k for k, v in query_cache.items() if now - v['timestamp'] > v['ttl']]
        for k in expired:
            query_cache.pop(k, None)


def clear_rnc_cache(user_id: int | None = None) -> None:
    with cache_lock:
        keys = list(query_cache.keys())
        for k in keys:
            if not k.startswith('rncs_list_'):
                continue
            if user_id is None or f"rncs_list_{user_id}_" in k:
                query_cache.pop(k, None)
