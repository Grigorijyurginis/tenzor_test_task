import json
import pytest

from unittest.mock import MagicMock
from org_structure.loader import INSERT_SQL, load_into_db, load_json_file, parse_records
from org_structure.models import OrgUnit, OrgUnitType


def test_parse_records_valid_data():
    """Корректные записи преобразуются в объекты OrgUnit."""
    raw = [
        {"id": 1, "ParentId": None, "Name": "Офис в Санкт-Петербурге", "Type": 1},
        {"id": 2, "ParentId": 1, "Name": "Отдел разработки", "Type": 2},
    ]

    assert parse_records(raw) == [
        OrgUnit(id=1, parent_id=None, name="Офис в Санкт-Петербурге", type=OrgUnitType.OFFICE),
        OrgUnit(id=2, parent_id=1, name="Отдел разработки", type=OrgUnitType.DEPARTMENT),
    ]


def test_parse_records_missing_field():
    """Отсутствие обязательного поля приводит к ValueError."""
    raw = [{"id": 1, "ParentId": None, "Name": "Офис"}]

    with pytest.raises(ValueError, match="Type"):
        parse_records(raw)


def test_parse_records_invalid_type_value():
    """Недопустимое значение Type (не 1/2/3) отклоняется."""
    raw = [{"id": 1, "ParentId": None, "Name": "Офис", "Type": 99}]

    with pytest.raises(ValueError, match="Type"):
        parse_records(raw)


def test_parse_records_invalid_name():
    """Пустое имя отклоняется."""
    raw = [{"id": 1, "ParentId": None, "Name": "", "Type": 1}]

    with pytest.raises(ValueError, match="Name"):
        parse_records(raw)


def test_parse_records_invalid_parent_id_type():
    """ParentId должен быть целым числом или null."""
    raw = [{"id": 1, "ParentId": "1", "Name": "Офис", "Type": 1}]

    with pytest.raises(ValueError, match="ParentId"):
        parse_records(raw)


def test_parse_records_rejects_bool_as_id():
    """bool — подкласс int в Python; id=True не должен проходить как id=1."""
    raw = [{"id": True, "ParentId": None, "Name": "Офис", "Type": 1}]

    with pytest.raises(ValueError, match="'id'"):
        parse_records(raw)


def test_parse_records_rejects_bool_as_parent_id():
    """Та же проблема для ParentId."""
    raw = [{"id": 1, "ParentId": True, "Name": "Офис", "Type": 1}]

    with pytest.raises(ValueError, match="ParentId"):
        parse_records(raw)


def test_parse_records_rejects_bool_as_type():
    """Та же проблема для Type: True in (1, 2, 3) иначе тоже даёт True."""
    raw = [{"id": 1, "ParentId": None, "Name": "Офис", "Type": True}]

    with pytest.raises(ValueError, match="Type"):
        parse_records(raw)


def test_load_json_file_reads_valid_array(tmp_path):
    """Читает JSON-массив из файла и возвращает его как есть."""
    raw = [{"id": 1, "ParentId": None, "Name": "Офис", "Type": 1}]
    path = tmp_path / "data.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    assert load_json_file(path) == raw


def test_load_json_file_rejects_non_list_top_level(tmp_path):
    """Если на верхнем уровне не массив (например, объект) — ValueError."""
    path = tmp_path / "data.json"
    path.write_text(json.dumps({"id": 1}), encoding="utf-8")

    with pytest.raises(ValueError, match="массив"):
        load_json_file(path)


def test_load_into_db_inserts_parsed_rows(tmp_path):
    """load_into_db читает файл и вставляет разобранные строки (коммит — на вызывающем коде)."""
    raw = [
        {"id": 1, "ParentId": None, "Name": "Офис", "Type": 1},
        {"id": 2, "ParentId": 1, "Name": "Иванов", "Type": 3},
    ]
    path = tmp_path / "data.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    cursor = MagicMock()
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor

    count = load_into_db(connection, path)

    cursor.executemany.assert_called_once_with(
        INSERT_SQL,
        [(1, None, "Офис", 1), (2, 1, "Иванов", 3)],
    )
    connection.commit.assert_not_called()
    assert count == 2
