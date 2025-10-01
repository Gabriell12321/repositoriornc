#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Monitoramento Avançado - IPPEL RNC
Monitoramento de performance, health checks, métricas e alertas
"""

import psutil
import time
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from flask import Blueprint, jsonify, request
from services.db import DB_PATH, get_db_connection, return_db_connection
import logging

monitoring = Blueprint('monitoring', __name__)
logger = logging.getLogger('ippel.monitoring')

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    active_connections: int
    response_time_avg: float
    error_rate: float
    timestamp: datetime

@dataclass
class DatabaseMetrics:
    """Métricas do banco de dados"""
    total_rncs: int
    active_rncs: int
    finalized_rncs: int
    total_users: int
    active_users: int
    database_size_mb: float
    query_count_last_hour: int
    avg_query_time_ms: float

class PerformanceMonitor:
    """Monitor de performance do sistema"""
    
    def __init__(self):
        self.metrics_history: List[SystemMetrics] = []
        self.db_metrics_history: List[DatabaseMetrics] = []
        self.response_times: List[float] = []
        self.error_count = 0
        self.request_count = 0
        self.start_time = datetime.now()
        self._lock = threading.Lock()
    
    def record_request_time(self, response_time: float):
        """Registra tempo de resposta de uma requisição"""
        with self._lock:
            self.response_times.append(response_time)
            self.request_count += 1
            # Manter apenas últimas 1000 requisições
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]
    
    def record_error(self):
        """Registra um erro"""
        with self._lock:
            self.error_count += 1
    
    def get_system_metrics(self) -> SystemMetrics:
        """Coleta métricas atuais do sistema"""
        try:
            # CPU e Memória
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disco
            disk_usage = psutil.disk_usage('/').percent
            
            # Conexões de rede (aproximação)
            connections = len(psutil.net_connections())
            
            # Tempo de resposta médio
            with self._lock:
                if self.response_times:
                    avg_response_time = sum(self.response_times) / len(self.response_times)
                else:
                    avg_response_time = 0.0
                
                # Taxa de erro
                if self.request_count > 0:
                    error_rate = (self.error_count / self.request_count) * 100
                else:
                    error_rate = 0.0
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage=disk_usage,
                active_connections=connections,
                response_time_avg=avg_response_time,
                error_rate=error_rate,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return SystemMetrics(0, 0, 0, 0, 0, 0, datetime.now())
    
    def get_database_metrics(self) -> DatabaseMetrics:
        """Coleta métricas do banco de dados"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Contagem de RNCs
            cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
            total_rncs = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0 AND status != 'Finalizado'")
            active_rncs = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0 AND status = 'Finalizado'")
            finalized_rncs = cursor.fetchone()[0]
            
            # Contagem de usuários
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            active_users = cursor.fetchone()[0]
            
            # Tamanho do banco
            import os
            db_size_bytes = os.path.getsize(DB_PATH)
            db_size_mb = db_size_bytes / (1024 * 1024)
            
            return_db_connection(conn)
            
            return DatabaseMetrics(
                total_rncs=total_rncs,
                active_rncs=active_rncs,
                finalized_rncs=finalized_rncs,
                total_users=total_users,
                active_users=active_users,
                database_size_mb=round(db_size_mb, 2),
                query_count_last_hour=0,  # Implementar posteriormente
                avg_query_time_ms=0.0     # Implementar posteriormente
            )
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do banco: {e}")
            return DatabaseMetrics(0, 0, 0, 0, 0, 0.0, 0, 0.0)
    
    def collect_metrics(self):
        """Coleta e armazena métricas periodicamente"""
        try:
            system_metrics = self.get_system_metrics()
            db_metrics = self.get_database_metrics()
            
            with self._lock:
                self.metrics_history.append(system_metrics)
                self.db_metrics_history.append(db_metrics)
                
                # Manter apenas últimas 24 horas de métricas (assumindo coleta a cada 5 min)
                max_entries = 24 * 12  # 288 entries
                if len(self.metrics_history) > max_entries:
                    self.metrics_history = self.metrics_history[-max_entries:]
                if len(self.db_metrics_history) > max_entries:
                    self.db_metrics_history = self.db_metrics_history[-max_entries:]
            
            # Verificar alertas
            self._check_alerts(system_metrics, db_metrics)
            
        except Exception as e:
            logger.error(f"Erro na coleta de métricas: {e}")
    
    def _check_alerts(self, sys_metrics: SystemMetrics, db_metrics: DatabaseMetrics):
        """Verifica condições de alerta"""
        alerts = []
        
        # CPU alta
        if sys_metrics.cpu_percent > 85:
            alerts.append(f"CPU alta: {sys_metrics.cpu_percent}%")
        
        # Memória alta
        if sys_metrics.memory_percent > 85:
            alerts.append(f"Memória alta: {sys_metrics.memory_percent}%")
        
        # Disco cheio
        if sys_metrics.disk_usage > 90:
            alerts.append(f"Disco cheio: {sys_metrics.disk_usage}%")
        
        # Taxa de erro alta
        if sys_metrics.error_rate > 5:
            alerts.append(f"Taxa de erro alta: {sys_metrics.error_rate}%")
        
        # Tempo de resposta alto
        if sys_metrics.response_time_avg > 2000:  # 2 segundos
            alerts.append(f"Resposta lenta: {sys_metrics.response_time_avg}ms")
        
        # Banco muito grande
        if db_metrics.database_size_mb > 1000:  # 1GB
            alerts.append(f"Banco grande: {db_metrics.database_size_mb}MB")
        
        # Log de alertas
        if alerts:
            logger.warning(f"ALERTAS: {', '.join(alerts)}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde do sistema"""
        try:
            system_metrics = self.get_system_metrics()
            db_metrics = self.get_database_metrics()
            
            # Determinar status geral
            status = "healthy"
            issues = []
            
            if system_metrics.cpu_percent > 85:
                status = "warning"
                issues.append("CPU alta")
            
            if system_metrics.memory_percent > 85:
                status = "warning"
                issues.append("Memória alta")
            
            if system_metrics.error_rate > 10:
                status = "critical"
                issues.append("Taxa de erro crítica")
            
            uptime = datetime.now() - self.start_time
            
            return {
                "status": status,
                "uptime_seconds": int(uptime.total_seconds()),
                "uptime_formatted": str(uptime).split('.')[0],
                "issues": issues,
                "system": {
                    "cpu_percent": system_metrics.cpu_percent,
                    "memory_percent": system_metrics.memory_percent,
                    "disk_usage": system_metrics.disk_usage,
                    "active_connections": system_metrics.active_connections,
                    "response_time_avg": system_metrics.response_time_avg,
                    "error_rate": system_metrics.error_rate
                },
                "database": {
                    "total_rncs": db_metrics.total_rncs,
                    "active_rncs": db_metrics.active_rncs,
                    "finalized_rncs": db_metrics.finalized_rncs,
                    "total_users": db_metrics.total_users,
                    "active_users": db_metrics.active_users,
                    "size_mb": db_metrics.database_size_mb
                },
                "requests": {
                    "total": self.request_count,
                    "errors": self.error_count
                }
            }
        except Exception as e:
            logger.error(f"Erro ao gerar status de saúde: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

# Instância global do monitor
performance_monitor = PerformanceMonitor()

def start_monitoring_scheduler():
    """Inicia coleta periódica de métricas"""
    def monitor_worker():
        while True:
            try:
                performance_monitor.collect_metrics()
                time.sleep(300)  # 5 minutos
            except Exception as e:
                logger.error(f"Erro no worker de monitoramento: {e}")
                time.sleep(60)  # 1 minuto em caso de erro
    
    thread = threading.Thread(target=monitor_worker, daemon=True, name="MonitoringScheduler")
    thread.start()
    logger.info("Sistema de monitoramento iniciado")

# === ROTAS DE API ===

@monitoring.route('/api/monitoring/health')
def health_check():
    """Endpoint de health check"""
    try:
        health_status = performance_monitor.get_health_status()
        status_code = 200
        
        if health_status.get("status") == "warning":
            status_code = 200  # Warning ainda é OK
        elif health_status.get("status") == "critical":
            status_code = 503  # Service Unavailable
        elif health_status.get("status") == "error":
            status_code = 500  # Internal Server Error
        
        return jsonify(health_status), status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@monitoring.route('/api/monitoring/metrics')
def get_metrics():
    """Endpoint para métricas detalhadas"""
    try:
        # Últimas métricas
        with performance_monitor._lock:
            recent_system = performance_monitor.metrics_history[-10:] if performance_monitor.metrics_history else []
            recent_db = performance_monitor.db_metrics_history[-10:] if performance_monitor.db_metrics_history else []
        
        return jsonify({
            "system_metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "disk_usage": m.disk_usage,
                    "active_connections": m.active_connections,
                    "response_time_avg": m.response_time_avg,
                    "error_rate": m.error_rate
                } for m in recent_system
            ],
            "database_metrics": [
                {
                    "timestamp": datetime.now().isoformat(),  # Assumindo timestamp atual
                    "total_rncs": m.total_rncs,
                    "active_rncs": m.active_rncs,
                    "finalized_rncs": m.finalized_rncs,
                    "total_users": m.total_users,
                    "active_users": m.active_users,
                    "database_size_mb": m.database_size_mb
                } for m in recent_db
            ]
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@monitoring.route('/api/monitoring/stats')
def get_statistics():
    """Estatísticas gerais do sistema"""
    try:
        uptime = datetime.now() - performance_monitor.start_time
        
        with performance_monitor._lock:
            avg_response_time = (
                sum(performance_monitor.response_times) / len(performance_monitor.response_times)
                if performance_monitor.response_times else 0
            )
        
        return jsonify({
            "uptime": {
                "seconds": int(uptime.total_seconds()),
                "formatted": str(uptime).split('.')[0]
            },
            "requests": {
                "total": performance_monitor.request_count,
                "errors": performance_monitor.error_count,
                "success_rate": (
                    ((performance_monitor.request_count - performance_monitor.error_count) / 
                     performance_monitor.request_count * 100) 
                    if performance_monitor.request_count > 0 else 100
                )
            },
            "performance": {
                "avg_response_time_ms": avg_response_time,
                "total_response_samples": len(performance_monitor.response_times)
            }
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# Middleware para monitoramento automático
def monitoring_middleware(app):
    """Middleware para capturar métricas de requisições"""
    
    @app.before_request
    def before_request():
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        try:
            if hasattr(request, 'start_time'):
                response_time = (time.time() - request.start_time) * 1000  # ms
                performance_monitor.record_request_time(response_time)
                
                # Registrar erro se status >= 400
                if response.status_code >= 400:
                    performance_monitor.record_error()
        except Exception as e:
            logger.error(f"Erro no middleware de monitoramento: {e}")
        
        return response
    
    return app
