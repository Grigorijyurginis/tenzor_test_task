from unittest.mock import MagicMock, patch

from org_structure.repository import OrgUnitsRepository


def test_init_schema_delegates_to_schema():
    connection = MagicMock()
    repo = OrgUnitsRepository(connection)

    with patch("org_structure.repository.schema.init_schema") as init_schema:
        repo.init_schema()

    init_schema.assert_called_once_with(connection)


def test_load_delegates_to_loader():
    connection = MagicMock()
    repo = OrgUnitsRepository(connection)

    with patch("org_structure.repository.loader.load_into_db", return_value=3) as load_into_db:
        result = repo.load("data/org_structure.json")

    load_into_db.assert_called_once_with(connection, "data/org_structure.json")
    assert result == 3


def test_employees_by_office_delegates_to_queries():
    connection = MagicMock()
    repo = OrgUnitsRepository(connection)

    with patch(
        "org_structure.repository.queries.fetch_employees_by_office",
        return_value=["Иванов", "Сидоров"],
    ) as fetch_employees_by_office:
        result = repo.employees_by_office(3)

    fetch_employees_by_office.assert_called_once_with(connection, 3)
    assert result == ["Иванов", "Сидоров"]
