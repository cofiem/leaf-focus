from enum import unique, Enum


@unique
class LineTypeEnum(Enum):
    UNKNOWN = "unknown"
    LINE = "line"
    TABLE_HEADER = "table-header"
    TABLE_BODY = "table-body"

    @classmethod
    def get_by_value(cls, value: str):
        for i in cls:
            if i.value == value:
                return i
        return None
