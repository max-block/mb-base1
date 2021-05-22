from mb_commons.mongo import MongoCollection
from pymongo.database import Database

from app.models import Data


class DB:
    def __init__(self, database: Database):
        self.data: MongoCollection[Data] = Data.init_collection(database)
