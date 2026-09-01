import argparse

from pathlib import Path

import db

from org_structure.repository import OrgUnitsRepository

DATA_PATH = Path("data/org_structure.json")
DEFAULT_EMPLOYEE_ID = 3  # id из примера в задании


def parse_args() -> argparse.Namespace:
    """Разбирает аргументы командной строки: --employee-id."""
    parser = argparse.ArgumentParser(
        description="Импорт орг. структуры и вывод сотрудников офиса по id сотрудника."
    )
    parser.add_argument(
        "--employee-id",
        type=int,
        default=DEFAULT_EMPLOYEE_ID,
        help=f"Id сотрудника, офис которого нужно найти (по умолчанию {DEFAULT_EMPLOYEE_ID})",
    )
    return parser.parse_args()


def init_db(repo: OrgUnitsRepository) -> None:
    """Создаёт схему БД (таблицу org_units и индекс)."""
    repo.init_schema()


def load_data(repo: OrgUnitsRepository) -> None:
    """Загружает данные из DATA_PATH."""
    repo.load(DATA_PATH)


def show_employees(repo: OrgUnitsRepository, employee_id: int) -> None:
    """Печатает сотрудников офиса, к которому относится employee_id."""
    for name in repo.employees_by_office(employee_id):
        print(name)


def main() -> None:
    """Создаёт схему, загружает данные и выводит сотрудников офиса — одной транзакцией."""
    args = parse_args()
    connection = db.get_connection()
    try:
        repo = OrgUnitsRepository(connection)
        init_db(repo)
        load_data(repo)
        show_employees(repo, args.employee_id)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
