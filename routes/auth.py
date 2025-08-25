from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
import logging

from services.users import get_user_by_email

auth = Blueprint('auth_bp', __name__)
logger = logging.getLogger('ippel.auth')

@auth.post('/api/login')
def login():
    try:
        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')
        user_data = get_user_by_email(email)
        if user_data and check_password_hash(user_data[3], password):
            session['user_id'] = user_data[0]
            session['user_name'] = user_data[1]
            session['user_email'] = user_data[2]
            session['user_department'] = user_data[4]
            session['user_role'] = user_data[5]
            session.permanent = True
            resp = jsonify({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'redirect': '/dashboard',
                'user': {
                    'name': user_data[1],
                    'email': user_data[2],
                    'department': user_data[4]
                }
            })
            try:
                resp.set_cookie('IPPEL_UID', str(user_data[0]), max_age=60*60*8, path='/', httponly=False, samesite='Lax')
            except Exception:
                pass
            return resp
        return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do sistema'}), 500

@auth.get('/api/logout')
def logout():
    try:
        for k in ['user_id','user_name','user_email','user_department','user_role']:
            try: session.pop(k, None)
            except Exception: pass
        session.clear()
        resp = jsonify({'success': True, 'message': 'Logout realizado com sucesso!'})
        try: resp.delete_cookie('IPPEL_UID', path='/')
        except Exception: pass
        return resp
    except Exception:
        return jsonify({'success': True})
