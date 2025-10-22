#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rotas para gerenciamento de permissões de ações rápidas
"""

from flask import Blueprint, render_template_string, request, jsonify, redirect, url_for, flash
import sqlite3
from functools import wraps

# Criar blueprint
quick_actions_bp = Blueprint('quick_actions', __name__, url_prefix='/admin')

def get_db_connection():
    """Conecta ao banco de dados."""
    conn = sqlite3.connect('ippel_system.db')
    conn.row_factory = sqlite3.Row
    return conn

def admin_required(f):
    """Decorator para verificar se o usuário é admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implementar verificação de admin real
        # Por enquanto, sempre permite
        return f(*args, **kwargs)
    return decorated_function

@quick_actions_bp.route('/quick-actions-permissions')
@admin_required
def manage_permissions():
    """Interface para gerenciar permissões das ações rápidas."""
    
    conn = get_db_connection()
    
    # Buscar todas as ações
    actions = conn.execute('''
        SELECT action_key, action_name, action_description, icon, url, is_active
        FROM quick_actions
        ORDER BY action_name
    ''').fetchall()
    
    # Buscar todos os grupos
    groups = conn.execute('''
        SELECT id, name, description
        FROM groups
        ORDER BY name
    ''').fetchall()
    
    # Buscar permissões existentes
    permissions = {}
    for action in actions:
        permissions[action['action_key']] = conn.execute('''
            SELECT g.id, g.name, qap.permission_level
            FROM quick_action_permissions qap
            JOIN groups g ON qap.group_id = g.id
            WHERE qap.action_key = ?
        ''', (action['action_key'],)).fetchall()
    
    conn.close()
    
    template = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerenciar Permissões - Ações Rápidas</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
    <style>
        .permissions-container {
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header {
            border-bottom: 2px solid #007bff;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        
        .header h1 {
            color: #007bff;
            margin: 0;
            font-size: 24px;
        }
        
        .header p {
            color: #666;
            margin: 5px 0 0 0;
        }
        
        .action-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        
        .action-header {
            background: #f8f9fa;
            padding: 15px;
            border-bottom: 1px solid #ddd;
        }
        
        .action-title {
            font-size: 18px;
            font-weight: bold;
            margin: 0;
            color: #333;
        }
        
        .action-description {
            color: #666;
            margin: 5px 0 0 0;
            font-size: 14px;
        }
        
        .action-url {
            color: #007bff;
            font-size: 12px;
            font-family: monospace;
        }
        
        .permissions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 15px;
        }
        
        .permission-item {
            display: flex;
            align-items: center;
            padding: 10px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            background: #fafafa;
        }
        
        .permission-item.active {
            background: #e8f5e8;
            border-color: #28a745;
        }
        
        .permission-checkbox {
            margin-right: 10px;
        }
        
        .group-name {
            font-weight: bold;
            color: #333;
        }
        
        .permission-level {
            font-size: 12px;
            color: #666;
            margin-left: auto;
        }
        
        .btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
        }
        
        .btn:hover {
            background: #0056b3;
        }
        
        .btn-success {
            background: #28a745;
        }
        
        .btn-success:hover {
            background: #1e7e34;
        }
        
        .btn-secondary {
            background: #6c757d;
        }
        
        .btn-secondary:hover {
            background: #545b62;
        }
        
        .stats {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
            flex: 1;
        }
        
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }
        
        .stat-label {
            color: #666;
            font-size: 14px;
        }
        
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .alert-info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }
        
        .actions-buttons {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="permissions-container">
        <div class="header">
            <h1> Gerenciar Permissões - Ações Rápidas</h1>
            <p>Configure quais grupos podem visualizar cada ação rápida no dashboard</p>
        </div>
        
        <div class="alert alert-info">
            <strong> Como funciona:</strong> 
            Por padrão, as ações rápidas não aparecem para ninguém. 
            Marque os grupos que devem ter acesso a cada ação.
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ actions|length }}</div>
                <div class="stat-label">Ações Disponíveis</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ groups|length }}</div>
                <div class="stat-label">Grupos Cadastrados</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_permissions }}</div>
                <div class="stat-label">Permissões Configuradas</div>
            </div>
        </div>
        
        <form id="permissionsForm" method="POST" action="{{ url_for('quick_actions.save_permissions') }}">
            {% for action in actions %}
            <div class="action-card">
                <div class="action-header">
                    <div class="action-title">{{ action.icon }} {{ action.action_name }}</div>
                    <div class="action-description">{{ action.action_description }}</div>
                    <div class="action-url">{{ action.url }}</div>
                </div>
                
                <div class="permissions-grid">
                    {% for group in groups %}
                    {% set has_permission = false %}
                    {% for perm in permissions[action.action_key] %}
                        {% if perm.id == group.id %}
                            {% set has_permission = true %}
                        {% endif %}
                    {% endfor %}
                    
                    <div class="permission-item {{ 'active' if has_permission }}">
                        <input type="checkbox" 
                               class="permission-checkbox"
                               name="permission_{{ action.action_key }}_{{ group.id }}"
                               value="view"
                               {{ 'checked' if has_permission }}
                               onchange="togglePermissionStyle(this)">
                        <span class="group-name">{{ group.name }}</span>
                        <span class="permission-level">{{ 'ATIVO' if has_permission else 'INATIVO' }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
            
            <div class="actions-buttons">
                <button type="submit" class="btn btn-success"> Salvar Permissões</button>
                <a href="/dashboard" class="btn btn-secondary"> Voltar ao Dashboard</a>
                <button type="button" class="btn" onclick="selectAllGroups()"> Marcar Todos</button>
                <button type="button" class="btn" onclick="clearAllGroups()"> Desmarcar Todos</button>
            </div>
        </form>
    </div>
    
    <script>
        function togglePermissionStyle(checkbox) {
            const item = checkbox.closest('.permission-item');
            const level = item.querySelector('.permission-level');
            
            if (checkbox.checked) {
                item.classList.add('active');
                level.textContent = 'ATIVO';
            } else {
                item.classList.remove('active');
                level.textContent = 'INATIVO';
            }
        }
        
        function selectAllGroups() {
            const checkboxes = document.querySelectorAll('.permission-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
                togglePermissionStyle(checkbox);
            });
        }
        
        function clearAllGroups() {
            const checkboxes = document.querySelectorAll('.permission-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
                togglePermissionStyle(checkbox);
            });
        }
        
        // Auto-submit form quando checkbox mudar (opcional)
        document.querySelectorAll('.permission-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                // Pode adicionar auto-save aqui se desejar
            });
        });
    </script>
</body>
</html>
    '''
    
    # Calcular total de permissões
    total_permissions = sum(len(perms) for perms in permissions.values())
    
    return render_template_string(template, 
                                actions=actions, 
                                groups=groups, 
                                permissions=permissions,
                                total_permissions=total_permissions)

@quick_actions_bp.route('/quick-actions-permissions/save', methods=['POST'])
@admin_required
def save_permissions():
    """Salva as permissões das ações rápidas."""
    
    conn = get_db_connection()
    
    try:
        # Limpar todas as permissões existentes
        conn.execute('DELETE FROM quick_action_permissions')
        
        # Processar formulário
        for key, value in request.form.items():
            if key.startswith('permission_'):
                # Formato: permission_ACTION_KEY_GROUP_ID
                parts = key.split('_')
                if len(parts) >= 3:
                    action_key = '_'.join(parts[1:-1])  # Pode ter underscores no action_key
                    group_id = parts[-1]
                    permission_level = value
                    
                    # Inserir permissão
                    conn.execute('''
                        INSERT INTO quick_action_permissions 
                        (action_key, group_id, permission_level)
                        VALUES (?, ?, ?)
                    ''', (action_key, group_id, permission_level))
        
        conn.commit()
        flash(' Permissões salvas com sucesso!', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f' Erro ao salvar permissões: {str(e)}', 'error')
    
    finally:
        conn.close()
    
    return redirect(url_for('quick_actions.manage_permissions'))

@quick_actions_bp.route('/api/user-quick-actions/<int:user_id>')
def get_user_quick_actions(user_id):
    """API para buscar ações rápidas disponíveis para um usuário."""
    
    conn = get_db_connection()
    
    # Buscar grupos do usuário
    user_groups = conn.execute('''
        SELECT g.id, g.name
        FROM groups g
        JOIN user_groups ug ON g.id = ug.group_id
        WHERE ug.user_id = ?
    ''', (user_id,)).fetchall()
    
    if not user_groups:
        conn.close()
        return jsonify([])
    
    group_ids = [g['id'] for g in user_groups]
    placeholders = ','.join('?' for _ in group_ids)
    
    # Buscar ações permitidas para os grupos do usuário
    quick_actions = conn.execute(f'''
        SELECT DISTINCT qa.action_key, qa.action_name, qa.icon, qa.url, qa.action_description
        FROM quick_actions qa
        JOIN quick_action_permissions qap ON qa.action_key = qap.action_key
        WHERE qap.group_id IN ({placeholders})
        AND qa.is_active = 1
        ORDER BY qa.action_name
    ''', group_ids).fetchall()
    
    conn.close()
    
    # Converter para lista de dicionários
    actions = []
    for action in quick_actions:
        actions.append({
            'key': action['action_key'],
            'name': action['action_name'],
            'icon': action['icon'],
            'url': action['url'],
            'description': action['action_description']
        })
    
    return jsonify(actions)

if __name__ == '__main__':
    print("Blueprint de Ações Rápidas criado!")
    print("Para usar, registre no app.py:")
    print("from routes.quick_actions import quick_actions_bp")
    print("app.register_blueprint(quick_actions_bp)")
