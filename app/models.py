from datetime import datetime
from enum import Enum, unique
from typing import Optional

from mb_commons import utc_now
from mb_commons.mongo import MongoModel, ObjectIdStr
from pydantic import Field


@unique
class DataStatus(str, Enum):
    OK = "OK"
    ERROR = "ERROR"


class Data(MongoModel):
    id: Optional[ObjectIdStr] = Field(None, alias="_id")
    status: DataStatus
    value: int
    created_at: datetime = Field(default_factory=utc_now)

    __collection__ = "data"
    __indexes__ = ["status", "created_at"]
