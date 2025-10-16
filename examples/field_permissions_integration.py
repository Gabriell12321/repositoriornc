"""
Exemplo de integração: Campo de permissões no formulário RNC
Este arquivo mostra como aplicar as permissões de campo no formulário de criação
"""

from flask import session, jsonify, request
from routes.field_locks import get_user_locked_fields, AVAILABLE_FIELDS
import sqlite3
import logging

logger = logging.getLogger('ippel.form_integration')

def validate_rnc_form_permissions(form_data):
    """
    Valida se o usuário atual pode preencher os campos enviados
    
    Args:
        form_data (dict): Dados do formulário enviado
        
    Returns:
        tuple: (is_valid, error_message, blocked_fields)
    """
    if 'user_id' not in session:
        return False, "Usuário não autenticado", []
    
    try:
        # Buscar campos bloqueados para o usuário
        locked_fields = get_user_locked_fields(session['user_id'])
        
        # Verificar quais campos enviados estão bloqueados
        blocked_attempts = []
        for field_name, value in form_data.items():
            if field_name in locked_fields and value:  # Se campo bloqueado tem valor
                blocked_attempts.append(field_name)
        
        if blocked_attempts:
            field_labels = [AVAILABLE_FIELDS.get(field, field) for field in blocked_attempts]
            return False, f"Campos não permitidos: {', '.join(field_labels)}", blocked_attempts
        
        return True, "OK", []
        
    except Exception as e:
        logger.error(f"Erro ao validar permissões: {e}")
        return False, "Erro interno", []


def get_form_field_config(user_id=None):
    """
    Retorna configuração de campos para o formulário
    
    Args:
        user_id (int, optional): ID do usuário. Se None, usa sessão atual
        
    Returns:
        dict: Configuração dos campos {field_name: {disabled: bool, label: str}}
    """
    if user_id is None:
        user_id = session.get('user_id')
    
    if not user_id:
        return {}
    
    try:
        locked_fields = get_user_locked_fields(user_id)
        
        config = {}
        for field_name, field_label in AVAILABLE_FIELDS.items():
            config[field_name] = {
                'disabled': field_name in locked_fields,
                'label': field_label,
                'required': field_name in ['title', 'description']  # Campos obrigatórios
            }
        
        return config
        
    except Exception as e:
        logger.error(f"Erro ao buscar configuração: {e}")
        return {}


def apply_field_permissions_to_template_context(context):
    """
    Adiciona configurações de permissão ao contexto do template
    
    Args:
        context (dict): Contexto do template
        
    Returns:
        dict: Contexto atualizado com field_permissions
    """
    try:
        context['field_permissions'] = get_form_field_config()
        context['has_field_restrictions'] = any(
            config['disabled'] for config in context['field_permissions'].values()
        )
        return context
        
    except Exception as e:
        logger.error(f"Erro ao aplicar permissões ao template: {e}")
        context['field_permissions'] = {}
        context['has_field_restrictions'] = False
        return context


# Exemplo de middleware para Flask
def check_field_permissions_middleware():
    """
    Middleware para verificar permissões automaticamente em rotas de criação/edição
    """
    # Aplicar apenas em rotas de criação/edição
    if request.endpoint in ['create_rnc', 'edit_rnc', 'submit_rnc']:
        if request.method == 'POST':
            form_data = request.form.to_dict()
            
            is_valid, error_msg, blocked_fields = validate_rnc_form_permissions(form_data)
            
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': error_msg,
                    'blocked_fields': blocked_fields
                }), 403


# Exemplo de função auxiliar para templates Jinja2
def setup_template_functions(app):
    """
    Registra funções auxiliares no Jinja2 para uso nos templates
    """
    
    @app.template_global()
    def field_is_disabled(field_name):
        """Verifica se um campo está desabilitado para o usuário atual"""
        try:
            config = get_form_field_config()
            return config.get(field_name, {}).get('disabled', False)
        except:
            return False
    
    @app.template_global()
    def get_field_config(field_name):
        """Retorna configuração completa de um campo"""
        try:
            config = get_form_field_config()
            return config.get(field_name, {
                'disabled': False,
                'label': field_name.title(),
                'required': False
            })
        except:
            return {'disabled': False, 'label': field_name.title(), 'required': False}
    
    @app.template_global()
    def user_locked_fields():
        """Retorna lista de campos bloqueados para o usuário atual"""
        try:
            user_id = session.get('user_id')
            if user_id:
                return get_user_locked_fields(user_id)
            return []
        except:
            return []


# Exemplo de uso em uma rota
def example_route_with_permissions():
    """
    Exemplo de como usar as permissões em uma rota
    """
    from flask import render_template, request, flash, redirect, url_for
    
    if request.method == 'POST':
        # Validar permissões antes de processar
        form_data = request.form.to_dict()
        is_valid, error_msg, blocked_fields = validate_rnc_form_permissions(form_data)
        
        if not is_valid:
            flash(f"Erro: {error_msg}", 'error')
            return redirect(request.url)
        
        # Processar formulário normalmente...
        # ... código de criação da RNC ...
        
        flash('RNC criada com sucesso!', 'success')
        return redirect(url_for('list_rncs'))
    
    # GET - Renderizar formulário com permissões
    context = {
        'title': 'Nova RNC',
        'action': 'create'
    }
    
    # Aplicar permissões ao contexto
    context = apply_field_permissions_to_template_context(context)
    
    return render_template('create_rnc.html', **context)


# JavaScript para integração no frontend
FRONTEND_INTEGRATION_JS = """
// Função para carregar e aplicar permissões de campo
async function loadFieldPermissions() {
    try {
        const response = await fetch('/admin/field-locks/api/user/locked-fields');
        const data = await response.json();
        
        if (data.success) {
            const lockedFields = data.locked_fields;
            
            // Desabilitar campos bloqueados
            lockedFields.forEach(fieldName => {
                const inputs = document.querySelectorAll(`[name="${fieldName}"], #${fieldName}, .field-${fieldName}`);
                
                inputs.forEach(input => {
                    input.disabled = true;
                    input.style.backgroundColor = '#f8f9fa';
                    input.style.cursor = 'not-allowed';
                    
                    // Adicionar tooltip explicativo
                    input.title = `Campo bloqueado para seu grupo de usuário`;
                    
                    // Adicionar ícone visual
                    const icon = document.createElement('span');
                    icon.innerHTML = ' 🔒';
                    icon.style.color = '#dc3545';
                    
                    if (input.parentNode && !input.parentNode.querySelector('.lock-icon')) {
                        icon.className = 'lock-icon';
                        input.parentNode.appendChild(icon);
                    }
                });
            });
            
            // Mostrar aviso se há campos bloqueados
            if (lockedFields.length > 0) {
                showFieldRestrictionsNotice(data.locked_with_labels);
            }
        }
    } catch (error) {
        console.error('Erro ao carregar permissões:', error);
    }
}

function showFieldRestrictionsNotice(lockedFieldsWithLabels) {
    const notice = document.createElement('div');
    notice.className = 'alert alert-warning';
    notice.innerHTML = `
        <strong>⚠️ Restrições de Campo:</strong><br>
        Os seguintes campos estão bloqueados para seu grupo:<br>
        <ul>
            ${Object.entries(lockedFieldsWithLabels).map(([field, label]) => 
                `<li>${label} (${field})</li>`
            ).join('')}
        </ul>
    `;
    
    // Inserir no topo do formulário
    const form = document.querySelector('form');
    if (form) {
        form.insertBefore(notice, form.firstChild);
    }
}

// Validação no cliente antes do envio
function validateFormPermissions(formData) {
    return fetch('/admin/field-locks/api/user/locked-fields')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const lockedFields = data.locked_fields;
                const violations = [];
                
                for (const [fieldName, value] of Object.entries(formData)) {
                    if (lockedFields.includes(fieldName) && value) {
                        violations.push(data.locked_with_labels[fieldName] || fieldName);
                    }
                }
                
                if (violations.length > 0) {
                    throw new Error(`Campos não permitidos: ${violations.join(', ')}`);
                }
            }
            return true;
        });
}

// Carregar permissões quando a página estiver pronta
document.addEventListener('DOMContentLoaded', loadFieldPermissions);
"""

if __name__ == "__main__":
    print("🔧 Exemplo de Integração - Sistema de Permissões de Campos")
    print("="*60)
    print("Este arquivo contém exemplos de como integrar o sistema de")
    print("permissões de campos com formulários RNC existentes.")
    print("\nFunções principais:")
    print("• validate_rnc_form_permissions() - Validação backend")
    print("• get_form_field_config() - Configuração de campos")
    print("• setup_template_functions() - Funções para templates")
    print("• JavaScript para frontend automático")
    print("\nPara usar, importe as funções necessárias nas suas rotas.")