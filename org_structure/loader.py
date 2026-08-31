import json

from pathlib import Path
from typing import Any

REQUIRED_FIELDS = ("id", "ParentId", "Name", "Type")
VALID_TYPES = (1, 2, 3)

INSERT_SQL = Path("sql/upsert_org_unit.sql").read_text(encoding="utf-8")


def _is_plain_int(value: Any) -> bool:
    """True только для настоящего int: в Python bool — подкласс int, поэтому
    обычный isinstance(value, int) пропустил бы True/False как валидный id/type."""
    return isinstance(value, int) and not isinstance(value, bool)


def parse_records(raw_records: list[dict[str, Any]]) -> list[tuple]:
    """
    Проверяет и преобразует список сырых JSON-записей в кортежи
    (id, parent_id, name, type), готовые для вставки в БД.

    При несоответствии структуры (отсутствует поле, неверный тип значения,
    недопустимое значение Type и т.п.) бросает ValueError с указанием
    номера и содержимого проблемной записи.
    """
    rows = []
    for index, record in enumerate(raw_records):
        missing = [field for field in REQUIRED_FIELDS if field not in record]
        if missing:
            raise ValueError(
                f"Запись #{index} не содержит обязательные поля {missing}: {record!r}"
            )

        node_id = record["id"]
        parent_id = record["ParentId"]
        name = record["Name"]
        node_type = record["Type"]

        if not _is_plain_int(node_id):
            raise ValueError(
                f"Запись #{index}: 'id' должен быть целым числом, получено {node_id!r}"
            )
        if parent_id is not None and not _is_plain_int(parent_id):
            raise ValueError(
                f"Запись #{index}: 'ParentId' должен быть целым числом или null, "
                f"получено {parent_id!r}"
            )
        if not isinstance(name, str) or not name:
            raise ValueError(
                f"Запись #{index}: 'Name' должен быть непустой строкой, получено {name!r}"
            )
        if not _is_plain_int(node_type) or node_type not in VALID_TYPES:
            raise ValueError(
                f"Запись #{index}: 'Type' должен быть одним из {VALID_TYPES}, "
                f"получено {node_type!r}"
            )

        rows.append((node_id, parent_id, name, node_type))
    return rows


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
    rows = parse_records(raw_records)
    with connection.cursor() as cursor:
        cursor.executemany(INSERT_SQL, rows)
    return len(rows)
