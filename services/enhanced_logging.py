"""
Sistema de logging estruturado e centralizado para IPPEL RNC
Substitui logging básico por sistema mais robusto com contexto e métricas
"""

import logging
import json
import time
import functools
from datetime import datetime
from typing import Any, Dict, Optional, Union
from flask import request, session, g
import traceback

# Configuração do formato de log estruturado
class StructuredFormatter(logging.Formatter):
    """Formatter que produz logs estruturados em JSON"""
    
    def format(self, record):
        # Informações básicas do log
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Adicionar contexto da requisição se disponível
        try:
            if hasattr(record, 'request_id'):
                log_entry['request_id'] = record.request_id
            elif hasattr(g, 'request_id'):
                log_entry['request_id'] = g.request_id
                
            # Informações do usuário se autenticado
            if 'user_id' in session:
                log_entry['user_id'] = session['user_id']
                log_entry['user_name'] = session.get('user_name', 'unknown')
                
            # Informações da requisição
            if request:
                log_entry['request'] = {
                    'method': request.method,
                    'url': request.url,
                    'endpoint': request.endpoint,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', 'unknown')[:200]
                }
        except:
            # Em contexto fora de request, ignora
            pass
            
        # Informações adicionais se presentes no record
        if hasattr(record, 'extra_data') and record.extra_data:
            log_entry['extra'] = record.extra_data
            
        # Stack trace para erros
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        # Performance metrics se disponível
        if hasattr(record, 'duration'):
            log_entry['performance'] = {
                'duration_ms': round(record.duration * 1000, 2)
            }
            
        return json.dumps(log_entry, ensure_ascii=False)

class IPPELLogger:
    """Logger principal do sistema IPPEL com funcionalidades avançadas"""
    
    def __init__(self, name: str = 'ippel'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Evitar handlers duplicados
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura handlers de log"""
        
        # Handler para arquivo com rotação
        try:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                'logs/ippel_app.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(StructuredFormatter())
            file_handler.setLevel(logging.INFO)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Não foi possível configurar file handler: {e}")
        
        # Handler para console (desenvolvimento)
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.WARNING)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, extra_data: Optional[Dict] = None, **kwargs):
        """Log de informação com dados estruturados"""
        extra = {'extra_data': extra_data} if extra_data else {}
        self.logger.info(message, extra=extra, **kwargs)
    
    def warning(self, message: str, extra_data: Optional[Dict] = None, **kwargs):
        """Log de warning com dados estruturados"""
        extra = {'extra_data': extra_data} if extra_data else {}
        self.logger.warning(message, extra=extra, **kwargs)
    
    def error(self, message: str, extra_data: Optional[Dict] = None, exc_info=True, **kwargs):
        """Log de erro com dados estruturados"""
        extra = {'extra_data': extra_data} if extra_data else {}
        self.logger.error(message, extra=extra, exc_info=exc_info, **kwargs)
    
    def debug(self, message: str, extra_data: Optional[Dict] = None, **kwargs):
        """Log de debug com dados estruturados"""
        extra = {'extra_data': extra_data} if extra_data else {}
        self.logger.debug(message, extra=extra, **kwargs)

# Instância global do logger
ippel_logger = IPPELLogger()

def log_performance(operation_name: str = None):
    """Decorator para medir e logar performance de funções"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log de sucesso com métricas
                extra = logging.LogRecord(
                    name=ippel_logger.logger.name,
                    level=logging.INFO,
                    pathname='',
                    lineno=0,
                    msg=f"Operation completed: {op_name}",
                    args=(),
                    exc_info=None
                )
                extra.duration = duration
                ippel_logger.logger.handle(extra)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Log de erro com métricas
                ippel_logger.error(
                    f"Operation failed: {op_name}",
                    extra_data={
                        'duration_ms': round(duration * 1000, 2),
                        'error_type': type(e).__name__,
                        'args_count': len(args),
                        'kwargs_keys': list(kwargs.keys()) if kwargs else []
                    }
                )
                raise
                
        return wrapper
    return decorator

def log_api_request():
    """Decorator para logar requisições API"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Log início da requisição
            ippel_logger.info(
                f"API Request: {request.method} {request.endpoint}",
                extra_data={
                    'request_data_size': request.content_length or 0,
                    'content_type': request.content_type
                }
            )
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Extrair status code da resposta
                status_code = 200
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                elif isinstance(result, tuple) and len(result) > 1:
                    status_code = result[1]
                
                # Log sucesso
                ippel_logger.info(
                    f"API Response: {status_code} - {request.endpoint}",
                    extra_data={
                        'duration_ms': round(duration * 1000, 2),
                        'status_code': status_code
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                ippel_logger.error(
                    f"API Error: {request.endpoint}",
                    extra_data={
                        'duration_ms': round(duration * 1000, 2),
                        'error_type': type(e).__name__
                    }
                )
                raise
                
        return wrapper
    return decorator

def log_database_operation(operation_type: str):
    """Decorator para logar operações de banco de dados"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log operação bem-sucedida
                ippel_logger.info(
                    f"Database {operation_type} completed",
                    extra_data={
                        'operation': operation_type,
                        'function': func.__name__,
                        'duration_ms': round(duration * 1000, 2)
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                ippel_logger.error(
                    f"Database {operation_type} failed",
                    extra_data={
                        'operation': operation_type,
                        'function': func.__name__,
                        'duration_ms': round(duration * 1000, 2),
                        'error_details': str(e)
                    }
                )
                raise
                
        return wrapper
    return decorator

class SecurityLogger:
    """Logger especializado para eventos de segurança"""
    
    def __init__(self):
        self.logger = IPPELLogger('ippel.security')
    
    def log_auth_attempt(self, email: str, success: bool, ip: str, details: Dict = None):
        """Log de tentativa de autenticação"""
        self.logger.info(
            f"Authentication {'successful' if success else 'failed'}: {email}",
            extra_data={
                'event_type': 'auth_attempt',
                'email': email,
                'success': success,
                'ip_address': ip,
                'details': details or {}
            }
        )
    
    def log_permission_check(self, user_id: int, permission: str, granted: bool, resource: str = None):
        """Log de verificação de permissão"""
        self.logger.info(
            f"Permission check: {permission} - {'granted' if granted else 'denied'}",
            extra_data={
                'event_type': 'permission_check',
                'user_id': user_id,
                'permission': permission,
                'granted': granted,
                'resource': resource
            }
        )
    
    def log_suspicious_activity(self, user_id: int, activity: str, details: Dict):
        """Log de atividade suspeita"""
        self.logger.warning(
            f"Suspicious activity detected: {activity}",
            extra_data={
                'event_type': 'suspicious_activity',
                'user_id': user_id,
                'activity': activity,
                'details': details
            }
        )

# Instâncias globais
security_logger = SecurityLogger()

# Utilitários para logging contextual
def set_request_context(request_id: str = None):
    """Define contexto da requisição para logs"""
    if not request_id:
        import uuid
        request_id = str(uuid.uuid4())[:8]
    g.request_id = request_id
    return request_id

def get_request_context() -> Optional[str]:
    """Obtém contexto da requisição atual"""
    return getattr(g, 'request_id', None)
