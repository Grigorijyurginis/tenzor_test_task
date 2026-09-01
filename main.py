from pathlib import Path

from org_structure import db
from org_structure.repository import OrgUnitsRepository

DATA_PATH = Path("data/org_structure.json")
EMPLOYEE_ID = 3


def init_db(repo: OrgUnitsRepository) -> None:
    """Создаёт схему БД (таблицу org_units и индекс)."""
    repo.init_schema()
    print("Схема БД создана")


def load_data(repo: OrgUnitsRepository) -> None:
    """Загружает данные из DATA_PATH."""
    count = repo.load(DATA_PATH)
    print(f"Загружено записей: {count}")


def show_employees(repo: OrgUnitsRepository, employee_id: int) -> None:
    """Печатает сотрудников офиса, к которому относится employee_id."""
    for name in repo.employees_by_office(employee_id):
        print(name)


def main() -> None:
    """Создаёт схему и загружает данные одной транзакцией."""
    connection = db.get_connection()
    try:
        repo = OrgUnitsRepository(connection)
        init_db(repo)
        load_data(repo)
        show_employees(repo, EMPLOYEE_ID)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
