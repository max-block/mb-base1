from __future__ import annotations

import itertools
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable, Union

import pydash
import yaml
from mb_commons import Result, utc_now
from mb_commons.mongo import MongoCollection
from wrapt import synchronized

from mb_base1.errors import UnregisteredDConfigError
from mb_base1.models import DConfig, DConfigType
from mb_base1.utils import get_registered_attributes


class DC:
    _counter = itertools.count()

    def __init__(self, value: Union[str, int, float, bool, Decimal], description="", hide=False):
        self.value = value
        self.description = description
        self.hide = hide
        self.order = next(DC._counter)

    def __get__(self, obj, cls):
        if obj is None:
            return self

        return getattr(DConfigService.dconfig_storage, self.key)

    def __set_name__(self, owner, name):
        self.key = name

    @staticmethod
    def get_attrs_from_settings(dconfig_settings) -> list[DC]:
        attrs: list[DC] = []
        keys = get_registered_attributes(dconfig_settings)
        for key in keys:
            field = getattr(dconfig_settings.__class__, key)
            if isinstance(field, DC):
                attrs.append(field)
        attrs.sort(key=lambda x: x.order)

        return attrs


class DConfigStorage(dict):
    descriptions: dict[str, str] = {}
    types: dict[str, DConfigType] = {}
    hidden: set[str] = set()

    def __getattr__(self, item):
        if item not in self:
            raise UnregisteredDConfigError(item)

        return self.get(item, None)

    def get_or_none(self, key: str):
        try:
            return self.get(key)
        except UnregisteredDConfigError:
            return None

    def get_non_hidden_keys(self):
        return self.keys() - self.hidden


@dataclass
class DConfigInitValue:
    key: str
    order: int
    description: str
    value: Union[str, int, float, bool]


class DConfigService:
    dconfig_storage = DConfigStorage()
    dconfig_collection: MongoCollection[DConfig]
    dlog: Callable

    @classmethod
    @synchronized
    def init_storage(cls, dconfig_collection: MongoCollection[DConfig], dconfig_settings, dlog: Callable):
        cls.dconfig_collection = dconfig_collection
        cls.dlog = dlog

        for attr in DC.get_attrs_from_settings(dconfig_settings):
            type_ = cls.get_type(attr.value)
            cls.dconfig_storage.descriptions[attr.key] = attr.description
            cls.dconfig_storage.types[attr.key] = type_
            if attr.hide:
                cls.dconfig_storage.hidden.add(attr.key)

            dv = cls.dconfig_collection.get_or_none(attr.key)
            if dv:
                cls.dconfig_storage[attr.key] = cls.get_type_value(dv.type, dv.value).ok
            else:  # create rows if not exists
                cls.dconfig_collection.insert_one(
                    DConfig(_id=attr.key, type=type_, value=cls.get_str_value(type_, attr.value)),
                )
                cls.dconfig_storage[attr.key] = attr.value

        # remove rows which not in settings.DCONFIG
        cls.dconfig_collection.delete_many({"_id": {"$nin": get_registered_attributes(dconfig_settings)}})
        return cls.dconfig_storage

    @classmethod
    def update_multiline(cls, key: str, value: str):
        value = value.replace("\r", "")
        cls.dconfig_collection.update_by_id(key, {"$set": {"value": value, "updated_at": utc_now()}})
        cls.dconfig_storage[key] = value
        return True

    @classmethod
    def update(cls, data: dict[str, str]) -> bool:
        result = True
        for key, str_value in data.items():
            if key in cls.dconfig_storage:
                str_value = str_value or ""  # for BOOLEAN type (checkbox)
                str_value = str_value.replace("\r", "")  # for MULTILINE (textarea do it)
                type_value_res = cls.get_type_value(cls.dconfig_storage.types[key], str_value.strip())
                if type_value_res.is_ok():
                    cls.dconfig_collection.update_by_id(key, {"$set": {"value": str_value, "updated_at": utc_now()}})
                    cls.dconfig_storage[key] = type_value_res.ok
                else:
                    cls.dlog("dconfig_service_update", {"error": type_value_res.error, "key": key})
                    result = False
            else:
                cls.dlog("dconfig_service_update", {"error": "unknown key", "key": key})
                result = False
        return result

    @classmethod
    def update_dconfig_yaml(cls, yaml_value: str):
        data = yaml.full_load(yaml_value)
        if isinstance(data, dict):
            return cls.update(data)

    @classmethod
    def export_dconfig_yaml(cls):
        result = {k: v for k, v in cls.dconfig_storage.items()}
        result = pydash.omit(result, *cls.dconfig_storage.hidden)
        return yaml.dump(result, explicit_end=True, default_style="'")

    @staticmethod
    def get_type(value) -> DConfigType:
        if type(value) is str:
            return DConfigType.MULTILINE if "\n" in value else DConfigType.STRING
        elif type(value) is int:
            return DConfigType.INTEGER
        elif type(value) is float:
            return DConfigType.FLOAT
        elif type(value) is Decimal:
            return DConfigType.DECIMAL
        elif type(value) is bool:
            return DConfigType.BOOLEAN
        else:
            raise ValueError(f"unsupported type: {type(value)}")

    @staticmethod
    def get_type_value(type_: DConfigType, str_value: str) -> Result[Any]:
        try:
            if type_ == DConfigType.BOOLEAN:
                return Result(ok=bool(str_value))
            elif type_ == DConfigType.INTEGER:
                return Result(ok=int(str_value))
            elif type_ == DConfigType.FLOAT:
                return Result(ok=float(str_value))
            elif type_ == DConfigType.DECIMAL:
                return Result(ok=Decimal(str_value))
            elif type_ == DConfigType.STRING:
                return Result(ok=str_value)
            elif type_ == DConfigType.MULTILINE:
                return Result(ok=str_value.replace("\r", ""))
            else:
                return Result(ok=f"unsupported type: {type_}")
        except Exception as e:
            return Result(error=str(e))

    @staticmethod
    def get_str_value(type_: DConfigType, value: Any) -> str:
        if type_ is DConfigType.BOOLEAN:
            return "True" if value else ""
        return str(value)
