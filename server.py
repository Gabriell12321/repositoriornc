import os
from typing import Dict, Any, List
from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__, static_folder=os.path.abspath('dist'))

# Dados simulados para usuários
current_user: Dict[str, Any] = {
    "id": "1",
    "username": "elvio",
    "name": "Elvio",
    "email": "elvio@exemplo.com",
    "role": "admin",
    "permissions": ["users.create", "users.edit", "users.delete", "users.view"],
    "isActive": True,
    "createdAt": "2025-01-01T00:00:00Z"
}
system_users: List[Dict[str, Any]] = [current_user]

@app.route('/_spark/kv/current-user', methods=['GET', 'POST'])
def spark_current_user():
    if request.method == 'GET':
        return jsonify(current_user)
    elif request.method == 'POST':
        try:
            data = request.get_json(force=True)
            if data:
                current_user.update(data)
            return jsonify(current_user)
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return '', 405

@app.route('/_spark/kv/system-users', methods=['GET', 'POST'])
def spark_system_users():
    if request.method == 'GET':
        return jsonify(system_users)
    elif request.method == 'POST':
        try:
            data = request.get_json(force=True)
            if data:
                system_users.append(data)
            return jsonify(system_users)
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return '', 405

@app.route('/_spark/loaded', methods=['POST'])
def spark_loaded():
    return jsonify({"status": "ok"}), 200

@app.route('/_spark/kv/<path:key>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def spark_kv_generic(key: str):
    """Rota genérica para qualquer chave do key-value store"""
    if request.method == 'GET':
        return jsonify({"key": key, "value": None})
    elif request.method in ['POST', 'PUT']:
        try:
            data = request.get_json(force=True)
            return jsonify({"key": key, "value": data})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    elif request.method == 'DELETE':
        return jsonify({"status": "deleted"}), 200
    return '', 405

@app.route('/')
def index():
    static_folder = app.static_folder or os.path.abspath('dist')
    return send_from_directory(static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path: str):
    static_folder = app.static_folder or os.path.abspath('dist')
    file_path = os.path.join(static_folder, path)
    if os.path.isfile(file_path):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
