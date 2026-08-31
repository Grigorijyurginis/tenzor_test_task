-- ON CONFLICT DO UPDATE делает загрузку идемпотентной: повторный запуск
-- load с тем же файлом не упадёт на дублировании id, а обновит данные.
INSERT INTO org_units (id, parent_id, name, type)
VALUES (%s, %s, %s, %s)
ON CONFLICT (id) DO UPDATE
    SET parent_id = EXCLUDED.parent_id,
        name = EXCLUDED.name,
        type = EXCLUDED.type;
