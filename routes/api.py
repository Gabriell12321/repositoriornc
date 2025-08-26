from flask import Blueprint, request, jsonify, session
import sqlite3, json, logging

# DB path local para evitar dependência circular; mantido igual ao servidor
DB_PATH = 'ippel_system.db'
logger = logging.getLogger('ippel.api')

api = Blueprint('api_bp', __name__)

# Exigir autenticação para todas as rotas deste blueprint
@api.before_request
def _require_auth_api():
    if request.method != 'OPTIONS' and 'user_id' not in session:
        try:
            import importlib
            _sl = importlib.import_module('services.security_log')
            _sl.sec_log('api', 'unauthorized', ip=request.remote_addr, details={'path': request.path, 'method': request.method})
        except Exception:
            pass
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

# Aplicar um limite padrão por IP em todas as rotas da API (se limiter estiver ativo)
try:
    import importlib
    _rl = importlib.import_module('services.rate_limit')
    _limiter = getattr(_rl, 'limiter')()
    if _limiter is not None:
        _limiter.limit("120 per minute")(api)
except Exception:
    pass

# Proteções avançadas: CSRF em endpoints de escrita e permissão
try:
    import importlib
    _ep = importlib.import_module('services.endpoint_protection')
    csrf_protect = getattr(_ep, 'csrf_protect')
    require_permission = getattr(_ep, 'require_permission')
    ensure_csrf_token = getattr(_ep, 'ensure_csrf_token')
except Exception:
    def csrf_protect(*_a, **_k):
        def _d(f): return f
        return _d
    def require_permission(*_a, **_k):
        def _d(f): return f
        return _d
    def ensure_csrf_token():
        return ''

@api.get('/api/csrf-token')
def get_csrf_token():
    token = ensure_csrf_token()
    return jsonify({'success': True, 'csrf_token': token})


@api.post('/api/user/avatar')
@csrf_protect()
@require_permission('update_avatar')
def update_avatar():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        data = request.get_json(silent=True) or {}
        avatar = str(data.get('avatar', '')).strip()[:64]
        prefs = data.get('prefs') if isinstance(data.get('prefs'), dict) else None

        allowed = {
            'ava-ippel','ava-galaxy','ava-ocean','ava-rainbow','ava-neon','ava-sunset','ava-wave','ava-pulse',
            'ava-forest','ava-lava','ava-mint','ava-sky','ava-rose','ava-candy','ava-silver','ava-carbon',
            'ava-custom','ava-image','ava-corp-blue','ava-corp-slate','ava-corp-navy','ava-corp-teal','ava-corp-gray','ava-corp-indigo','ava-initials'
        }
        if avatar and avatar not in allowed:
            return jsonify({'success': False, 'message': 'Avatar inválido'}), 400

        if avatar == 'ava-image':
            if not prefs or not isinstance(prefs.get('image'), str):
                return jsonify({'success': False, 'message': 'Imagem do avatar inválida'}), 400
            img = prefs.get('image', '')
            if len(img) > 512:
                return jsonify({'success': False, 'message': 'URL de imagem muito longa'}), 400
            allowed_prefixes = ('/static/avatars/','https://api.dicebear.com/','http://api.dicebear.com/')
            if not img.startswith(allowed_prefixes):
                return jsonify({'success': False, 'message': 'Origem de imagem não permitida'}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        prefs_json = json.dumps(prefs, ensure_ascii=False) if prefs else None
        cursor.execute('UPDATE users SET avatar_key = ?, avatar_prefs = ? WHERE id = ?', (avatar or None, prefs_json, session['user_id']))
        conn.commit(); conn.close()
        return jsonify({'success': True, 'avatar': avatar, 'prefs': prefs})
    except Exception as e:
        try:
            logger.error(f"Erro ao atualizar avatar do usuário {session.get('user_id')}: {e}")
        except Exception:
            pass
        return jsonify({'success': False, 'message': 'Erro ao atualizar avatar'}), 500
    