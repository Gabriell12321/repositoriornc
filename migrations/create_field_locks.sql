-- =====================================================
-- SISTEMA DE BLOQUEIO DE CAMPOS POR GRUPO
-- =====================================================
-- Criado em: 03/10/2025
-- Descrição: Permite ao admin configurar quais campos
--            cada grupo pode ou não editar na criação de RNC
-- =====================================================

-- Criar tabela de bloqueios de campos
CREATE TABLE IF NOT EXISTS field_locks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    is_locked INTEGER DEFAULT 1,  -- 1 = bloqueado, 0 = liberado
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    UNIQUE(group_id, field_name)
);

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_field_locks_group ON field_locks(group_id);
CREATE INDEX IF NOT EXISTS idx_field_locks_field ON field_locks(field_name);

-- Campos disponíveis para bloqueio na criação de RNC
-- (Estes são os campos que podem ser bloqueados)
/*
Campos editáveis:
  - title                 (Título)
  - description           (Descrição)
  - equipment             (Equipamento)
  - client                (Cliente)
  - priority              (Prioridade)
  - status                (Status)
  - responsavel           (Responsável)
  - inspetor              (Inspetor)
  - setor                 (Setor)
  - area_responsavel      (Área Responsável)
  - price                 (Preço)
  - assigned_user_id      (Usuário Atribuído)
*/

-- =====================================================
-- DADOS INICIAIS (EXEMPLO)
-- =====================================================
-- Por padrão, todos os campos estão liberados
-- O admin pode bloquear conforme necessário

-- Inserir configuração padrão para grupos existentes
-- (Ajuste os IDs de grupo conforme seu banco)

-- Exemplo: Bloquear alguns campos para grupo "Operadores" (assumindo group_id = 2)
-- INSERT INTO field_locks (group_id, field_name, is_locked) VALUES
-- (2, 'price', 1),              -- Operadores não podem editar preço
-- (2, 'area_responsavel', 1),   -- Operadores não podem editar área
-- (2, 'priority', 1);            -- Operadores não podem editar prioridade

-- Exemplo: Bloquear para grupo "Inspetores" (assumindo group_id = 3)
-- INSERT INTO field_locks (group_id, field_name, is_locked) VALUES
-- (3, 'status', 1),              -- Inspetores não podem mudar status
-- (3, 'price', 1);               -- Inspetores não podem editar preço

-- =====================================================
-- TRIGGER PARA ATUALIZAR updated_at
-- =====================================================
CREATE TRIGGER IF NOT EXISTS update_field_locks_timestamp 
AFTER UPDATE ON field_locks
BEGIN
    UPDATE field_locks 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- =====================================================
-- CONSULTAS ÚTEIS
-- =====================================================

-- Ver todos os bloqueios por grupo
-- SELECT g.name as grupo, fl.field_name as campo, fl.is_locked as bloqueado
-- FROM field_locks fl
-- JOIN groups g ON fl.group_id = g.id
-- ORDER BY g.name, fl.field_name;

-- Ver campos bloqueados para um grupo específico
-- SELECT field_name FROM field_locks 
-- WHERE group_id = ? AND is_locked = 1;

-- Limpar todos os bloqueios de um grupo
-- DELETE FROM field_locks WHERE group_id = ?;

-- =====================================================
