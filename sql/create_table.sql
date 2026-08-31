-- Внешний ключ сделан DEFERRABLE INITIALLY DEFERRED, чтобы порядок строк во
-- входном JSON (например, если потомок случайно окажется в файле раньше
-- родителя) не влиял на успешность загрузки внутри одной транзакции:
-- проверка ссылочной целостности откладывается до COMMIT.
CREATE TABLE IF NOT EXISTS org_units (
    id        INTEGER PRIMARY KEY,
    parent_id INTEGER REFERENCES org_units (id) DEFERRABLE INITIALLY DEFERRED,
    name      TEXT NOT NULL,
    type      SMALLINT NOT NULL CHECK (type IN (1, 2, 3))
);
