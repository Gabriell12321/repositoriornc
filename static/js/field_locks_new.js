// JavaScript para interface de permissões de campos RNC
let currentGroupId = null;
let currentContext = 'creation'; // Contexto ativo: 'creation' ou 'response'
let fieldLocks = {};
let hasChanges = false;

const availableFields = [
    // === INFORMAÇÕES PRINCIPAIS DO RNC ===
    'rnc_number', 'title', 'equipment', 'client', 'description', 'created_at',
    
    // === DADOS TÉCNICOS DO PRODUTO ===
    'mp', 'revision', 'position', 'cv', 'conjunto', 'modelo', 'description_drawing',
    'quantity', 'material', 'drawing', 'purchase_order',
    
    // === RESPONSABILIDADES E SETORES ===
    'responsavel', 'inspetor', 'setor', 'area_responsavel',
    
    // === ASSINATURAS ===
    'signature_inspection_name', 'signature_engineering_name', 'signature_inspection2_name',
    
    // === DATAS DE ASSINATURA ===
    'signature_inspection_date', 'signature_engineering_date', 'signature_inspection2_date',
    
    // === INSTRUÇÕES E ANÁLISES ===
    'instruction_retrabalho', 'cause_rnc', 'action_rnc',
    
    // === DISPOSIÇÃO DO MATERIAL NÃO-CONFORME ===
    'disposition_usar', 'disposition_retrabalhar', 'disposition_rejeitar',
    'disposition_sucata', 'disposition_devolver_estoque', 'disposition_devolver_fornecedor',
    
    // === INSPEÇÃO DO RETRABALHO ===
    'inspection_aprovado', 'inspection_reprovado', 'inspection_ver_rnc',
    
    // === CAMPOS ADMINISTRATIVOS ===
    'priority', 'status', 'assigned_user_id', 'price', 'justificativa'
];

// Carregar grupos na inicialização
document.addEventListener('DOMContentLoaded', function() {
    loadGroups();
    setupEventListeners();
});

function setupEventListeners() {
    // Search functionality
    const groupSearch = document.getElementById('groupSearch');
    if (groupSearch) {
        groupSearch.addEventListener('input', function(e) {
            filterGroups(e.target.value);
        });
    }

    // Field click handlers
    document.querySelectorAll('.field-preview').forEach(field => {
        field.addEventListener('click', function() {
            if (currentGroupId) {
                toggleField(this.dataset.field);
            }
        });
    });

    // Warning on page leave if there are unsaved changes
    window.addEventListener('beforeunload', function(e) {
        if (hasChanges) {
            e.preventDefault();
            e.returnValue = 'Você tem alterações não salvas. Deseja continuar?';
        }
    });
}

async function loadGroups() {
    try {
        const response = await fetch('/admin/field-locks/api/groups');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const groups = await response.json();
        
        console.log('Groups loaded:', groups);
        
        const groupList = document.getElementById('groupList');
        if (!groupList) {
            throw new Error('Element groupList not found');
        }
        
        groupList.innerHTML = '';
        
        if (Array.isArray(groups)) {
            groups.forEach(group => {
                const li = document.createElement('li');
                li.className = 'group-item';
                li.onclick = () => selectGroup(group.id, group.name);
                
                li.innerHTML = `
                    <div class="group-name">${group.name}</div>
                    <div class="group-desc">${group.description || 'Sem descrição'}</div>
                `;
                
                groupList.appendChild(li);
            });
        } else {
            console.error('Groups response is not an array:', groups);
            showAlert('Erro: Resposta dos grupos não é um array válido', 'error');
        }
        
    } catch (error) {
        console.error('Erro ao carregar grupos:', error);
        showAlert('Erro ao carregar grupos: ' + error.message, 'error');
    }
}

function filterGroups(searchTerm) {
    const groups = document.querySelectorAll('.group-item');
    const term = searchTerm.toLowerCase();
    
    groups.forEach(group => {
        const text = group.textContent.toLowerCase();
        group.style.display = text.includes(term) ? 'block' : 'none';
    });
}

async function selectGroup(groupId, groupName) {
    // Verificar se há mudanças não salvas
    if (hasChanges) {
        const confirm = window.confirm('Você tem alterações não salvas. Deseja continuar sem salvar?');
        if (!confirm) return;
    }

    currentGroupId = groupId;
    
    // Atualizar UI
    document.querySelectorAll('.group-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Encontrar o item clicado e marcar como ativo
    const clickedItem = Array.from(document.querySelectorAll('.group-item')).find(item => {
        return item.onclick.toString().includes(groupId);
    });
    
    if (clickedItem) {
        clickedItem.classList.add('active');
    }
    
    document.getElementById('loading').style.display = 'none';
    document.getElementById('groupContent').style.display = 'block';
    document.getElementById('groupTitle').textContent = `Configurações do Grupo: ${groupName}`;
    
    // Carregar configurações do grupo
    await loadGroupSettings(groupId);
}

async function loadGroupSettings(groupId) {
    try {
        // Adicionar parâmetro context na URL
        const response = await fetch(`/admin/field-locks/api/locks/${groupId}?context=${currentContext}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const responseData = await response.json();
        
        console.log(`Lock settings response [${currentContext}]:`, responseData);
        
        // Resetar fieldLocks
        fieldLocks = {};
        
        // Verificar se a resposta contém locks
        if (responseData.success && responseData.locks) {
            // A API retorna locks como objeto: {field_name: {is_locked: boolean}}
            Object.keys(responseData.locks).forEach(fieldName => {
                const lockData = responseData.locks[fieldName];
                if (lockData && typeof lockData.is_locked === 'boolean') {
                    fieldLocks[fieldName] = lockData.is_locked;
                }
            });
        } else {
            console.warn('Resposta da API não contém locks válidos:', responseData);
        }
        
        // Atualizar interface visual
        updateFieldDisplay();
        hasChanges = false;
        
    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
        showAlert('Erro ao carregar configurações: ' + error.message, 'error');
    }
}

function updateFieldDisplay() {
    availableFields.forEach(fieldName => {
        const fieldElement = document.querySelector(`[data-field="${fieldName}"]`);
        if (!fieldElement) {
            console.warn(`Field element not found: ${fieldName}`);
            return;
        }
        
        const statusElement = fieldElement.querySelector('.field-status');
        if (!statusElement) {
            console.warn(`Status element not found for field: ${fieldName}`);
            return;
        }
        
        const isLocked = fieldLocks[fieldName] || false;
        
        // Atualizar classes
        fieldElement.className = `field-preview ${isLocked ? 'locked' : 'unlocked'}`;
        statusElement.className = `field-status ${isLocked ? 'locked' : 'unlocked'}`;
        statusElement.textContent = isLocked ? '🔒' : '🔓';
    });
}

function toggleField(fieldName) {
    if (!fieldName) {
        console.warn('Field name is empty');
        return;
    }
    
    fieldLocks[fieldName] = !fieldLocks[fieldName];
    updateFieldDisplay();
    hasChanges = true;
}

async function saveChanges() {
    if (!currentGroupId) {
        showAlert('Selecione um grupo primeiro', 'error');
        return;
    }

    try {
        const locks = {};
        availableFields.forEach(fieldName => {
            locks[fieldName] = fieldLocks[fieldName] || false;
        });

        const contextLabel = currentContext === 'creation' ? '🆕 CRIAÇÃO' : '📝 RESPOSTA';
        
        const response = await fetch(`/admin/field-locks/api/locks/${currentGroupId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                locks: locks,
                context: currentContext // Enviar contexto atual
            })
        });

        const result = await response.json();

        if (response.ok) {
            showAlert(`✅ Configurações [${contextLabel}] salvas com sucesso!`, 'success');
            hasChanges = false;
        } else {
            throw new Error(result.error || 'Erro desconhecido');
        }

    } catch (error) {
        console.error('Erro ao salvar:', error);
        showAlert('❌ Erro ao salvar: ' + error.message, 'error');
    }
}

function unlockAll() {
    availableFields.forEach(fieldName => {
        fieldLocks[fieldName] = false;
    });
    updateFieldDisplay();
    hasChanges = true;
    showAlert('🔓 Todos os campos foram liberados', 'success');
}

function lockAll() {
    availableFields.forEach(fieldName => {
        fieldLocks[fieldName] = true;
    });
    updateFieldDisplay();
    hasChanges = true;
    showAlert('🔒 Todos os campos foram bloqueados', 'success');
}

async function resetGroup() {
    if (!currentGroupId) {
        showAlert('Selecione um grupo primeiro', 'error');
        return;
    }

    const confirm = window.confirm('Tem certeza que deseja resetar todas as configurações deste grupo?');
    if (!confirm) return;

    try {
        const response = await fetch(`/admin/field-locks/api/locks/${currentGroupId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok) {
            showAlert('🗑️ Configurações resetadas com sucesso!', 'success');
            await loadGroupSettings(currentGroupId);
        } else {
            throw new Error(result.error || 'Erro desconhecido');
        }

    } catch (error) {
        console.error('Erro ao resetar:', error);
        showAlert('❌ Erro ao resetar: ' + error.message, 'error');
    }
}

function showAlert(message, type) {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) {
        console.error('Alerts container not found');
        return;
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    alertsContainer.innerHTML = '';
    alertsContainer.appendChild(alertDiv);
    
    // Auto-hide success messages
    if (type === 'success') {
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Exposer funções globalmente para os botões HTML
window.saveChanges = saveChanges;
window.unlockAll = unlockAll;
window.lockAll = lockAll;
window.resetGroup = resetGroup;
// Modal visual premium para campos bloqueados
function showBlockedFieldsModal(blockedFields) {
    // Remove modal anterior se existir
    const oldModal = document.getElementById('blockedFieldsModal');
    if (oldModal) oldModal.remove();

    // Cria modal
    const modal = document.createElement('div');
    modal.id = 'blockedFieldsModal';
    modal.className = 'blocked-modal-premium';
    modal.innerHTML = `
        <div class="blocked-modal-content">
            <div class="blocked-modal-icon">🔒</div>
            <h2 class="blocked-modal-title">Campos Bloqueados</h2>
            <p class="blocked-modal-desc">Os seguintes campos estão bloqueados para seu grupo:</p>
            <ul class="blocked-modal-list">
                ${blockedFields.map(f => `<li><span class='blocked-modal-lock'>🔒</span> <b>${f}</b></li>`).join('')}
            </ul>
            <button class="blocked-modal-btn" onclick="document.getElementById('blockedFieldsModal').remove()">OK</button>
        </div>
    `;
    document.body.appendChild(modal);
    setTimeout(() => { modal.classList.add('show'); }, 50);
}

// Exemplo de uso: showBlockedFieldsModal(['title', 'description', 'equipment'])

// Destacar campos bloqueados no formulário
function highlightBlockedFields(blockedFields) {
    blockedFields.forEach(fieldName => {
        const fieldElement = document.querySelector(`[data-field="${fieldName}"]`);
        if (fieldElement) {
            fieldElement.classList.add('blocked-visual');
            // Adiciona ícone de cadeado se não existir
            if (!fieldElement.querySelector('.blocked-visual-icon')) {
                const icon = document.createElement('span');
                icon.className = 'blocked-visual-icon';
                icon.textContent = '🔒';
                fieldElement.appendChild(icon);
            }
        }
    });
}

// Exemplo de integração: chamar showBlockedFieldsModal e highlightBlockedFields quando tentar salvar e houver bloqueio
window.showBlockedFieldsModal = showBlockedFieldsModal;

// ========== FUNÇÕES DE CONTEXTO (CRIAÇÃO vs RESPOSTA) ==========

/**
 * Alterna entre os contextos de permissão (Criação e Resposta)
 */
async function switchContext(newContext) {
    if (newContext === currentContext) {
        return; // Já está no contexto correto
    }
    
    // Verificar se há mudanças não salvas
    if (hasChanges) {
        const confirmMessage = `Você tem alterações não salvas no contexto "${currentContext === 'creation' ? 'Criação' : 'Resposta'}". Deseja continuar sem salvar?`;
        if (!window.confirm(confirmMessage)) {
            return;
        }
    }
    
    // Atualizar contexto atual
    currentContext = newContext;
    
    // Atualizar UI das abas
    document.querySelectorAll('.context-tab').forEach(tab => {
        if (tab.dataset.context === newContext) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Atualizar descrição do contexto
    const contextDesc = document.getElementById('contextDesc');
    if (contextDesc) {
        if (newContext === 'creation') {
            contextDesc.innerHTML = '<strong>🆕 Permissões de Criação:</strong> Campos que o grupo pode editar ao <strong>criar um novo RNC</strong>';
        } else {
            contextDesc.innerHTML = '<strong>📝 Permissões de Resposta:</strong> Campos que o grupo pode editar ao <strong>responder ou editar um RNC existente</strong>';
        }
    }
    
    // Adicionar animação de transição
    const formPreview = document.querySelector('.rnc-form-preview');
    if (formPreview) {
        formPreview.parentElement.classList.add('context-switching');
    }
    
    // Recarregar configurações para o novo contexto
    if (currentGroupId) {
        await loadGroupSettings(currentGroupId);
    }
    
    // Remover classe de animação
    setTimeout(() => {
        if (formPreview) {
            formPreview.parentElement.classList.remove('context-switching');
        }
    }, 500);
    
    // Resetar flag de mudanças
    hasChanges = false;
    
    // Mostrar notificação
    const contextLabel = newContext === 'creation' ? '🆕 CRIAÇÃO' : '📝 RESPOSTA';
    showAlert(`Contexto alterado para: ${contextLabel}`, 'info');
}

// Expor função globalmente
window.switchContext = switchContext;
window.highlightBlockedFields = highlightBlockedFields;