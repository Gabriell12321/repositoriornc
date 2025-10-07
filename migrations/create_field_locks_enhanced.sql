-- Migração: Sistema de Bloqueio de Campos por Grupo para RNC
-- Criado em: 03/10/2025
-- Permite que administradores definam quais campos cada grupo pode responder/editar

-- Tabela para armazenar configurações de bloqueio de campos por grupo
CREATE TABLE IF NOT EXISTS field_locks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    is_locked BOOLEAN DEFAULT 0,
    is_required BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
    UNIQUE(group_id, field_name)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_field_locks_group_id ON field_locks(group_id);
CREATE INDEX IF NOT EXISTS idx_field_locks_field_name ON field_locks(field_name);

-- Trigger para atualizar updated_at automaticamente
CREATE TRIGGER IF NOT EXISTS update_field_locks_timestamp 
    AFTER UPDATE ON field_locks
BEGIN
    UPDATE field_locks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Inserir configurações padrão para grupos existentes
-- Campos disponíveis para configuração
INSERT OR IGNORE INTO field_locks (group_id, field_name, is_locked, is_required)
SELECT 
    g.id,
    field.name,
    0 as is_locked,  -- Por padrão, todos os campos são editáveis
    CASE 
        WHEN field.name IN ('title', 'description') THEN 1 
        ELSE 0 
    END as is_required  -- Título e descrição são obrigatórios por padrão
FROM groups g
CROSS JOIN (
    SELECT 'title' as name UNION ALL
    SELECT 'description' UNION ALL
    SELECT 'equipment' UNION ALL
    SELECT 'client' UNION ALL
    SELECT 'priority' UNION ALL
    SELECT 'status' UNION ALL
    SELECT 'responsavel' UNION ALL
    SELECT 'inspetor' UNION ALL
    SELECT 'setor' UNION ALL
    SELECT 'area_responsavel' UNION ALL
    SELECT 'price' UNION ALL
    SELECT 'assigned_user_id' UNION ALL
    SELECT 'material' UNION ALL
    SELECT 'quantity' UNION ALL
    SELECT 'drawing' UNION ALL
    SELECT 'mp' UNION ALL
    SELECT 'revision' UNION ALL
    SELECT 'position' UNION ALL
    SELECT 'cv' UNION ALL
    SELECT 'conjunto' UNION ALL
    SELECT 'modelo' UNION ALL
    SELECT 'description_drawing' UNION ALL
    SELECT 'purchase_order' UNION ALL
    SELECT 'justificativa'
) field;