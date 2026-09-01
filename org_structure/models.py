from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class OrgUnitType(IntEnum):
    OFFICE = 1
    DEPARTMENT = 2
    EMPLOYEE = 3


def _is_plain_int(value: Any) -> bool:
    """True только для настоящего int: в Python bool — подкласс int, поэтому
    обычный isinstance(value, int) пропустил бы True/False как валидный id."""
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass(frozen=True, slots=True)
class OrgUnit:
    """Один узел орг. структуры: офис, отдел или сотрудник."""

    id: int
    parent_id: int | None
    name: str
    type: OrgUnitType

    @classmethod
    def from_raw(cls, record: dict[str, Any], index: int) -> "OrgUnit":
        """Валидирует сырую JSON-запись и превращает её в OrgUnit.

        Бросает ValueError с номером и содержимым записи
        """
        missing = [f for f in ("id", "ParentId", "Name", "Type") if f not in record]
        if missing:
            raise ValueError(
                f"Запись #{index} не содержит обязательные поля {missing}: {record!r}"
            )

        node_id, parent_id = record["id"], record["ParentId"]
        name, raw_type = record["Name"], record["Type"]

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
        if not _is_plain_int(raw_type) or raw_type not in (t.value for t in OrgUnitType):
            raise ValueError(
                f"Запись #{index}: 'Type' должен быть одним из "
                f"{[t.value for t in OrgUnitType]}, получено {raw_type!r}"
            )

        return cls(id=node_id, parent_id=parent_id, name=name, type=OrgUnitType(raw_type))
