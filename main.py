from org_structure import db, schema


def init_db() -> None:
    """Открывает соединение с PostgreSQL и создаёт схему БД."""
    connection = db.get_connection()
    try:
        schema.init_schema(connection)
        print("Схема БД создана")
    finally:
        connection.close()


if __name__ == "__main__":
    init_db()
