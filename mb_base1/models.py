from datetime import datetime
from enum import Enum, unique
from typing import Any, Optional

from mb_commons import utc_now
from mb_commons.mongo import MongoModel, ObjectIdStr
from pydantic import Field


@unique
class DConfigType(str, Enum):
    STRING = "STRING"
    MULTILINE_STRING = "MULTILINE_STRING"
    DATETIME = "DATETIME"
    BOOLEAN = "BOOLEAN"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    DECIMAL = "DECIMAL"


class DConfig(MongoModel):
    id: str = Field(..., alias="_id")
    type: DConfigType
    value: str
    updated_at: Optional[datetime]
    created_at: datetime = Field(default_factory=utc_now)

    __collection__ = "dconfig"


class DValue(MongoModel):
    id: str = Field(..., alias="_id")
    value: str
    updated_at: Optional[datetime]
    created_at: datetime = Field(default_factory=utc_now)

    __collection__ = "dvalue"


class DLog(MongoModel):
    id: Optional[ObjectIdStr] = Field(None, alias="_id")
    category: str
    data: Optional[Any]
    created_at: datetime = Field(default_factory=utc_now)

    __collection__ = "dlog"
    __indexes__ = ["category", "created_at"]
