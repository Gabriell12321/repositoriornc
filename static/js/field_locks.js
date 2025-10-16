// Field Locks Interface - JavaScript Moderno e Seguro
let currentGroupId = null;
let fieldLocks = {};
let hasChanges = false;

const availableFields = [
    'rnc_number', 'title', 'description', 'priority', 'status', 'price',
    'equipment', 'material', 'quantity', 'drawing', 'mp', 'revision', 'position', 
    'cv', 'conjunto', 'modelo', 'description_drawing', 'purchase_order',
    'assigned_user_id', 'responsavel', 'inspetor', 'setor', 'area_responsavel', 'client',
    'disposition_usar', 'disposition_retrabalhar', 'disposition_rejeitar', 
    'disposition_sucata', 'disposition_devolver_estoque', 'disposition_devolver_fornecedor',
    'inspection_aprovado', 'inspection_reprovado', 'inspection_ver_rnc',
    'signature_inspection_name', 'signature_inspection_date', 'signature_engineering_name',
    'signature_engineering_date', 'signature_inspection2_name', 'signature_inspection2_date',
    'instruction_retrabalho', 'cause_rnc', 'action_rnc', 'justificativa'
];

document.addEventListener('DOMContentLoaded', function() {
    loadGroups();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('groupSearch').addEventListener('input', function(e) {
        filterGroups(e.target.value);
    });
    
    document.querySelectorAll('.field-item').forEach(field => {
        field.addEventListener('click', function() {
            if (currentGroupId) toggleField(this.dataset.field);
        });
    });
}

async function loadGroups() {
    try {
        const response = await fetch('/admin/field-locks/api/groups');
        const groups = await response.json();
        const groupList = document.getElementById('groupList');
        groupList.innerHTML = '';
        
        if (groups.length === 0) {
            groupList.innerHTML = '<li class="no-groups">📭 Nenhum grupo encontrado</li>';
            return;
        }
        
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
    } catch (error) {
        showAlert('❌ Erro ao carregar grupos: ' + error.message, 'error');
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
    currentGroupId = groupId;
    document.querySelectorAll('.group-item').forEach(item => item.classList.remove('active'));
    event.target.closest('.group-item').classList.add('active');
    
    document.getElementById('loading').style.display = 'none';
    document.getElementById('groupContent').style.display = 'block';
    document.getElementById('groupTitle').textContent = `Configurações: ${groupName}`;
    
    await loadGroupSettings(groupId);
}

async function loadGroupSettings(groupId) {
    try {
        const response = await fetch(`/admin/field-locks/api/locks/${groupId}`);
        const locks = await response.json();
        
        fieldLocks = {};
        locks.forEach(lock => {
            fieldLocks[lock.field_name] = lock.is_locked;
        });
        
        updateFieldDisplay();
        updateStats();
        hasChanges = false;
    } catch (error) {
        showAlert('❌ Erro ao carregar configurações: ' + error.message, 'error');
    }
}

function updateFieldDisplay() {
    availableFields.forEach(fieldName => {
        const fieldElement = document.querySelector(`[data-field="${fieldName}"]`);
        if (!fieldElement) return;
        
        const statusElement = fieldElement.querySelector('.field-status');
        const isLocked = fieldLocks[fieldName] || false;
        
        fieldElement.className = `field-item ${isLocked ? 'locked' : 'unlocked'}`;
        statusElement.className = `field-status ${isLocked ? 'locked' : 'unlocked'}`;
        statusElement.textContent = isLocked ? '🔒' : '🔓';
    });
}

function updateStats() {
    const locked = availableFields.filter(field => fieldLocks[field]).length;
    const unlocked = availableFields.length - locked;
    document.getElementById('statLocked').textContent = locked;
    document.getElementById('statUnlocked').textContent = unlocked;
}

function toggleField(fieldName) {
    fieldLocks[fieldName] = !fieldLocks[fieldName];
    updateFieldDisplay();
    updateStats();
    hasChanges = true;
}

async function saveChanges() {
    if (!currentGroupId) {
        showAlert('⚠️ Selecione um grupo primeiro', 'error');
        return;
    }
    
    try {
        const locks = availableFields.map(fieldName => ({
            field_name: fieldName,
            is_locked: fieldLocks[fieldName] || false
        }));
        
        const response = await fetch(`/admin/field-locks/api/locks/${currentGroupId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ locks })
        });
        
        const result = await response.json();
        if (response.ok) {
            showAlert('✅ Configurações salvas com sucesso!', 'success');
            hasChanges = false;
        } else {
            throw new Error(result.error || 'Erro desconhecido');
        }
    } catch (error) {
        showAlert('❌ Erro ao salvar: ' + error.message, 'error');
    }
}

function unlockAll() {
    availableFields.forEach(fieldName => {
        fieldLocks[fieldName] = false;
    });
    updateFieldDisplay();
    updateStats();
    hasChanges = true;
    showAlert('🔓 Todos os campos foram liberados', 'success');
}

function lockAll() {
    availableFields.forEach(fieldName => {
        fieldLocks[fieldName] = true;
    });
    updateFieldDisplay();
    updateStats();
    hasChanges = true;
    showAlert('🔒 Todos os campos foram bloqueados', 'success');
}

async function resetGroup() {
    if (!currentGroupId) {
        showAlert('⚠️ Selecione um grupo primeiro', 'error');
        return;
    }
    
    if (!confirm('🗑️ Tem certeza que deseja resetar todas as configurações deste grupo?')) return;
    
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
        showAlert('❌ Erro ao resetar: ' + error.message, 'error');
    }
}

function showAlert(message, type) {
    const alertsContainer = document.getElementById('alerts');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    alertsContainer.appendChild(alertDiv);
    
    if (type === 'success') {
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}