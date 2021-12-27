from bson import ObjectId
from pydantic.json import ENCODERS_BY_TYPE  # noqa
from pymongo.results import DeleteResult, InsertManyResult, InsertOneResult, UpdateResult


def add_custom_encodings():
    ENCODERS_BY_TYPE[ObjectId] = lambda obj: str(obj)
    ENCODERS_BY_TYPE[DeleteResult] = lambda obj: obj.raw_result
    ENCODERS_BY_TYPE[UpdateResult] = lambda obj: obj.raw_result
    ENCODERS_BY_TYPE[InsertOneResult] = lambda o: str(o.inserted_id) if isinstance(o.inserted_id, ObjectId) else o.inserted_id
    ENCODERS_BY_TYPE[InsertManyResult] = lambda obj: obj.inserted_ids  # TODO: ObjectId -> str
