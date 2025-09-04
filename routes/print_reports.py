#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas para Relatórios de Impressão - IPPEL
Funcionalidades específicas para gerar relatórios otimizados para impressão
"""

import sqlite3
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, render_template, session, redirect, url_for
from services.db import DB_PATH, get_db_connection, return_db_connection
from services.permissions import has_permission

print_reports = Blueprint('print_reports', __name__)

@print_reports.route('/report/print_rnc')
def print_rnc_report():
    """Gera relatório de RNCs otimizado para impressão"""
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    
    # Verificar permissão
    if not has_permission(session['user_id'], 'can_print_reports'):
        return "Você não tem permissão para imprimir relatórios", 403
    
    # Parâmetros da URL
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    format_type = request.args.get('format', 'detailed')
    
    if not start_date or not end_date:
        return "Parâmetros de data são obrigatórios", 400
    
    try:
        # Buscar RNCs no período
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query base para buscar RNCs
        query = """
            SELECT r.*, u.name as creator_name, u.department as creator_department,
                   au.name as assigned_user_name, au.department as assigned_department
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN users au ON r.assigned_user_id = au.id
            WHERE r.is_deleted = 0 
            AND DATE(r.created_at) BETWEEN ? AND ?
            ORDER BY r.created_at DESC
        """
        
        cursor.execute(query, (start_date, end_date))
        rncs = cursor.fetchall()
        
        # Obter colunas
        columns = [desc[0] for desc in cursor.description]
        rncs_list = [dict(zip(columns, rnc)) for rnc in rncs]
        
        # Estatísticas resumidas
        stats = calculate_report_stats(cursor, start_date, end_date)
        
        return_db_connection(conn)
        
        # Renderizar template baseado no formato
        if format_type == 'summary':
            return render_template('reports/print_summary.html', 
                                 rncs=rncs_list, 
                                 stats=stats,
                                 start_date=start_date,
                                 end_date=end_date,
                                 generated_at=datetime.now())
        elif format_type == 'charts':
            return render_template('reports/print_charts.html', 
                                 rncs=rncs_list, 
                                 stats=stats,
                                 start_date=start_date,
                                 end_date=end_date,
                                 generated_at=datetime.now())
        else:  # detailed
            return render_template('reports/print_detailed.html', 
                                 rncs=rncs_list, 
                                 stats=stats,
                                 start_date=start_date,
                                 end_date=end_date,
                                 generated_at=datetime.now())
                                 
    except Exception as e:
        return f"Erro ao gerar relatório: {str(e)}", 500

@print_reports.route('/reports/menu')
def reports_menu():
    """Menu de seleção de relatórios"""
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    
    return render_template('reports/reports_menu.html')

@print_reports.route('/reports/date_selection')
def date_selection():
    """Página de seleção de datas para relatórios"""
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    
    return render_template('reports/date_selection.html')

@print_reports.route('/reports/generate')
def generate_report():
    """Gera relatório de RNCs finalizados"""
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    
    # Obter parâmetros da URL
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    report_type = request.args.get('type', 'finalized')
    
    # Se não foram fornecidas datas, mostrar formulário de seleção
    if not start_date or not end_date:
        return render_template('reports/date_selection.html')
    
    try:
        # Buscar RNCs baseado no tipo de relatório
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if report_type == 'finalized':
            # Relatório de RNCs finalizados
            query = """
                SELECT r.*, u.name as creator_name, u.department as creator_department,
                       au.name as assigned_user_name, au.department as assigned_department
                FROM rncs r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN users au ON r.assigned_user_id = au.id
                WHERE r.is_deleted = 0 
                AND r.status = 'Finalizado'
                AND DATE(r.finalized_at) BETWEEN ? AND ?
                ORDER BY r.finalized_at DESC
            """
            template = 'reports/finalized_rncs_report.html'
            stats = calculate_finalized_stats_period(cursor, start_date, end_date)
            
        elif report_type == 'total_detailed':
            # Relatório total detalhado
            query = """
                SELECT r.*, u.name as creator_name, u.department as creator_department,
                       au.name as assigned_user_name, au.department as assigned_department
                FROM rncs r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN users au ON r.assigned_user_id = au.id
                WHERE r.is_deleted = 0 
                AND DATE(r.created_at) BETWEEN ? AND ?
                ORDER BY r.created_at DESC
            """
            template = 'reports/total_detailed_report.html'
            stats = calculate_total_stats_period(cursor, start_date, end_date)
            
        elif report_type == 'by_operator':
            # Relatório por operador
            query = """
                SELECT r.*, u.name as creator_name, u.department as creator_department,
                       au.name as assigned_user_name, au.department as assigned_department
                FROM rncs r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN users au ON r.assigned_user_id = au.id
                WHERE r.is_deleted = 0 
                AND DATE(r.created_at) BETWEEN ? AND ?
                ORDER BY u.name, r.created_at DESC
            """
            template = 'reports/by_operator_report.html'
            stats = calculate_operator_stats_period(cursor, start_date, end_date)
            
        elif report_type == 'by_sector':
            # Relatório por setor
            query = """
                SELECT r.*, u.name as creator_name, u.department as creator_department,
                       au.name as assigned_user_name, au.department as assigned_department
                FROM rncs r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN users au ON r.assigned_user_id = au.id
                WHERE r.is_deleted = 0 
                AND DATE(r.created_at) BETWEEN ? AND ?
                ORDER BY u.department, r.created_at DESC
            """
            template = 'reports/by_sector_report.html'
            stats = calculate_sector_stats_period(cursor, start_date, end_date)
            
        else:
            return "Tipo de relatório não reconhecido", 400
        
        cursor.execute(query, (start_date, end_date))
        rncs = cursor.fetchall()
        
        # Obter colunas
        columns = [desc[0] for desc in cursor.description]
        rncs_list = [dict(zip(columns, rnc)) for rnc in rncs]
        
        return_db_connection(conn)
        
        # Renderizar template do relatório
        return render_template(template, 
                             rncs=rncs_list, 
                             stats=stats,
                             start_date=start_date,
                             end_date=end_date,
                             report_type=report_type,
                             generated_at=datetime.now())
                             
    except Exception as e:
        return f"Erro ao gerar relatório: {str(e)}", 500

def calculate_report_stats(cursor, start_date, end_date):
    """Calcula estatísticas para o relatório"""
    stats = {}
    
    # Total de RNCs
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    stats['total_rncs'] = cursor.fetchone()[0]
    
    # RNCs por status
    cursor.execute("""
        SELECT status, COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
        GROUP BY status
    """, (start_date, end_date))
    stats['by_status'] = dict(cursor.fetchall())
    
    # RNCs por prioridade
    cursor.execute("""
        SELECT priority, COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
        GROUP BY priority
    """, (start_date, end_date))
    stats['by_priority'] = dict(cursor.fetchall())
    
    # RNCs por departamento
    cursor.execute("""
        SELECT u.department, COUNT(*) FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY u.department
    """, (start_date, end_date))
    stats['by_department'] = dict(cursor.fetchall())
    
    # RNCs finalizados vs pendentes
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN status = 'Finalizado' THEN 1 ELSE 0 END) as finalized,
            SUM(CASE WHEN status != 'Finalizado' THEN 1 ELSE 0 END) as pending
        FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    result = cursor.fetchone()
    stats['finalized'] = result[0] or 0
    stats['pending'] = result[1] or 0
    
    # Taxa de resolução
    if stats['total_rncs'] > 0:
        stats['resolution_rate'] = round((stats['finalized'] / stats['total_rncs']) * 100, 1)
    else:
        stats['resolution_rate'] = 0
    
    return stats

def calculate_finalized_stats_period(cursor, start_date, end_date):
    """Calcula estatísticas dos RNCs finalizados em um período específico"""
    stats = {}
    
    # Total de RNCs finalizados no período
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND status = 'Finalizado'
        AND DATE(finalized_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    stats['total_finalized'] = cursor.fetchone()[0]
    
    # RNCs finalizados por departamento no período
    cursor.execute("""
        SELECT u.department, COUNT(*) FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.is_deleted = 0 AND r.status = 'Finalizado'
        AND DATE(r.finalized_at) BETWEEN ? AND ?
        GROUP BY u.department
    """, (start_date, end_date))
    stats['by_department'] = dict(cursor.fetchall())
    
    # RNCs finalizados por prioridade no período
    cursor.execute("""
        SELECT priority, COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND status = 'Finalizado'
        AND DATE(finalized_at) BETWEEN ? AND ?
        GROUP BY priority
    """, (start_date, end_date))
    stats['by_priority'] = dict(cursor.fetchall())
    
    # Valor total dos RNCs finalizados no período
    cursor.execute("""
        SELECT SUM(CAST(price AS REAL)) FROM rncs 
        WHERE is_deleted = 0 AND status = 'Finalizado'
        AND DATE(finalized_at) BETWEEN ? AND ?
        AND price IS NOT NULL AND price != ''
    """, (start_date, end_date))
    result = cursor.fetchone()
    stats['total_value'] = result[0] if result[0] else 0
    
    return stats

def calculate_total_stats_period(cursor, start_date, end_date):
    """Calcula estatísticas para relatório total detalhado"""
    stats = {}
    
    # Total de RNCs no período
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    stats['total_rncs'] = cursor.fetchone()[0]
    
    # RNCs por status
    cursor.execute("""
        SELECT status, COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
        GROUP BY status
    """, (start_date, end_date))
    stats['by_status'] = dict(cursor.fetchall())
    
    # RNCs por prioridade
    cursor.execute("""
        SELECT priority, COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
        GROUP BY priority
    """, (start_date, end_date))
    stats['by_priority'] = dict(cursor.fetchall())
    
    # RNCs por departamento
    cursor.execute("""
        SELECT u.department, COUNT(*) FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY u.department
    """, (start_date, end_date))
    stats['by_department'] = dict(cursor.fetchall())
    
    # Valor total
    cursor.execute("""
        SELECT SUM(CAST(price AS REAL)) FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
        AND price IS NOT NULL AND price != ''
    """, (start_date, end_date))
    result = cursor.fetchone()
    stats['total_value'] = result[0] if result[0] else 0
    
    return stats

def calculate_operator_stats_period(cursor, start_date, end_date):
    """Calcula estatísticas para relatório por operador"""
    stats = {}
    
    # Total de RNCs no período
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    stats['total_rncs'] = cursor.fetchone()[0]
    
    # RNCs por operador
    cursor.execute("""
        SELECT u.name, COUNT(*) FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY u.name
        ORDER BY COUNT(*) DESC
    """, (start_date, end_date))
    stats['by_operator'] = dict(cursor.fetchall())
    
    # Valor por operador
    cursor.execute("""
        SELECT u.name, SUM(CAST(r.price AS REAL)) FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        AND r.price IS NOT NULL AND r.price != ''
        GROUP BY u.name
        ORDER BY SUM(CAST(r.price AS REAL)) DESC
    """, (start_date, end_date))
    stats['value_by_operator'] = dict(cursor.fetchall())
    
    return stats

def calculate_sector_stats_period(cursor, start_date, end_date):
    """Calcula estatísticas para relatório por setor"""
    stats = {}
    
    # Total de RNCs no período
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    stats['total_rncs'] = cursor.fetchone()[0]
    
    # RNCs por setor
    cursor.execute("""
        SELECT u.department, COUNT(*) FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY u.department
        ORDER BY COUNT(*) DESC
    """, (start_date, end_date))
    stats['by_sector'] = dict(cursor.fetchall())
    
    # Valor por setor
    cursor.execute("""
        SELECT u.department, SUM(CAST(r.price AS REAL)) FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        AND r.price IS NOT NULL AND r.price != ''
        GROUP BY u.department
        ORDER BY SUM(CAST(r.price AS REAL)) DESC
    """, (start_date, end_date))
    stats['value_by_sector'] = dict(cursor.fetchall())
    
    # RNCs por status por setor
    cursor.execute("""
        SELECT u.department, r.status, COUNT(*) FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY u.department, r.status
    """, (start_date, end_date))
    sector_status = cursor.fetchall()
    stats['sector_status'] = {}
    for dept, status, count in sector_status:
        if dept not in stats['sector_status']:
            stats['sector_status'][dept] = {}
        stats['sector_status'][dept][status] = count
    
    return stats

def calculate_finalized_stats(cursor):
    """Calcula estatísticas dos RNCs finalizados (todos)"""
    stats = {}
    
    # Total de RNCs finalizados
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND status = 'Finalizado'
    """)
    stats['total_finalized'] = cursor.fetchone()[0]
    
    # RNCs finalizados por departamento
    cursor.execute("""
        SELECT u.department, COUNT(*) FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.is_deleted = 0 AND r.status = 'Finalizado'
        GROUP BY u.department
    """)
    stats['by_department'] = dict(cursor.fetchall())
    
    # RNCs finalizados por prioridade
    cursor.execute("""
        SELECT priority, COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND status = 'Finalizado'
        GROUP BY priority
    """)
    stats['by_priority'] = dict(cursor.fetchall())
    
    # RNCs finalizados por mês (últimos 12 meses)
    cursor.execute("""
        SELECT strftime('%Y-%m', finalized_at) as month, COUNT(*) 
        FROM rncs 
        WHERE is_deleted = 0 AND status = 'Finalizado'
        AND finalized_at >= date('now', '-12 months')
        GROUP BY strftime('%Y-%m', finalized_at)
        ORDER BY month DESC
    """)
    stats['by_month'] = dict(cursor.fetchall())
    
    # Valor total dos RNCs finalizados
    cursor.execute("""
        SELECT SUM(CAST(price AS REAL)) FROM rncs 
        WHERE is_deleted = 0 AND status = 'Finalizado'
        AND price IS NOT NULL AND price != ''
    """)
    result = cursor.fetchone()
    stats['total_value'] = result[0] if result[0] else 0
    
    return stats
