import json

from pathlib import Path
from typing import Any

from org_structure.models import OrgUnit

INSERT_SQL = Path("sql/upsert_org_unit.sql").read_text(encoding="utf-8")


def parse_records(raw_records: list[dict[str, Any]]) -> list[OrgUnit]:
    """
    Проверяет и преобразует список сырых JSON-записей в список OrgUnit.

    При несоответствии структуры (отсутствует поле, неверный тип значения,
    недопустимое значение Type и т.п.) бросает ValueError с указанием
    номера и содержимого записи с ошибкой.
    """
    return [OrgUnit.from_raw(record, index) for index, record in enumerate(raw_records)]


def load_json_file(path: Path) -> list[dict[str, Any]]:
    """Читает JSON-файл и возвращает массив записей орг. структуры."""
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("Ожидался JSON-массив записей на верхнем уровне")
    return data


def load_into_db(connection, path: Path) -> int:
    """
    Загружает данные из JSON-файла в таблицу org_units.

    Возвращает количество загруженных записей.

    Упрощение: весь файл читается в память (json.load), все строки
    собираются в один список (parse_records) и вставляются одним
    executemany(). Для входного файла из задания (десятки записей) это
    нормально, но для файла на порядки больше (условно 10k+ записей) так
    делать в проде не стоит — понадобится потоковый парсинг JSON (например,
    ijson) вместо json.load, чтобы не держать весь файл в памяти, и
    массовая загрузка через COPY FROM STDIN вместо executemany с
    построчными INSERT — она на порядок быстрее на больших объёмах.
    """
    raw_records = load_json_file(path)
    units = parse_records(raw_records)
    rows = [(u.id, u.parent_id, u.name, int(u.type)) for u in units]
    with connection.cursor() as cursor:
        cursor.executemany(INSERT_SQL, rows)
    return len(rows)
