from pathlib import Path

EMPLOYEES_BY_OFFICE_SQL = Path("sql/employees_by_office.sql").read_text(encoding="utf-8")


def fetch_employees_by_office(connection, employee_id: int) -> list[str]:
    """
    Возвращает имена всех сотрудников офиса, к которому относится сотрудник
    с указанным employee_id (сам он входит в результат), отсортированные по id.

    Если узел с таким id не найден в таблице, `ancestors`/`root`/`descendants`
    остаются пустыми и функция возвращает пустой список — без исключений.
    """
    with connection.cursor() as cursor:
        cursor.execute(EMPLOYEES_BY_OFFICE_SQL, {"employee_id": employee_id})
        return [row[0] for row in cursor.fetchall()]
