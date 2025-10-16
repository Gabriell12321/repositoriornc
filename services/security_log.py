"""
Logger de segurança com saída em JSON (linhas) e arquivo rotativo.

Uso:
  from services.security_log import setup_security_logger, sec_log
  setup_security_logger(app)
  sec_log('auth', 'login_attempt', ip=..., email=..., status='success'|'fail', details={...})
"""
from __future__ import annotations

import json
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Any, Dict, Optional


_LOGGER_NAME = 'security'


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def setup_security_logger(app=None, *, log_dir: Optional[str] = None, filename: str = 'security.log') -> logging.Logger:
    """Configura logger 'security' com RotatingFileHandler e formato JSON por linha.

    - Por padrão grava em logs/security.log no diretório do projeto.
    - maxBytes ~ 5MB, backupCount 5.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    # Evita duplicar handlers se já configurado
    if logger.handlers:
        return logger

    root = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(root)
    base_dir = log_dir or os.path.join(project_root, 'logs')
    _ensure_dir(base_dir)
    log_path = os.path.join(base_dir, filename)

    handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8')

    class JsonLineFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            payload = {
                'ts': datetime.utcnow().isoformat() + 'Z',
                'lvl': record.levelname,
                'msg': record.getMessage(),
            }
            if isinstance(getattr(record, 'extra', None), dict):
                payload.update(record.extra)  # type: ignore
            return json.dumps(payload, ensure_ascii=False)

    handler.setFormatter(JsonLineFormatter())
    logger.addHandler(handler)
    # Também loga no console principal
    stream = logging.StreamHandler()
    stream.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.addHandler(stream)
    logger.propagate = False
    return logger


def sec_log(category: str, action: str, *, ip: Optional[str] = None, user_id: Optional[int] = None,
            email: Optional[str] = None, status: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
            level: int = logging.INFO) -> None:
    """Escreve um evento de segurança padronizado.

    Campos comuns: categoria (ex.: 'auth', 'rate_limit', 'api'), ação, ip, user_id, email, status, details.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    payload: Dict[str, Any] = {
        'cat': category,
        'act': action,
    }
    if ip:
        payload['ip'] = ip
    if user_id is not None:
        payload['user_id'] = user_id
    if email:
        payload['email'] = email
    if status:
        payload['status'] = status
    if details:
        payload['details'] = details
    logger.log(level, action, extra={'extra': payload})
