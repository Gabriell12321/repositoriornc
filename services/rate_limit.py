"""
Rate limiting helper com fallback seguro.

Uso:
  from services.rate_limit import init_limiter, rate_limit
  limiter = init_limiter(app, default_limits=["200 per minute"])  # aplica a todas as rotas
  @rate_limit("5 per minute; 20 per hour")
  def login(): ...

Se Flask-Limiter não estiver instalado, os decoradores viram no-op.
"""
from __future__ import annotations

from typing import Callable, Optional, List

try:
    from flask_limiter import Limiter  # type: ignore
    from flask_limiter.util import get_remote_address  # type: ignore
    _HAS_LIMITER = True
except Exception:  # pragma: no cover - fallback when not installed
    Limiter = None  # type: ignore
    def get_remote_address():  # type: ignore
        from flask import request
        return request.remote_addr if request else "127.0.0.1"
    _HAS_LIMITER = False

_limiter_instance = None  # type: ignore


def init_limiter(app, default_limits: Optional[List[str]] = None):
    """Inicializa o Limiter no app. Se não houver lib, retorna None.

    - Usa REDIS_URL se definido para storage distribuído; caso contrário, memória.
    - Aplica default_limits (por ex.: ["200 per minute"]).
    """
    global _limiter_instance
    if not _HAS_LIMITER or Limiter is None:
        _limiter_instance = None
        return None
    import os
    storage_uri = os.environ.get("REDIS_URL")
    if storage_uri:
        # Compatível com redis e rediss
        storage = storage_uri
    else:
        storage = "memory://"
    try:
        _limiter_instance = Limiter(
            get_remote_address,
            app=app,
            default_limits=default_limits or [],
            storage_uri=storage,
            strategy="fixed-window",
        )
    except Exception:
        # fallback para memória sem defaults
        _limiter_instance = Limiter(get_remote_address, app=app, storage_uri="memory://")
    return _limiter_instance


def rate_limit(limits: str) -> Callable:
    """Decorator que aplica limite à rota. No fallback, retorna função no-op."""
    def _decorator(func: Callable) -> Callable:
        if _limiter_instance is not None:
            return _limiter_instance.limit(limits)(func)  # type: ignore
        # no-op
        return func
    return _decorator


def limiter():
    """Retorna a instância atual do Limiter (ou None)."""
    return _limiter_instance


def exempt_from_rate_limit(func: Callable) -> Callable:
    """Marca uma rota como isenta de rate limiting."""
    if _limiter_instance is not None:
        try:
            return _limiter_instance.exempt(func)  # type: ignore
        except Exception:
            pass
    return func
