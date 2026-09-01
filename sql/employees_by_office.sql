-- Запрос выполняется одним обращением к БД (один round-trip) за счёт двух
-- последовательных рекурсивных CTE в одной инструкции:
--   1. ancestors   — подъём от указанного узла к корню (офису, parent_id IS NULL);
--   2. descendants — спуск от найденного офиса по всему поддереву.
-- Итоговая выборка отфильтрована по type = 3 (сотрудник),
-- на вход утилита принимает employee_id.
WITH RECURSIVE ancestors AS (
    SELECT id, parent_id
    FROM org_units
    WHERE id = %(employee_id)s

    UNION ALL

    SELECT u.id, u.parent_id
    FROM org_units u
    JOIN ancestors a ON u.id = a.parent_id
),
root AS (
    SELECT id FROM ancestors WHERE parent_id IS NULL
),
descendants AS (
    SELECT id, parent_id, name, type
    FROM org_units
    WHERE id = (SELECT id FROM root)

    UNION ALL

    SELECT u.id, u.parent_id, u.name, u.type
    FROM org_units u
    JOIN descendants d ON u.parent_id = d.id
)
SELECT name
FROM descendants
WHERE type = 3
ORDER BY id;
