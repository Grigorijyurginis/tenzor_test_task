from pathlib import Path

CREATE_TABLE_SQL = Path("sql/create_table.sql").read_text(encoding="utf-8")
CREATE_INDEX_SQL = Path("sql/create_index.sql").read_text(encoding="utf-8")


def init_schema(connection):
    """Создаёт таблицу org_units и индекс по parent_id, если их ещё нет."""
    with connection.cursor() as cursor:
        cursor.execute(CREATE_TABLE_SQL)
        cursor.execute(CREATE_INDEX_SQL)
    connection.commit()
