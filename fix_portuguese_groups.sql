-- Script para corrigir erros de português nos nomes dos setores/grupos
-- Executar com: sqlite3 ippel_system.db < fix_portuguese_groups.sql

-- Verificar nomes atuais antes da correção
SELECT 'ANTES DA CORREÇÃO:' as status;
SELECT id, name FROM groups ORDER BY name;

-- Corrigir erros de português
UPDATE groups SET name = 'Não Definidos' WHERE name = 'Não Definidos' OR name LIKE 'N%o Definidos';
UPDATE groups SET name = 'Produção' WHERE name = 'Produção' OR name LIKE 'Produ%o';
UPDATE groups SET name = 'Usinagem Cilíndrica CNC' WHERE name LIKE 'Usin.%Cil%ndrica CNC' OR name LIKE 'Usin%Cil%ndrica CNC';
UPDATE groups SET name = 'Usinagem Cilíndrica Convencional' WHERE name LIKE 'Usin.%Cil%ndrica Convencional' OR name LIKE 'Usin%Cil%ndrica Convencional';

-- Verificar se há outros caracteres estranhos (�, �, etc)
UPDATE groups SET name = REPLACE(name, '�', 'ã') WHERE name LIKE '%�%';
UPDATE groups SET name = REPLACE(name, '�', 'õ') WHERE name LIKE '%�%';
UPDATE groups SET name = REPLACE(name, '�', 'á') WHERE name LIKE '%�%';
UPDATE groups SET name = REPLACE(name, '�', 'é') WHERE name LIKE '%�%';
UPDATE groups SET name = REPLACE(name, '�', 'í') WHERE name LIKE '%�%';
UPDATE groups SET name = REPLACE(name, '�', 'ó') WHERE name LIKE '%�%';
UPDATE groups SET name = REPLACE(name, '�', 'ú') WHERE name LIKE '%�%';
UPDATE groups SET name = REPLACE(name, '�', 'â') WHERE name LIKE '%�%';
UPDATE groups SET name = REPLACE(name, '�', 'ê') WHERE name LIKE '%�%';
UPDATE groups SET name = REPLACE(name, '�', 'ô') WHERE name LIKE '%�%';
UPDATE groups SET name = REPLACE(name, '�', 'ç') WHERE name LIKE '%�%';

-- Verificar nomes após a correção
SELECT 'APÓS A CORREÇÃO:' as status;
SELECT id, name FROM groups ORDER BY name;

-- Mostrar total de registros afetados
SELECT 'Total de grupos:' as info, COUNT(*) as total FROM groups;
