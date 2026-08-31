from pathlib import Path

from org_structure import db, loader, schema

DATA_PATH = Path("data/org_structure.json")


def init_db(connection) -> None:
    """Создаёт схему БД (таблицу org_units и индекс)."""
    schema.init_schema(connection)
    print("Схема БД создана")


def load_data(connection) -> None:
    """Загружает данные из DATA_PATH."""
    count = loader.load_into_db(connection, DATA_PATH)
    print(f"Загружено записей: {count}")


def main() -> None:
    """
    Создаёт схему и загружает данные одной транзакцией
    """
    connection = db.get_connection()
    try:
        init_db(connection)
        load_data(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
