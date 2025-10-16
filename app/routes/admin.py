from flask import Blueprint, request, jsonify, session, render_template, redirect
import os
import json
from datetime import datetime, timedelta
import sqlite3

bp = Blueprint('admin', __name__)


@bp.route('/admin/monitoring')
def monitoring_dashboard():
    if 'user_id' not in session:
        return redirect('/')
    try:
        from services.permissions import has_permission
        if not has_permission(session['user_id'], 'admin_access'):
            return redirect('/dashboard?error=access_denied&message=Acesso negado ao painel de monitoramento')
    except Exception:
        return redirect('/dashboard')
    return render_template('monitoring_dashboard.html')


@bp.get('/api/monitoring/security-events')
def api_monitoring_security_events():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    try:
        from services.permissions import has_permission
        if not has_permission(session['user_id'], 'admin_access'):
            return jsonify({'success': False, 'message': 'Sem permissão'}), 403
        # Localizar arquivo de log de segurança
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(base_dir)), 'logs')  # subir de routes -> app -> raiz
        log_path = os.path.join(logs_dir, 'security.log')
        limit = int(request.args.get('limit', 200))
        limit = 1 if limit < 1 else 2000 if limit > 2000 else limit
        events = []
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-limit:]
            for ln in lines:
                try:
                    events.append(json.loads(ln.strip()))
                except Exception:
                    continue
        return jsonify({'success': True, 'events': events})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao carregar eventos'}), 500


@bp.get('/api/monitoring/summary')
def api_monitoring_summary():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    try:
        from services.permissions import has_permission
        if not has_permission(session['user_id'], 'admin_access'):
            return jsonify({'success': False, 'message': 'Sem permissão'}), 403
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(base_dir)), 'logs')
        log_path = os.path.join(logs_dir, 'security.log')
        now = datetime.utcnow()
        window_hours = int(request.args.get('hours', 24))
        window_hours = 1 if window_hours < 1 else 168 if window_hours > 168 else window_hours
        since = now - timedelta(hours=window_hours)

        counters = {'auth_success': 0, 'auth_fail': 0, 'auth_lockout': 0, 'api_unauthorized': 0}
        bucket = {}
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                for ln in f:
                    try:
                        ev = json.loads(ln)
                    except Exception:
                        continue
                    ts = ev.get('ts')
                    if not ts:
                        continue
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z','').replace('z',''))
                    except Exception:
                        continue
                    if dt < since:
                        continue
                    cat = str(ev.get('cat') or '')
                    act = str(ev.get('act') or '')
                    status = str(ev.get('status') or '')
                    if cat == 'auth' and act == 'login' and status == 'success':
                        counters['auth_success'] += 1
                    if cat == 'auth' and act == 'login' and status == 'fail':
                        counters['auth_fail'] += 1
                        key = dt.strftime('%Y-%m-%d %H:00')
                        bucket[key] = bucket.get(key, 0) + 1
                    if cat == 'auth' and act == 'lockout':
                        counters['auth_lockout'] += 1
                        key = dt.strftime('%Y-%m-%d %H:00')
                        bucket[key] = bucket.get(key, 0) + 1
                    if cat == 'api' and act == 'unauthorized':
                        counters['api_unauthorized'] += 1

        timeline = [{'bucket': k, 'count': bucket[k]} for k in sorted(bucket.keys())]

        # Active lockouts from DB
        try:
            DB_PATH = 'ippel_system.db'
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM login_lockouts WHERE locked_until IS NOT NULL AND locked_until > strftime("%s","now")')
            active_lockouts = cur.fetchone()[0]
            conn.close()
        except Exception:
            active_lockouts = 0

        return jsonify({'success': True, 'window_hours': window_hours, 'counters': counters, 'timeline': timeline, 'active_lockouts': active_lockouts})
    except Exception:
        return jsonify({'success': False, 'message': 'Erro ao carregar resumo'}), 500


@bp.get('/api/monitoring/lockouts')
def api_monitoring_lockouts():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    try:
        from services.permissions import has_permission
        if not has_permission(session['user_id'], 'admin_access'):
            return jsonify({'success': False, 'message': 'Sem permissão'}), 403
        DB_PATH = 'ippel_system.db'
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute('''
            SELECT ll.user_id, u.name, u.email, ll.failed_count, ll.locked_until
              FROM login_lockouts ll
              LEFT JOIN users u ON u.id = ll.user_id
             WHERE ll.locked_until IS NOT NULL AND ll.locked_until > strftime('%s','now')
             ORDER BY ll.locked_until DESC
             LIMIT 100
        ''')
        rows = cur.fetchall(); conn.close()
        data = [
            {
                'user_id': r[0],
                'name': r[1],
                'email': r[2],
                'failed_count': r[3],
                'locked_until': int(r[4]) if r[4] is not None else None
            } for r in rows
        ]
        return jsonify({'success': True, 'lockouts': data})
    except Exception:
        return jsonify({'success': False, 'message': 'Erro ao carregar lockouts'}), 500
