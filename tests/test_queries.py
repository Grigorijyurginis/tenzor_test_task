import pytest

from pathlib import Path
from unittest.mock import MagicMock

from org_structure import db, loader, schema
from org_structure.queries import EMPLOYEES_BY_OFFICE_SQL, fetch_employees_by_office


def test_fetch_employees_by_office_passes_parameter_and_returns_names():
    """Функция-обёртка должна передать employee_id в запрос и вернуть только имена."""
    cursor = MagicMock()
    cursor.fetchall.return_value = [("Иванов",), ("Сидоров",)]
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor

    result = fetch_employees_by_office(connection, employee_id=3)

    cursor.execute.assert_called_once_with(EMPLOYEES_BY_OFFICE_SQL, {"employee_id": 3})
    assert result == ["Иванов", "Сидоров"]


@pytest.mark.integration
def test_fetch_employees_by_office_against_real_db():
    """
    Проверка, что сам SQL-запрос возвращает верный результат на реальных данных
    из задания. Требует поднятого docker compose:
        docker compose up -d --wait
        pytest -m integration

    Тест выполняется в одной незакоммиченной транзакции и откатывается в finally
    (Postgres поддерживает транзакционный DDL). Вместо отдельной тестовой БД.
    """
    connection = db.get_connection()
    try:
        schema.init_schema(connection)
        loader.load_into_db(connection, Path("data/org_structure.json"))

        result = fetch_employees_by_office(connection, employee_id=3)
    finally:
        connection.rollback()
        connection.close()

    assert result == ["Иванов", "Сидоров", "Петров"]
