from pathlib import Path

from org_structure import loader, queries, schema


class OrgUnitsRepository:
    """Операции над таблицей org_units."""

    def __init__(self, connection):
        """Сохраняет уже открытое соединение — сам его не открывает и не закрывает."""
        self._connection = connection

    def init_schema(self) -> None:
        """Создаёт таблицу org_units и индекс по parent_id, если их ещё нет."""
        schema.init_schema(self._connection)

    def load(self, path: Path) -> int:
        """Загружает данные из JSON-файла в таблицу org_units, возвращает число записей."""
        return loader.load_into_db(self._connection, path)

    def employees_by_office(self, employee_id: int) -> list[str]:
        """Возвращает имена сотрудников офиса, к которому относится employee_id."""
        return queries.fetch_employees_by_office(self._connection, employee_id)
