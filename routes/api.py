from flask import Blueprint, request, jsonify, session
import sqlite3, json, logging

# DB path local para evitar dependência circular; mantido igual ao servidor
DB_PATH = 'ippel_system.db'
logger = logging.getLogger('ippel.api')

api = Blueprint('api_bp', __name__)

@api.post('/api/user/avatar')
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
    