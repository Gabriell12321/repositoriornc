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

# ===== Jinja filter: parse BRL currency to float =====
@print_reports.app_template_filter('parse_brl')
def _parse_brl_to_float(value):
    """Parse Brazilian currency string to float.
    
    Examples:
      'R$ 100,00' -> 100.0
      'R$ 1.234,56' -> 1234.56
      '100.00' -> 100.0
      None or '' -> 0.0
    """
    try:
        if value is None or value == '':
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        
        s = str(value).strip()
        # Remove currency symbols, quotes, and spaces
        for ch in ['R$', '$', ' ', '\"', '"', "'"]:
            s = s.replace(ch, '')
        
        # Determine format based on separators
        if ',' in s and '.' in s:
            # BR format: thousands '.' and decimal ','
            s = s.replace('.', '').replace(',', '.')
        elif ',' in s and '.' not in s:
            # Only comma -> decimal comma
            s = s.replace(',', '.')
        # else: only dot or no separator -> keep as is
        
        return float(s) if s and s not in ('-',) else 0.0
    except Exception:
        return 0.0

# ===== Jinja filter: format numbers in BRL style (1.234,56) =====
@print_reports.app_template_filter('brl')
def _format_brl_number(value):
    """Return number formatted in Brazilian style without currency symbol.

    Examples:
      1234.5 -> '1.234,50'
      'R$ 3,45' -> '3,45'
    """
    try:
        # Normalize to float
        if value is None or value == '':
            num = 0.0
        elif isinstance(value, (int, float)):
            num = float(value)
        else:
            s = str(value).strip()
            # Remove currency and quotes/spaces
            for ch in ['R$', '$', ' ', '\"', '"', "'"]:
                s = s.replace(ch, '')
            # Decide how to parse depending on separators present
            if ',' in s and '.' in s:
                # Assume BR format: thousands '.' and decimal ','
                s = s.replace('.', '').replace(',', '.')
            elif ',' in s and '.' not in s:
                # Only comma present -> decimal comma
                s = s.replace(',', '.')
            else:
                # Only dot or none -> keep as is
                s = s
            num = float(s) if s not in ('', '-',) else 0.0

        # Format with thousands comma and dot decimal, then swap
        txt = f"{num:,.2f}"
        return txt.replace(',', 'X').replace('.', ',').replace('X', '.')
    except Exception:
        return '0,00'

# With currency symbol
@print_reports.app_template_filter('brl_money')
def _format_brl_money(value):
    try:
        return f"R$ {_format_brl_number(value)}"
    except Exception:
        return 'R$ 0,00'
# Also expose a helper for direct use in templates if needed
@print_reports.app_context_processor
def _inject_brl_helpers():
    return {
        'format_brl': _format_brl_number,
        'format_brl_money': _format_brl_money,
    }

# ===== Função para remover duplicatas Máquina/Funcionário =====
def remove_duplicates_maquina_funcionario(rncs_list):
    """
    Remove duplicatas de RNCs quando Máquina e Funcionário têm o mesmo valor.
    
    Lógica:
    1. Agrupa RNCs por (responsavel, price)
    2. Se houver múltiplas RNCs com mesmo responsável e mesmo valor:
       - Verifica se há uma com 'Máquina' e outra com 'Funcionário' no título/descrição
       - Se sim: mantém apenas 'Funcionário', descarta 'Máquina'
    3. Caso contrário: mantém todas as RNCs
    
    Exemplo:
        Input:
            - RNC-001: João, R$ 1000, título="Máquina X"
            - RNC-002: João, R$ 1000, título="Funcionário João"
        Output:
            - RNC-002: João, R$ 1000, título="Funcionário João"
    """
    if not rncs_list:
        return []
    
    # Agrupar por (responsavel, price)
    from collections import defaultdict
    groups = defaultdict(list)
    
    for rnc in rncs_list:
        responsavel = rnc.get('responsavel') or rnc.get('creator_name') or 'Sistema'
        price = rnc.get('price', 0)
        
        # Normalizar price para float
        try:
            if isinstance(price, str):
                # Remover R$, espaços, vírgulas
                price_clean = price.replace('R$', '').replace(' ', '').replace(',', '').replace('"', '').replace("'", '')
                price_float = float(price_clean) if price_clean else 0.0
            else:
                price_float = float(price) if price else 0.0
        except:
            price_float = 0.0
        
        # Chave: (responsavel, price_arredondado)
        key = (responsavel, round(price_float, 2))
        groups[key].append(rnc)
    
    # Processar cada grupo
    result = []
    for (responsavel, price), group in groups.items():
        if len(group) == 1:
            # Apenas 1 RNC com esse responsável e valor → manter
            result.append(group[0])
        else:
            # Múltiplas RNCs → verificar se há Máquina + Funcionário
            has_maquina = False
            has_funcionario = False
            maquina_rnc = None
            funcionario_rnc = None
            
            for rnc in group:
                title = (rnc.get('title') or '').lower()
                description = (rnc.get('description') or '').lower()
                text = f"{title} {description}"
                
                if 'máquina' in text or 'maquina' in text:
                    has_maquina = True
                    maquina_rnc = rnc
                
                if 'funcionário' in text or 'funcionario' in text:
                    has_funcionario = True
                    funcionario_rnc = rnc
            
            if has_maquina and has_funcionario:
                # ✅ Duplicata detectada: Máquina + Funcionário com mesmo valor
                # Manter apenas Funcionário
                if funcionario_rnc:
                    result.append(funcionario_rnc)
                    print(f"🔍 Duplicata removida: {responsavel} - R$ {price:.2f} (mantido Funcionário, removido Máquina)")
                else:
                    # Fallback: manter todos
                    result.extend(group)
            else:
                # Não é caso Máquina+Funcionário → manter todos
                result.extend(group)
    
    print(f"📊 RNCs antes: {len(rncs_list)} | RNCs depois: {len(result)} | Removidas: {len(rncs_list) - len(result)}")
    return result

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
    
    # Permission check for reports access
    try:
        if not has_permission(session['user_id'], 'view_reports'):
            return redirect('/dashboard?error=access_denied')
    except Exception:
        return redirect('/dashboard?error=access_denied')
    return render_template('reports/reports_menu.html')

@print_reports.route('/reports/date_selection')
def date_selection():
    """Página de seleção de datas para relatórios"""
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    
    # Permission check for reports access
    try:
        if not has_permission(session['user_id'], 'view_reports'):
            return redirect('/dashboard?error=access_denied')
    except Exception:
        return redirect('/dashboard?error=access_denied')
    return render_template('reports/date_selection.html')

@print_reports.route('/reports/generate')
def generate_report():
    """Gera relatório de RNCs finalizados"""
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    # Permission check for reports generation
    try:
        if not has_permission(session['user_id'], 'view_reports'):
            return redirect('/dashboard?error=access_denied')
    except Exception:
        return redirect('/dashboard?error=access_denied')
    
    # Obter parâmetros da URL
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    report_type = request.args.get('type', 'finalized')
    
    # DEBUG: Mostrar parâmetros recebidos
    print(f"\n=== PARÂMETROS RECEBIDOS ===")
    print(f"start_date: {start_date}")
    print(f"end_date: {end_date}")
    print(f"report_type: {report_type}")
    print(f"============================\n")
    
    # Se não foram fornecidas datas, mostrar formulário de seleção
    if not start_date or not end_date:
        return render_template('reports/date_selection.html')
    
    try:
        # Buscar RNCs baseado no tipo de relatório
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # DEBUG: Verificar quantas RNCs existem no total
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
        total_rncs = cursor.fetchone()[0]
        print(f"Total de RNCs ativas no banco: {total_rncs}")
        
        # DEBUG: Verificar RNCs no período
        cursor.execute("""
            SELECT COUNT(*), MIN(created_at), MAX(created_at) 
            FROM rncs 
            WHERE is_deleted = 0 
            AND DATE(created_at) BETWEEN ? AND ?
        """, (start_date, end_date))
        period_info = cursor.fetchone()
        print(f"RNCs no período {start_date} a {end_date}: {period_info[0]}")
        print(f"Data mais antiga: {period_info[1]}, Data mais recente: {period_info[2]}")
        
        if report_type == 'finalized':
            # Relatório de RNCs finalizados
            # CORRIGIDO: Usar created_at porque finalized_at está NULL para todas as RNCs
            query = """
                SELECT r.*, u.name as creator_name, u.department as creator_department,
                       au.name as assigned_user_name, au.department as assigned_department
                FROM rncs r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN users au ON r.assigned_user_id = au.id
                WHERE r.is_deleted = 0 
                AND r.status = 'Finalizado'
                AND DATE(r.created_at) BETWEEN ? AND ?
                ORDER BY r.created_at DESC
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
            # CORRIGIDO: Incluir TODAS as RNCs finalizadas, mesmo sem responsável
            # O template agrupará por área/setor quando não houver responsável
            query = """
                SELECT r.*, 
                       COALESCE(NULLIF(r.responsavel, ''), 'Não informado') as creator_name,
                       CASE 
                           WHEN r.area_responsavel IS NOT NULL AND r.area_responsavel != '' THEN r.area_responsavel
                           WHEN r.setor IS NOT NULL AND r.setor != '' THEN r.setor
                           ELSE 'Não informado'
                       END as creator_department,
                       COALESCE(NULLIF(r.responsavel, ''), 'Não informado') as assigned_user_name,
                       CASE 
                           WHEN r.area_responsavel IS NOT NULL AND r.area_responsavel != '' THEN r.area_responsavel
                           WHEN r.setor IS NOT NULL AND r.setor != '' THEN r.setor
                           ELSE 'Não informado'
                       END as assigned_department
                FROM rncs r
                WHERE r.is_deleted = 0 
                AND r.status = 'Finalizado'
                AND DATE(r.created_at) BETWEEN ? AND ?
                ORDER BY creator_department, creator_name, r.created_at DESC
            """
            template = 'reports/by_operator_report.html'
            stats = calculate_operator_stats_period(cursor, start_date, end_date)
            
        elif report_type == 'by_sector':
            # Relatório por setor/departamento (usando area_responsavel ou setor)
            # CORRIGIDO: substituir r.department pela resolução dinâmica.
            query = """
                SELECT r.*, 
                       CASE 
                           WHEN r.area_responsavel IS NOT NULL AND r.area_responsavel != '' THEN r.area_responsavel
                           WHEN r.setor IS NOT NULL AND r.setor != '' THEN r.setor
                           ELSE 'Não informado'
                       END as creator_department,
                       r.responsavel as creator_name,
                       CASE 
                           WHEN r.area_responsavel IS NOT NULL AND r.area_responsavel != '' THEN r.area_responsavel
                           WHEN r.setor IS NOT NULL AND r.setor != '' THEN r.setor
                           ELSE 'Não informado'
                       END as assigned_department,
                       r.responsavel as assigned_user_name,
                       CASE 
                           WHEN (r.area_responsavel = 'Engenharia' OR r.setor = 'Engenharia') THEN 'Engenharia'
                           WHEN (r.area_responsavel = 'Qualidade' OR r.setor = 'Qualidade') THEN 'Qualidade'
                           WHEN (r.area_responsavel = 'TI' OR r.setor = 'TI') THEN 'TI'
                           WHEN (r.area_responsavel = 'Produção' OR r.setor = 'Produção') THEN 'Produção'
                           WHEN (r.area_responsavel = 'Compras' OR r.setor = 'Compras') THEN 'Compras'
                           WHEN (r.area_responsavel = 'Administração' OR r.setor = 'Administração') THEN 'Administrador'
                           WHEN (r.area_responsavel = 'Terceiros' OR r.setor = 'Terceiros') THEN 'Terceiros'
                           ELSE 'Outros'
                       END as group_name
                FROM rncs r
                WHERE r.is_deleted = 0 
                AND DATE(r.created_at) BETWEEN ? AND ?
                ORDER BY group_name, creator_department, r.created_at DESC
            """
            template = 'reports/by_sector_report_simple.html'
            stats = calculate_sector_stats_period(cursor, start_date, end_date)
            
        else:
            return "Tipo de relatório não reconhecido", 400
        
        cursor.execute(query, (start_date, end_date))
        rncs = cursor.fetchall()
        
        # Obter colunas
        columns = [desc[0] for desc in cursor.description]
        rncs_list = [dict(zip(columns, rnc)) for rnc in rncs]
        
        # ✅ CORREÇÃO: Remover duplicatas Máquina/Funcionário com mesmo valor
        if report_type == 'by_operator':
            rncs_list = remove_duplicates_maquina_funcionario(rncs_list)
        
        # DEBUG: Imprimir informações sobre a consulta
        print(f"\n=== DEBUG RELATÓRIO ===")
        print(f"Tipo: {report_type}")
        print(f"Período: {start_date} a {end_date}")
        print(f"Query executada: {query[:200]}...")
        print(f"Total de RNCs encontradas: {len(rncs_list)}")
        if rncs_list:
            print(f"Primeira RNC: {rncs_list[0]}")
            # DEBUG: Ver valores do campo price
            print(f"\n=== DEBUG PREÇOS ===")
            for i, rnc in enumerate(rncs_list[:5]):  # Primeiras 5 RNCs
                print(f"RNC {rnc.get('rnc_number', 'N/A')}: price='{rnc.get('price')}' (tipo: {type(rnc.get('price'))})")
            print(f"====================\n")
        print(f"Stats calculadas: {stats}")
        print(f"======================\n")
        
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
    # CORRIGIDO: Usar area_responsavel da RNC, não u.department do usuário
    cursor.execute("""
        SELECT 
            CASE 
                WHEN r.area_responsavel IS NOT NULL AND r.area_responsavel != '' THEN r.area_responsavel
                WHEN r.setor IS NOT NULL AND r.setor != '' THEN r.setor
                ELSE 'Não informado'
            END as departamento,
            COUNT(*) 
        FROM rncs r
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY departamento
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
    # CORRIGIDO: Usar created_at porque finalized_at está NULL
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND status = 'Finalizado'
        AND DATE(created_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    stats['total_finalized'] = cursor.fetchone()[0]
    
    # RNCs finalizados por departamento no período
    # CORRIGIDO: Usar area_responsavel da RNC, não u.department do usuário
    cursor.execute("""
        SELECT 
            CASE 
                WHEN r.area_responsavel IS NOT NULL AND r.area_responsavel != '' THEN r.area_responsavel
                WHEN r.setor IS NOT NULL AND r.setor != '' THEN r.setor
                ELSE 'Não informado'
            END as departamento,
            COUNT(*) 
        FROM rncs r
        WHERE r.is_deleted = 0 AND r.status = 'Finalizado'
        AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY departamento
    """, (start_date, end_date))
    stats['by_department'] = dict(cursor.fetchall())
    
    # RNCs finalizados por prioridade no período
    cursor.execute("""
        SELECT priority, COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND status = 'Finalizado'
        AND DATE(created_at) BETWEEN ? AND ?
        GROUP BY priority
    """, (start_date, end_date))
    stats['by_priority'] = dict(cursor.fetchall())
    
    # Valor total dos RNCs finalizados no período
    # CORRIGIDO: Remover 'R$', espaços, vírgulas e aspas do price antes de fazer o CAST
    cursor.execute("""
        SELECT SUM(CAST(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(price, 'R$', ''), ' ', ''), ',', ''), '"', ''), '''', '') AS REAL)) FROM rncs 
        WHERE is_deleted = 0 AND status = 'Finalizado'
        AND DATE(created_at) BETWEEN ? AND ?
        AND price IS NOT NULL AND price != '' AND price != '0' AND price != '0.0'
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
    # CORRIGIDO: Usar area_responsavel da RNC, não u.department do usuário
    cursor.execute("""
        SELECT 
            CASE 
                WHEN r.area_responsavel IS NOT NULL AND r.area_responsavel != '' THEN r.area_responsavel
                WHEN r.setor IS NOT NULL AND r.setor != '' THEN r.setor
                ELSE 'Não informado'
            END as departamento,
            COUNT(*) 
        FROM rncs r
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY departamento
    """, (start_date, end_date))
    stats['by_department'] = dict(cursor.fetchall())
    
    # Valor total
    # CORRIGIDO: Remover 'R$', espaços, vírgulas e aspas do price antes de fazer o CAST
    cursor.execute("""
        SELECT SUM(CAST(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(price, 'R$', ''), ' ', ''), ',', ''), '"', ''), '''', '') AS REAL)) FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
        AND price IS NOT NULL AND price != '' AND price != '0' AND price != '0.0'
    """, (start_date, end_date))
    result = cursor.fetchone()
    stats['total_value'] = result[0] if result[0] else 0
    
    return stats

def calculate_operator_stats_period(cursor, start_date, end_date):
    """Calcula estatísticas para relatório por operador"""
    stats = {}
    
    # Total de RNCs finalizadas no período
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 
        AND status = 'Finalizado'
        AND DATE(created_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    stats['total_rncs'] = cursor.fetchone()[0]
    
    # RNCs por operador (usando r.responsavel direto se existir)
    cursor.execute("""
        SELECT 
            COALESCE(NULLIF(r.responsavel, ''), u.name, 'Não informado') as operador,
            COUNT(*) 
        FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.is_deleted = 0 
        AND r.status = 'Finalizado'
        AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY operador
        ORDER BY COUNT(*) DESC
    """, (start_date, end_date))
    stats['by_operator'] = dict(cursor.fetchall())

    # Valor por operador (sanitizando campo price que pode conter R$, vírgulas etc.)
    cursor.execute("""
        SELECT 
            COALESCE(NULLIF(r.responsavel, ''), u.name, 'Não informado') as operador,
            SUM(CAST(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(r.price, 'R$', ''), ' ', ''), ',', ''), '"', ''), '''', '') AS REAL))
        FROM rncs r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.is_deleted = 0 
        AND r.status = 'Finalizado'
        AND DATE(r.created_at) BETWEEN ? AND ?
          AND r.price IS NOT NULL AND r.price != '' AND r.price NOT IN ('0','0.0')
        GROUP BY operador
        ORDER BY SUM(CAST(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(r.price, 'R$', ''), ' ', ''), ',', ''), '"', ''), '''', '') AS REAL)) DESC
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
    
    # RNCs por setor (usando area_responsavel ou setor)
    dept_case = """
        CASE 
            WHEN r.area_responsavel IS NOT NULL AND r.area_responsavel != '' THEN r.area_responsavel
            WHEN r.setor IS NOT NULL AND r.setor != '' THEN r.setor
            ELSE 'Não informado'
        END
    """
    cursor.execute(f"""
        SELECT {dept_case} as departamento, COUNT(*) FROM rncs r
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY departamento
        ORDER BY COUNT(*) DESC
    """, (start_date, end_date))
    stats['by_sector'] = dict(cursor.fetchall())
    
    # Valor por setor (sanitizando price)
    cursor.execute(f"""
        SELECT {dept_case} as departamento, 
               SUM(CAST(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(r.price, 'R$', ''), ' ', ''), ',', ''), '"', ''), '''', '') AS REAL)) 
        FROM rncs r
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
          AND r.price IS NOT NULL AND r.price != '' AND r.price NOT IN ('0','0.0')
        GROUP BY departamento
        ORDER BY SUM(CAST(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(r.price, 'R$', ''), ' ', ''), ',', ''), '"', ''), '''', '') AS REAL)) DESC
    """, (start_date, end_date))
    stats['value_by_sector'] = dict(cursor.fetchall())
    
    # RNCs por status por setor
    cursor.execute(f"""
        SELECT {dept_case} as departamento, r.status, COUNT(*) FROM rncs r
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY departamento, r.status
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
    
    # RNCs finalizados por departamento (usar campos da própria RNC)
    cursor.execute("""
        SELECT 
            CASE 
                WHEN r.area_responsavel IS NOT NULL AND r.area_responsavel != '' THEN r.area_responsavel
                WHEN r.setor IS NOT NULL AND r.setor != '' THEN r.setor
                ELSE 'Não informado'
            END as departamento,
            COUNT(*)
        FROM rncs r
        WHERE r.is_deleted = 0 AND r.status = 'Finalizado'
        GROUP BY departamento
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
    # CORRIGIDO: Remover 'R$', espaços, vírgulas e aspas do price antes de fazer o CAST
    cursor.execute("""
        SELECT SUM(CAST(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(price, 'R$', ''), ' ', ''), ',', ''), '"', ''), '''', '') AS REAL)) FROM rncs 
        WHERE is_deleted = 0 AND status = 'Finalizado'
        AND price IS NOT NULL AND price != '' AND price != '0' AND price != '0.0'
    """)
    result = cursor.fetchone()
    stats['total_value'] = result[0] if result[0] else 0
    
    return stats
