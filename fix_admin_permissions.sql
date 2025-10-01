-- Script para corrigir permissões do admin
-- Execute este script no banco de dados para resolver o problema de resposta das RNCs

-- 1. Criar grupo Admin se não existir
INSERT OR IGNORE INTO groups (name, description) 
VALUES ('Administrador', 'Grupo com todas as permissões do sistema');

-- 2. Obter ID do grupo Admin
-- (Execute separadamente se necessário)

-- 3. Limpar permissões existentes do grupo Admin
DELETE FROM group_permissions 
WHERE group_id = (SELECT id FROM groups WHERE name LIKE '%Admin%' OR name LIKE '%admin%');

-- 4. Adicionar todas as permissões para o grupo Admin
INSERT INTO group_permissions (group_id, permission_name, permission_value)
SELECT 
    (SELECT id FROM groups WHERE name LIKE '%Admin%' OR name LIKE '%admin%'),
    permission_name,
    1
FROM (
    SELECT 'create_rnc' as permission_name UNION ALL
    SELECT 'update_avatar' UNION ALL
    SELECT 'edit_own_rnc' UNION ALL
    SELECT 'view_own_rnc' UNION ALL
    SELECT 'view_all_rncs' UNION ALL
    SELECT 'edit_all_rncs' UNION ALL
    SELECT 'delete_rnc' UNION ALL
    SELECT 'reply_rncs' UNION ALL  -- PERMISSÃO CRÍTICA!
    SELECT 'share_rncs' UNION ALL
    SELECT 'finalize_rncs' UNION ALL
    SELECT 'assign_rncs' UNION ALL
    SELECT 'view_finalized_rncs' UNION ALL
    SELECT 'view_charts' UNION ALL
    SELECT 'view_reports' UNION ALL
    SELECT 'export_data' UNION ALL
    SELECT 'admin_access' UNION ALL
    SELECT 'manage_users' UNION ALL
    SELECT 'manage_groups' UNION ALL
    SELECT 'view_engineering_rncs' UNION ALL
    SELECT 'view_all_departments_rncs' UNION ALL
    SELECT 'view_levantamento_14_15' UNION ALL
    SELECT 'view_groups_for_assignment' UNION ALL
    SELECT 'view_users_for_assignment' UNION ALL
    SELECT 'view_audit_logs' UNION ALL
    SELECT 'manage_system_settings'
);

-- 5. Associar usuários admin ao grupo Admin
UPDATE users 
SET group_id = (SELECT id FROM groups WHERE name LIKE '%Admin%' OR name LIKE '%admin%')
WHERE role = 'admin';

-- 6. Verificar resultado
SELECT 
    g.name as grupo,
    COUNT(gp.permission_name) as total_permissoes
FROM groups g
LEFT JOIN group_permissions gp ON g.id = gp.group_id
WHERE g.name LIKE '%Admin%' OR g.name LIKE '%admin%'
GROUP BY g.id, g.name;

-- 7. Verificar permissão específica reply_rncs
SELECT 
    g.name as grupo,
    gp.permission_name as permissao,
    CASE gp.permission_value 
        WHEN 1 THEN '✅ ATIVA' 
        ELSE '❌ INATIVA' 
    END as status
FROM groups g
JOIN group_permissions gp ON g.id = gp.group_id
WHERE g.name LIKE '%Admin%' OR g.name LIKE '%admin%'
AND gp.permission_name = 'reply_rncs';

-- 8. Verificar usuários admin e seus grupos
SELECT 
    u.name as usuario,
    u.role as funcao,
    g.name as grupo
FROM users u
LEFT JOIN groups g ON u.group_id = g.id
WHERE u.role = 'admin';
