-- Script para corrigir permissões do sistema
-- Execute este script no banco de dados para adicionar a permissão reply_rncs

-- 1. Adicionar permissão reply_rncs para todos os grupos existentes
INSERT OR IGNORE INTO group_permissions (group_id, permission_name, permission_value)
SELECT g.id, 'reply_rncs', 1
FROM groups g
WHERE NOT EXISTS (
    SELECT 1 FROM group_permissions gp 
    WHERE gp.group_id = g.id AND gp.permission_name = 'reply_rncs'
);

-- 2. Adicionar outras permissões importantes que podem estar faltando
INSERT OR IGNORE INTO group_permissions (group_id, permission_name, permission_value)
SELECT g.id, 'share_rncs', 1
FROM groups g
WHERE NOT EXISTS (
    SELECT 1 FROM group_permissions gp 
    WHERE gp.group_id = g.id AND gp.permission_name = 'share_rncs'
);

INSERT OR IGNORE INTO group_permissions (group_id, permission_name, permission_value)
SELECT g.id, 'finalize_rncs', 1
FROM groups g
WHERE NOT EXISTS (
    SELECT 1 FROM group_permissions gp 
    WHERE gp.group_id = g.id AND gp.permission_name = 'finalize_rncs'
);

INSERT OR IGNORE INTO group_permissions (group_id, permission_name, permission_value)
SELECT g.id, 'assign_rncs', 1
FROM groups g
WHERE NOT EXISTS (
    SELECT 1 FROM group_permissions gp 
    WHERE gp.group_id = g.id AND gp.permission_name = 'assign_rncs'
);

-- 3. Verificar permissões existentes
SELECT 
    g.name as grupo,
    gp.permission_name as permissao,
    CASE gp.permission_value 
        WHEN 1 THEN '✅ ATIVA' 
        ELSE '❌ INATIVA' 
    END as status
FROM groups g
LEFT JOIN group_permissions gp ON g.id = gp.group_id
WHERE gp.permission_name IN ('reply_rncs', 'share_rncs', 'finalize_rncs', 'assign_rncs')
ORDER BY g.name, gp.permission_name;

-- 4. Contar permissões por grupo
SELECT 
    g.name as grupo,
    COUNT(gp.permission_name) as total_permissoes
FROM groups g
LEFT JOIN group_permissions gp ON g.id = gp.group_id
GROUP BY g.id, g.name
ORDER BY g.name;
