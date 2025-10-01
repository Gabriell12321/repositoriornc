# Health check endpoint para IPPEL RNC System
# Endpoint dedicado para verificação de saúde da aplicação

from flask import Blueprint, jsonify, current_app
import sqlite3
import time
import os
from datetime import datetime
import psutil

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check para verificação de saúde da aplicação
    Retorna status detalhado de todos os componentes críticos
    """
    start_time = time.time()
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'checks': {}
    }
    
    # 1. Verificar banco de dados
    try:
        db_path = 'ippel_system.db'
        conn = sqlite3.connect(db_path, timeout=5)
        cursor = conn.cursor()
        
        # Teste simples de consulta
        cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type="table"')
        table_count = cursor.fetchone()[0]
        
        # Verificar se tabelas principais existem
        required_tables = ['users', 'rncs', 'groups']
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        existing_tables = [row[0] for row in cursor.fetchall()]
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        conn.close()
        
        health_status['checks']['database'] = {
            'status': 'healthy' if not missing_tables else 'unhealthy',
            'tables_count': table_count,
            'missing_tables': missing_tables,
            'file_exists': os.path.exists(db_path),
            'file_size': os.path.getsize(db_path) if os.path.exists(db_path) else 0
        }
        
        if missing_tables:
            health_status['status'] = 'unhealthy'
            
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # 2. Verificar sistema de arquivos
    try:
        required_dirs = ['logs', 'backups', 'static', 'templates']
        missing_dirs = []
        disk_usage = {}
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                missing_dirs.append(directory)
        
        # Verificar espaço em disco
        disk_stats = psutil.disk_usage('.')
        disk_usage = {
            'total': disk_stats.total,
            'used': disk_stats.used,
            'free': disk_stats.free,
            'percent': (disk_stats.used / disk_stats.total) * 100
        }
        
        health_status['checks']['filesystem'] = {
            'status': 'healthy' if not missing_dirs and disk_usage['percent'] < 90 else 'warning',
            'missing_directories': missing_dirs,
            'disk_usage': disk_usage
        }
        
    except Exception as e:
        health_status['checks']['filesystem'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # 3. Verificar recursos do sistema
    try:
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        memory_status = 'healthy'
        if memory.percent > 90:
            memory_status = 'critical'
        elif memory.percent > 80:
            memory_status = 'warning'
        
        cpu_status = 'healthy'
        if cpu_percent > 90:
            cpu_status = 'critical'
        elif cpu_percent > 80:
            cpu_status = 'warning'
        
        health_status['checks']['system_resources'] = {
            'status': memory_status if memory_status == 'critical' or cpu_status == 'critical' else 'healthy',
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'status': memory_status
            },
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count(),
                'status': cpu_status
            }
        }
        
        if memory_status == 'critical' or cpu_status == 'critical':
            health_status['status'] = 'unhealthy'
            
    except Exception as e:
        health_status['checks']['system_resources'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # 4. Verificar configurações críticas
    try:
        config_status = 'healthy'
        config_issues = []
        
        # Verificar variáveis de ambiente críticas
        critical_env_vars = ['SECRET_KEY', 'FLASK_ENV']
        for var in critical_env_vars:
            if not os.environ.get(var):
                config_issues.append(f'Missing environment variable: {var}')
        
        # Verificar arquivo de configuração local
        if not os.path.exists('config_local.py'):
            config_issues.append('config_local.py not found')
        
        if config_issues:
            config_status = 'warning'
        
        health_status['checks']['configuration'] = {
            'status': config_status,
            'issues': config_issues,
            'environment': os.environ.get('FLASK_ENV', 'not_set')
        }
        
    except Exception as e:
        health_status['checks']['configuration'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # 5. Verificar serviços externos (se aplicável)
    try:
        external_services = {}
        
        # Verificar Redis (se configurado)
        try:
            import redis
            redis_client = redis.Redis(host='redis-cache', port=6379, db=0, socket_timeout=2)
            redis_client.ping()
            external_services['redis'] = {
                'status': 'healthy',
                'response_time': time.time() - start_time
            }
        except:
            external_services['redis'] = {
                'status': 'not_available',
                'note': 'Redis not configured or not accessible'
            }
        
        health_status['checks']['external_services'] = external_services
        
    except Exception as e:
        health_status['checks']['external_services'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Calcular tempo de resposta
    response_time = time.time() - start_time
    health_status['response_time'] = round(response_time * 1000, 2)  # em ms
    
    # Determinar código de status HTTP
    if health_status['status'] == 'unhealthy':
        status_code = 503  # Service Unavailable
    elif any(check.get('status') == 'warning' for check in health_status['checks'].values()):
        status_code = 200  # OK, mas com warnings
        health_status['status'] = 'degraded'
    else:
        status_code = 200  # OK
    
    return jsonify(health_status), status_code


@health_bp.route('/health/simple', methods=['GET'])
def simple_health_check():
    """Health check simples para load balancers"""
    try:
        # Verificação básica de banco
        conn = sqlite3.connect('ippel_system.db', timeout=2)
        conn.execute('SELECT 1')
        conn.close()
        
        return jsonify({
            'status': 'OK',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception:
        return jsonify({
            'status': 'ERROR',
            'timestamp': datetime.now().isoformat()
        }), 503


@health_bp.route('/health/deep', methods=['GET'])
def deep_health_check():
    """Health check completo com informações detalhadas"""
    start_time = time.time()
    
    detailed_health = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'application': {
            'name': 'IPPEL RNC System',
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'unknown'),
            'uptime': time.time() - start_time  # Simplificado
        },
        'database': {},
        'system': {},
        'performance': {}
    }
    
    try:
        # Análise detalhada do banco
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Contar registros principais
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        active_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE is_deleted = 0')
        active_rncs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE status = "Finalizado"')
        completed_rncs = cursor.fetchone()[0]
        
        # Verificar integridade
        cursor.execute('PRAGMA integrity_check(1)')
        integrity = cursor.fetchone()[0]
        
        conn.close()
        
        detailed_health['database'] = {
            'status': 'healthy' if integrity == 'ok' else 'unhealthy',
            'integrity': integrity,
            'statistics': {
                'active_users': active_users,
                'active_rncs': active_rncs,
                'completed_rncs': completed_rncs
            }
        }
        
    except Exception as e:
        detailed_health['database'] = {
            'status': 'error',
            'error': str(e)
        }
        detailed_health['status'] = 'unhealthy'
    
    try:
        # Informações do sistema
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        cpu_count = psutil.cpu_count()
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        
        detailed_health['system'] = {
            'memory': {
                'total_gb': round(memory.total / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'percent': memory.percent
            },
            'disk': {
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'percent': round((disk.used / disk.total) * 100, 2)
            },
            'cpu': {
                'count': cpu_count,
                'load_average': load_avg
            }
        }
        
    except Exception as e:
        detailed_health['system'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Performance metrics
    response_time = time.time() - start_time
    detailed_health['performance'] = {
        'response_time_ms': round(response_time * 1000, 2),
        'status': 'good' if response_time < 1.0 else 'slow'
    }
    
    return jsonify(detailed_health), 200


@health_bp.route('/metrics', methods=['GET'])
def prometheus_metrics():
    """Endpoint para métricas no formato Prometheus"""
    try:
        metrics = []
        
        # Métricas básicas da aplicação
        metrics.append('# HELP ippel_app_info Application information')
        metrics.append('# TYPE ippel_app_info gauge')
        metrics.append('ippel_app_info{version="1.0.0",environment="' + os.environ.get('FLASK_ENV', 'unknown') + '"} 1')
        
        # Métricas do banco de dados
        try:
            conn = sqlite3.connect('ippel_system.db', timeout=5)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
            active_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM rncs WHERE is_deleted = 0')
            active_rncs = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM rncs WHERE status = "Finalizado"')
            completed_rncs = cursor.fetchone()[0]
            
            conn.close()
            
            metrics.append('# HELP ippel_users_active Number of active users')
            metrics.append('# TYPE ippel_users_active gauge')
            metrics.append(f'ippel_users_active {active_users}')
            
            metrics.append('# HELP ippel_rncs_active Number of active RNCs')
            metrics.append('# TYPE ippel_rncs_active gauge')
            metrics.append(f'ippel_rncs_active {active_rncs}')
            
            metrics.append('# HELP ippel_rncs_completed Number of completed RNCs')
            metrics.append('# TYPE ippel_rncs_completed gauge')
            metrics.append(f'ippel_rncs_completed {completed_rncs}')
            
        except Exception:
            pass
        
        # Métricas de sistema
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            cpu_percent = psutil.cpu_percent()
            
            metrics.append('# HELP ippel_memory_usage_percent Memory usage percentage')
            metrics.append('# TYPE ippel_memory_usage_percent gauge')
            metrics.append(f'ippel_memory_usage_percent {memory.percent}')
            
            metrics.append('# HELP ippel_disk_usage_percent Disk usage percentage')
            metrics.append('# TYPE ippel_disk_usage_percent gauge')
            metrics.append(f'ippel_disk_usage_percent {round((disk.used / disk.total) * 100, 2)}')
            
            metrics.append('# HELP ippel_cpu_usage_percent CPU usage percentage')
            metrics.append('# TYPE ippel_cpu_usage_percent gauge')
            metrics.append(f'ippel_cpu_usage_percent {cpu_percent}')
            
        except Exception:
            pass
        
        return '\n'.join(metrics), 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
    except Exception as e:
        return f'# Error generating metrics: {str(e)}', 500, {'Content-Type': 'text/plain; charset=utf-8'}
