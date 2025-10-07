-- Adicionar coluna context à tabela field_locks
-- Permite diferenciar permissões entre criação e resposta de RNCs
-- Criado em: 07/10/2025

-- 1. Adicionar coluna context (se não existir)
ALTER TABLE field_locks ADD COLUMN context TEXT DEFAULT 'creation';

-- 2. Criar índice para melhor performance
CREATE INDEX IF NOT EXISTS idx_field_locks_context ON field_locks(group_id, context);

-- 3. Duplicar registros existentes para o contexto 'response'
-- Isso garante que as configurações atuais sejam mantidas para ambos os contextos
INSERT INTO field_locks (group_id, field_name, is_locked, context, created_at, updated_at)
SELECT group_id, field_name, is_locked, 'response', created_at, updated_at
FROM field_locks
WHERE context = 'creation'
ON CONFLICT DO NOTHING;

-- 4. Atualizar constraint unique se necessário
-- DROP INDEX IF EXISTS idx_unique_group_field;
-- CREATE UNIQUE INDEX idx_unique_group_field_context ON field_locks(group_id, field_name, context);
