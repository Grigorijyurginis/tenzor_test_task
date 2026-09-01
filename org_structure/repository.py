from pathlib import Path

from org_structure import loader, queries, schema


class OrgUnitsRepository:
    """Операции над таблицей org_units."""

    def __init__(self, connection):
        self._connection = connection

    def init_schema(self) -> None:
        schema.init_schema(self._connection)

    def load(self, path: Path) -> int:
        return loader.load_into_db(self._connection, path)

    def employees_by_office(self, employee_id: int) -> list[str]:
        return queries.fetch_employees_by_office(self._connection, employee_id)
