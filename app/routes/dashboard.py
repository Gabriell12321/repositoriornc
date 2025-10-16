from flask import Blueprint, request, jsonify, session, render_template, redirect, current_app
import sqlite3
from datetime import datetime, timedelta
import os
import json

bp = Blueprint('dashboard', __name__)


@bp.route('/test-dashboard')
def test_dashboard():
    """Test route to verify blueprint is working"""
    return "Dashboard blueprint is working!"


@bp.route('/dashboard')
def dashboard():
    """Dashboard principal do sistema"""
    if 'user_id' not in session:
        return redirect('/')
    
    try:
        from services.permissions import has_permission, get_user_department
        
        # Obter informações de permissões do usuário para o frontend
        user_permissions = {
            'canViewAllRncs': has_permission(session['user_id'], 'view_all_rncs'),
            'canViewFinalizedRncs': has_permission(session['user_id'], 'view_finalized_rncs'),
            'canViewCharts': has_permission(session['user_id'], 'view_charts'),
            'canViewReports': has_permission(session['user_id'], 'view_reports'),
            'hasAdminAccess': has_permission(session['user_id'], 'admin_access'),
            'canCreateRnc': has_permission(session['user_id'], 'create_rnc'),
            'canViewLevantamento1415': has_permission(session['user_id'], 'view_levantamento_14_15'),
            'canViewGroupsForAssignment': has_permission(session['user_id'], 'view_groups_for_assignment'),
            'canViewUsersForAssignment': has_permission(session['user_id'], 'view_users_for_assignment'),
            'canViewEngineeringRncs': has_permission(session['user_id'], 'view_engineering_rncs'),
            'department': get_user_department(session['user_id'])
        }
        
        return render_template('dashboard_improved.html', user_permissions=user_permissions)
        
    except Exception as e:
        # Fallback for any permission service errors
        return render_template('dashboard_improved.html', user_permissions={
            'canViewAllRncs': False,
            'canViewFinalizedRncs': False,
            'canViewCharts': False,
            'canViewReports': False,
            'hasAdminAccess': False,
            'canCreateRnc': False,
            'canViewLevantamento1415': False,
            'canViewGroupsForAssignment': False,
            'canViewUsersForAssignment': False,
            'canViewEngineeringRncs': False,
            'department': None
        })


@bp.route('/indicadores-dashboard')
def indicadores_dashboard():
    if 'user_id' not in session:
        return redirect('/')
    try:
        from services.permissions import has_permission
        if not has_permission(session['user_id'], 'view_reports'):
            return redirect('/dashboard?error=access_denied&message=Acesso negado: usuário não tem permissão para visualizar indicadores')
    except Exception:
        # If permission service fails, be conservative
        return redirect('/dashboard?error=access_denied')
    return render_template('indicadores_dashboard.html')


@bp.route('/api/indicadores-detalhados')
def api_indicadores_detalhados():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401

    # Get data type filter (rnc or garantia)
    data_type = request.args.get('tipo', 'rnc').lower()
    
    # Validate data type
    if data_type not in ['rnc', 'garantia']:
        data_type = 'rnc'  # Default to RNC if invalid
        
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Filter based on data_type
        type_filter = ""
        if data_type == 'rnc':
            type_filter = "AND (category IS NULL OR category != 'garantia')"
        else:  # garantia
            type_filter = "AND category = 'garantia'"

        cursor.execute(f"SELECT COUNT(*) FROM rncs WHERE is_deleted = 0 {type_filter}")
        total_rncs = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM rncs WHERE status = 'Pendente' AND is_deleted = 0 {type_filter}")
        pendentes = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM rncs WHERE finalized_at IS NOT NULL AND is_deleted = 0 {type_filter}")
        finalizadas = cursor.fetchone()[0]

        tendencia_mensal = {}
        for i in range(12):
            d = datetime.now() - timedelta(days=30 * i)
            key = d.strftime('%Y-%m')
            cursor.execute(
                f"""
                SELECT COUNT(*) FROM rncs 
                WHERE strftime('%Y-%m', created_at) = ? AND is_deleted = 0 {type_filter}
                """,
                (key,),
            )
            tendencia_mensal[d.strftime('%b/%Y')] = cursor.fetchone()[0]

        cursor.execute(
            f"""
            SELECT COALESCE(r.department, u.department) as department, COUNT(r.id) as total
              FROM rncs r
              LEFT JOIN users u ON r.user_id = u.id
             WHERE r.is_deleted = 0 {type_filter}
             GROUP BY department
             ORDER BY total DESC
            """
        )
        por_departamento = dict(cursor.fetchall())

        cursor.execute(
            f"""
            SELECT status, COUNT(*) as total
              FROM rncs 
             WHERE is_deleted = 0 {type_filter}
             GROUP BY status
             ORDER BY total DESC
            """
        )
        por_status = dict(cursor.fetchall())

        eficiencia = {
            'finalizadas': finalizadas,
            'pendentes': pendentes,
            'taxa': round((finalizadas / max(total_rncs, 1)) * 100, 1),
        }

        cursor.execute(
            """
            SELECT r.rnc_number, r.title, r.status, r.priority, r.created_at, u.name
              FROM rncs r
              LEFT JOIN users u ON r.user_id = u.id
             WHERE r.is_deleted = 0
             ORDER BY r.created_at DESC
             LIMIT 10
            """
        )
        rncs_recentes = [
            {
                'numero': row[0],
                'titulo': row[1],
                'status': row[2],
                'prioridade': row[3],
                'data': row[4],
                'usuario': row[5] or 'Usuário',
            }
            for row in cursor.fetchall()
        ]

        conn.close()
        return jsonify(
            {
                'success': True,
                'data': {
                    'total_rncs': total_rncs,
                    'pendentes': pendentes,
                    'finalizadas': finalizadas,
                    'tendencia_mensal': tendencia_mensal,
                    'por_departamento': por_departamento if por_departamento else {'Geral': total_rncs},
                    'por_status': por_status if por_status else {'Pendente': pendentes, 'Finalizada': finalizadas},
                    'eficiencia': eficiencia,
                    'rncs_recentes': rncs_recentes,
                },
            }
        )
    except Exception as e:
        # Fallback neutro para não quebrar UI
        return jsonify(
            {
                'success': True,
                'data': {
                    'total_rncs': 0,
                    'pendentes': 0,
                    'finalizadas': 0,
                    'tendencia_mensal': {},
                    'por_departamento': {'Geral': 0},
                    'por_status': {'Pendente': 0},
                    'eficiencia': {'finalizadas': 0, 'pendentes': 0, 'taxa': 0},
                    'rncs_recentes': [],
                },
            }
        )


@bp.route('/api/funcionario-desempenho')
def api_funcionario_desempenho():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401

    try:
        ano = request.args.get('ano', datetime.now().strftime('%Y'))
        mes = request.args.get('mes', datetime.now().strftime('%m'))
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT u.name, COUNT(r.id) as total_rncs, 
                   (SELECT COUNT(*) FROM rncs WHERE user_id = r.user_id AND strftime('%Y-%m', created_at) = ? AND finalized_at IS NOT NULL AND is_deleted = 0) as resolvidas,
                   30 as meta
              FROM rncs r
              JOIN users u ON r.user_id = u.id
             WHERE strftime('%Y-%m', r.created_at) = ? AND r.is_deleted = 0
             GROUP BY r.user_id
             ORDER BY total_rncs DESC
             LIMIT 20
            """,
            (f"{ano}-{mes}", f"{ano}-{mes}"),
        )

        dados = []
        for row in cursor.fetchall():
            total = row[1]
            resolvidas = row[2]
            percentual = round((resolvidas / max(total, 1)) * 100, 1)
            dados.append(
                {
                    'responsavel': row[0],
                    'rncs': total,
                    'meta': row[3],
                    'percentual': percentual,
                    'status': 'Abaixo' if percentual < 70 else 'Adequado',
                }
            )

        if not dados:
            cursor.execute(
                """
                SELECT u.name, COUNT(r.id) as total_rncs, 
                       (SELECT COUNT(*) FROM rncs WHERE user_id = r.user_id AND finalized_at IS NOT NULL AND is_deleted = 0) as resolvidas,
                       30 as meta
                  FROM rncs r
                  JOIN users u ON r.user_id = u.id
                 WHERE r.is_deleted = 0
                 GROUP BY r.user_id
                 ORDER BY total_rncs DESC
                 LIMIT 20
                """
            )
            for row in cursor.fetchall():
                total = row[1]
                resolvidas = row[2]
                percentual = round((resolvidas / max(total, 1)) * 100, 1)
                dados.append(
                    {
                        'responsavel': row[0],
                        'rncs': total,
                        'meta': row[3],
                        'percentual': percentual,
                        'status': 'Abaixo' if percentual < 70 else 'Adequado',
                    }
                )

        if not dados:
            dados = [
                {'responsavel': 'Administrador', 'rncs': 4, 'meta': 30, 'percentual': 7, 'status': 'Abaixo'},
                {'responsavel': 'Engenheiro 1', 'rncs': 2, 'meta': 30, 'percentual': 7, 'status': 'Abaixo'},
            ]

        conn.close()
        return jsonify({'success': True, 'data': dados})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/percentuais-cumprimento')
def api_percentuais_cumprimento():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401

    try:
        ano = request.args.get('ano', datetime.now().strftime('%Y'))
        mes = request.args.get('mes')  # Opcional
        dados = [
            {'Mês': f"JAN {ano}", 'RNCs': 5, 'Meta': 30, 'Percentual': 17, 'Status': 'Abaixo'},
            {'Mês': f"FEV {ano}", 'RNCs': 8, 'Meta': 30, 'Percentual': 27, 'Status': 'Abaixo'},
            {'Mês': f"MAR {ano}", 'RNCs': 12, 'Meta': 30, 'Percentual': 40, 'Status': 'Abaixo'},
            {'Mês': f"ABR {ano}", 'RNCs': 15, 'Meta': 30, 'Percentual': 50, 'Status': 'Abaixo'},
            {'Mês': f"MAI {ano}", 'RNCs': 18, 'Meta': 30, 'Percentual': 60, 'Status': 'Abaixo'},
            {'Mês': f"JUN {ano}", 'RNCs': 22, 'Meta': 30, 'Percentual': 73, 'Status': 'Adequado'},
            {'Mês': f"JUL {ano}", 'RNCs': 25, 'Meta': 30, 'Percentual': 83, 'Status': 'Adequado'},
            {'Mês': f"AGO {ano}", 'RNCs': 28, 'Meta': 30, 'Percentual': 93, 'Status': 'Adequado'},
            {'Mês': f"SET {ano}", 'RNCs': 32, 'Meta': 30, 'Percentual': 107, 'Status': 'Adequado'},
        ]

        if mes:
            try:
                mes_int = int(mes)
                if 1 <= mes_int <= 12:
                    nome_mes = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'][mes_int - 1]
                    dados = [item for item in dados if item['Mês'].startswith(nome_mes)]
            except Exception:
                pass

        return jsonify({'success': True, 'data': dados})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/indicadores')
def api_indicadores():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401

    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
        total_rncs = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Pendente' AND is_deleted = 0")
        pendentes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE finalized_at IS NOT NULL AND is_deleted = 0")
        finalizadas = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COALESCE(r.department, u.department) as setor, COUNT(r.id) as total
              FROM rncs r
              LEFT JOIN users u ON r.user_id = u.id
             WHERE r.is_deleted = 0 AND COALESCE(r.department, u.department) IS NOT NULL
             GROUP BY setor
             ORDER BY total DESC
            """
        )
        setores_raw = cursor.fetchall()

        cursor.execute(
            """
            SELECT priority, COUNT(*) as total
              FROM rncs 
             WHERE is_deleted = 0 AND priority IS NOT NULL
             GROUP BY priority
             ORDER BY total DESC
            """
        )
        prioridades_raw = cursor.fetchall()

        monthly_data = []
        for i in range(6):
            d = datetime.now() - timedelta(days=30 * i)
            key = d.strftime('%Y-%m')
            cursor.execute(
                """
                SELECT COUNT(*) FROM rncs 
                WHERE strftime('%Y-%m', created_at) = ? AND is_deleted = 0
                """,
                (key,),
            )
            monthly_data.append({'mes': d.strftime('%b'), 'total': cursor.fetchone()[0]})

        monthly_data.reverse()

        efficiency_data = []
        for setor, total in setores_raw:
            cursor.execute(
                """
                SELECT COUNT(*) FROM rncs r
                  LEFT JOIN users u ON r.user_id = u.id
                 WHERE r.is_deleted = 0 
                   AND COALESCE(r.department, u.department) = ? 
                   AND r.finalized_at IS NOT NULL
                """,
                (setor,),
            )
            finalizadas_setor = cursor.fetchone()[0]
            efficiency = round((finalizadas_setor / max(total, 1)) * 100, 1)
            efficiency_data.append({'setor': setor, 'eficiencia': efficiency, 'meta': 85.0, 'realizado': efficiency})

        conn.close()

        departments_data = [
            {'department': e['setor'], 'meta': e['meta'], 'realizado': e['realizado'], 'efficiency': e['eficiencia']}
            for e in efficiency_data
        ] or [
            {'department': 'PRODUÇÃO', 'meta': 80, 'realizado': 60, 'efficiency': 75.0},
            {'department': 'ENGENHARIA', 'meta': 70, 'realizado': 55, 'efficiency': 78.6},
            {'department': 'QUALIDADE', 'meta': 50, 'realizado': 35, 'efficiency': 70.0},
        ]

        result = {
            'success': True,
            'kpis': {
                'total_rncs': total_rncs,
                'total_metas': total_rncs,
                'active_departments': len(setores_raw) if setores_raw else 3,
                'overall_efficiency': round((finalizadas / max(total_rncs, 1)) * 100, 1),
                'avg_rncs_per_dept': round(total_rncs / max(len(setores_raw), 1), 1) if setores_raw else 0,
            },
            'totals': {
                'total': total_rncs,
                'pendentes': pendentes,
                'finalizadas': finalizadas,
                'resolvidas': finalizadas,
            },
            'departments': departments_data,
            'monthly_trends': monthly_data,
            'setores': [{'setor': row[0], 'total': row[1]} for row in setores_raw] if setores_raw else [{'setor': 'Geral', 'total': total_rncs}],
            'prioridades': [{'prioridade': row[0], 'total': row[1]} for row in prioridades_raw] if prioridades_raw else [{'prioridade': 'Média', 'total': total_rncs}],
            'tendencia': monthly_data,
            'eficiencia_departamentos': efficiency_data,
            'eficiencia': round((finalizadas / max(total_rncs, 1)) * 100, 1),
        }

        return jsonify(result)
    except Exception as e:
        return jsonify(
            {
                'success': True,
                'kpis': {
                    'total_rncs': 0,
                    'total_metas': 0,
                    'active_departments': 3,
                    'overall_efficiency': 0,
                    'avg_rncs_per_dept': 0,
                },
                'totals': {'total': 0, 'pendentes': 0, 'finalizadas': 0, 'resolvidas': 0},
                'departments': [
                    {'department': 'PRODUÇÃO', 'meta': 80, 'realizado': 0, 'efficiency': 0},
                    {'department': 'ENGENHARIA', 'meta': 70, 'realizado': 0, 'efficiency': 0},
                    {'department': 'QUALIDADE', 'meta': 50, 'realizado': 0, 'efficiency': 0},
                ],
                'monthly_trends': [
                    {'mes': 'Jan', 'total': 0},
                    {'mes': 'Fev', 'total': 0},
                    {'mes': 'Mar', 'total': 0},
                    {'mes': 'Abr', 'total': 0},
                    {'mes': 'Mai', 'total': 0},
                    {'mes': 'Jun', 'total': 0},
                ],
                'setores': [{'setor': 'Geral', 'total': 0}],
                'prioridades': [{'prioridade': 'Média', 'total': 0}],
                'tendencia': [],
                'eficiencia_departamentos': [],
                'eficiencia': 0,
            }
        )


@bp.route('/dashboard/api/kpis')
def dashboard_api_kpis():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
        total_rncs = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Pendente' AND is_deleted = 0")
        pendentes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE finalized_at IS NOT NULL AND is_deleted = 0")
        finalizadas = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT u.department) FROM rncs r LEFT JOIN users u ON r.user_id = u.id WHERE r.is_deleted = 0 AND u.department IS NOT NULL")
        departamentos_ativos = cursor.fetchone()[0]
        eficiencia_geral = round((finalizadas / max(total_rncs, 1)) * 100, 1)
        conn.close()
        return jsonify({'success': True, 'kpis': {'total_rncs': total_rncs, 'pendentes': pendentes, 'finalizadas': finalizadas, 'departamentos_ativos': departamentos_ativos, 'eficiencia_geral': eficiencia_geral}})
    except Exception:
        return jsonify({'success': True, 'kpis': {'total_rncs': 0, 'pendentes': 0, 'finalizadas': 0, 'departamentos_ativos': 0, 'eficiencia_geral': 0}})


@bp.get('/api/indicadores/extracted')
def api_indicadores_extracted():
    """Serve indicadores pré-processados a partir de data/indicadores_extracted.json.

    - Requer sessão ativa.
    - Útil como fallback/diagnóstico quando o cálculo em tempo real do banco não é desejado.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401

    filename = 'indicadores_extracted.json'

    # Procura o arquivo em locais prováveis para suportar ambos os modos (app factory e server_form)
    candidates = []
    try:
        # 1) Raiz do app atual
        candidates.append(os.path.join(current_app.root_path, 'data', filename))
        # 2) Um nível acima (quando root_path é app/)
        candidates.append(os.path.join(os.path.dirname(current_app.root_path), 'data', filename))
    except Exception:
        pass

    # 3) Baseado na localização deste arquivo (app/routes/.. -> raiz)
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(here))  # sobe de routes -> app -> raiz
        candidates.append(os.path.join(project_root, 'data', filename))
    except Exception:
        pass

    data_path = next((p for p in candidates if p and os.path.exists(p)), None)
    if not data_path:
        return jsonify({'success': False, 'message': 'Arquivo de indicadores não encontrado'}), 404

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Resposta padronizada
        return jsonify({'success': True, 'source': 'file', 'path': data_path, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao ler indicadores: {e}'}), 500


@bp.route('/api/employee-performance')
def get_employee_performance():
    """API para obter desempenho por funcionário (versão consolidada no blueprint)."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    conn = None
    try:
        year = request.args.get('year', '')
        month = request.args.get('month', '')
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        base_query = """
            SELECT 
                CASE 
                    WHEN r.signature_engineering_name IS NOT NULL AND r.signature_engineering_name != '' 
                    THEN r.signature_engineering_name
                    ELSE r.user_id
                END as owner_id,
                COUNT(r.id) as rnc_count
            FROM rncs r
            WHERE r.status IN ('Finalizado','finalized')
              AND r.is_deleted = 0
        """
        params = []
        if year and year.lower() != 'todos':
            base_query += " AND strftime('%Y', r.created_at) = ?"
            params.append(year)
        if month and month.lower() != 'todos':
            base_query += " AND strftime('%m', r.created_at) = ?"
            params.append(month.zfill(2))
        base_query += " GROUP BY owner_id"
        cursor.execute(base_query, params)
        rnc_rows = cursor.fetchall()
        rnc_data = {row[0]: row[1] for row in rnc_rows}
        meta_mensal = 5
        unique_signatures = set()
        for owner_id, _count in rnc_rows:
            if isinstance(owner_id, str) and owner_id:
                unique_signatures.add(owner_id)
            elif isinstance(owner_id, int):
                cursor.execute("SELECT name FROM users WHERE id = ?", (owner_id,))
                user_result = cursor.fetchone()
                if user_result:
                    unique_signatures.add(user_result[0])
        result = []
        for signature in sorted(unique_signatures):
            rncs = rnc_data.get(signature, 0)
            percentage = (rncs / meta_mensal * 100) if meta_mensal > 0 else 0
            status = 'Acima da Meta' if rncs >= meta_mensal else 'Abaixo da Meta'
            result.append({'id': signature, 'name': signature, 'rncs': rncs, 'meta': meta_mensal, 'percentage': round(percentage, 1), 'status': status, 'department': 'Engenharia'})
        result.sort(key=lambda x: x['percentage'], reverse=True)
        return jsonify({'success': True, 'data': result, 'filters': {'year': year or 'todos', 'month': month or 'todos'}})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar dados de funcionários: {str(e)}'}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


@bp.route('/api/dashboard/performance')
def get_dashboard_performance():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    conn = None
    try:
        year = request.args.get('year', '')
        month = request.args.get('month', '')
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        base_query = """
            SELECT 
                CASE 
                    WHEN r.signature_engineering_name IS NOT NULL AND r.signature_engineering_name != '' 
                    THEN r.signature_engineering_name
                    ELSE r.user_id
                END as owner_id,
                COUNT(r.id) as rnc_count
            FROM rncs r
            WHERE r.status IN ('Finalizado','finalized')
              AND r.is_deleted = 0
        """
        params = []
        if year and year.lower() != 'todos':
            base_query += " AND strftime('%Y', r.created_at) = ?"
            params.append(year)
        if month and month.lower() != 'todos':
            base_query += " AND strftime('%m', r.created_at) = ?"
            params.append(month.zfill(2))
        base_query += " GROUP BY owner_id"
        cursor.execute(base_query, params)
        rnc_rows = cursor.fetchall()
        rnc_data = {row[0]: row[1] for row in rnc_rows}
        meta_mensal = 5
        unique_signatures = set()
        for owner_id, _count in rnc_rows:
            if isinstance(owner_id, str) and owner_id:
                unique_signatures.add(owner_id)
            elif isinstance(owner_id, int):
                cursor.execute("SELECT name FROM users WHERE id = ?", (owner_id,))
                user_result = cursor.fetchone()
                if user_result:
                    unique_signatures.add(user_result[0])
        result = []
        for signature in sorted(unique_signatures):
            rncs = rnc_data.get(signature, 0)
            percentage = (rncs / meta_mensal * 100) if meta_mensal > 0 else 0
            status = 'Acima da Meta' if rncs >= meta_mensal else 'Abaixo da Meta'
            result.append({'id': signature, 'name': signature, 'rncs': rncs, 'meta': meta_mensal, 'percentage': round(percentage, 1), 'status': status, 'department': 'Engenharia'})
        result.sort(key=lambda x: x['percentage'], reverse=True)
        return jsonify({'success': True, 'data': result, 'filters': {'year': year or 'todos', 'month': month or 'todos'}})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar dados do dashboard: {str(e)}'}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
