import os
import threading
import tracemalloc

from mb_commons import Scheduler
from pymongo.database import Database

from app.config import AppConfig


class SystemService:
    def __init__(self, app_config: AppConfig, dconfig, dvalue, scheduler: Scheduler, database: Database):
        self.app_config = app_config
        self.dconfig = dconfig
        self.dvalue = dvalue
        self.logfile = self.app_config.data_dir + "/app.log"
        self.scheduler = scheduler
        self.database = database

    def read_logfile(self) -> str:
        with open(self.logfile) as f:
            return f.read()

    def clean_logfile(self):
        with open(self.logfile, "w") as f:
            f.write("")

    def get_stats(self):
        threads = []
        for t in threading.enumerate():
            thread_info = {"name": t.name, "daemon": t.daemon}
            target = t.__dict__.get("_target")
            if target:
                thread_info["func"] = target.__qualname__
            threads.append(thread_info)

        db_stats = {}
        for col in self.database.list_collection_names():
            db_stats[col] = self.database[col].count_documents({})

        return {
            "db": db_stats,
            "logfile": os.path.getsize(self.logfile),
            "dconfig": len(self.dconfig.keys()),
            "dvalue": len(self.dvalue.keys()),
            "dlog": self.database["dlog"].count_documents({}),
            "scheduler": self.scheduler.jobs,
            "threads": threads,
        }

    @staticmethod
    def tracemalloc_snapshot(key_type="lineno", limit=30) -> str:
        result = ""
        snapshot = tracemalloc.take_snapshot()
        for stat in snapshot.statistics(key_type)[:limit]:
            result += str(stat) + "\n"
        return result
