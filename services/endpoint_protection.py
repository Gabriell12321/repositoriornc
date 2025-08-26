"""
Proteções avançadas para endpoints: CSRF, permissões e allowlist de IP.

Observação: CSRF está em modo opcional (controlado por env CSRF_ENFORCE). Por padrão, só registra violações.
"""
from __future__ import annotations

import os
import secrets
from functools import wraps
from typing import Callable, Optional

from flask import request, jsonify, session


def ensure_csrf_token() -> str:
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_hex(16)
        session['csrf_token'] = token
    return token


def csrf_protect(enforce: Optional[bool] = None) -> Callable:
    """Decorator que valida header X-CSRF-Token para métodos de escrita.
    Enforce pode ser forçado; caso None, usa env CSRF_ENFORCE (default: false).
    """
    env_enforce = os.environ.get('CSRF_ENFORCE', '0') not in ('0', 'false', 'False', '')
    do_enforce = env_enforce if enforce is None else enforce

    def _dec(func: Callable) -> Callable:
        @wraps(func)
        def _wrap(*args, **kwargs):
            if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                expected = session.get('csrf_token')
                provided = request.headers.get('X-CSRF-Token') or request.headers.get('X-XSRF-TOKEN')
                ok = bool(expected) and provided == expected
                if not ok:
                    # Log violação
                    try:
                        import importlib
                        _sl = importlib.import_module('services.security_log')
                        _sl.sec_log('csrf', 'check', ip=request.remote_addr, status='violation', details={'path': request.path})
                    except Exception:
                        pass
                    if do_enforce:
                        return jsonify({'success': False, 'message': 'CSRF inválido'}), 403
            return func(*args, **kwargs)
        return _wrap
    return _dec


def require_permission(perm_name: str) -> Callable:
    from services.permissions import has_permission  # late import para evitar ciclos
    def _dec(func: Callable) -> Callable:
        @wraps(func)
        def _wrap(*args, **kwargs):
            uid = session.get('user_id')
            if not uid or not has_permission(uid, perm_name):
                return jsonify({'success': False, 'message': 'Sem permissão'}), 403
            return func(*args, **kwargs)
        return _wrap
    return _dec


def require_ip_allowlist(env_var: str = 'ADMIN_IP_ALLOWLIST') -> Callable:
    """Restringe rota a IPs em uma allowlist definida via env (CSV)."""
    allowlist = {ip.strip() for ip in os.environ.get(env_var, '').split(',') if ip.strip()}
    def _dec(func: Callable) -> Callable:
        @wraps(func)
        def _wrap(*args, **kwargs):
            if allowlist:
                ip = request.remote_addr
                if ip not in allowlist:
                    return jsonify({'success': False, 'message': 'IP não autorizado'}), 403
            return func(*args, **kwargs)
        return _wrap
    return _dec
