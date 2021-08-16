import logging
import os

from mb_commons import Scheduler
from mb_commons.logging import init_logger
from mb_commons.mongo import MongoCollection, MongoConnection
from pymongo.database import Database

from app.config import AppConfig, DConfigSettings, DValueSettings
from mb_base1.models import DConfig, DLog, DValue
from mb_base1.services.base import BaseServiceParams
from mb_base1.services.dconfig_service import DConfigService
from mb_base1.services.dvalue_service import DValueService
from mb_base1.services.system_service import SystemService
from mb_base1.utils import send_telegram_message


class BaseApp:
    def __init__(
        self,
        app_config: AppConfig,
        dconfig_settings: DConfigSettings,
        dvalue_settings: DValueSettings,
    ):
        self.app_config = app_config
        self.logger = init_logger(
            "app",
            file_path=f"{app_config.data_dir}/app.log",
            level=logging.DEBUG if self.app_config.debug else logging.INFO,
        )
        conn = MongoConnection.connect(app_config.database_url)
        self.mongo_client = conn.client
        self.database: Database = conn.database
        self.dconfig_collection: MongoCollection[DConfig] = DConfig.init_collection(self.database)
        self.dvalue_collection: MongoCollection[DValue] = DValue.init_collection(self.database)
        self.dlog_collection: MongoCollection[DLog] = DLog.init_collection(self.database)
        self.dconfig: DConfigSettings = DConfigService.init_storage(
            self.dconfig_collection,
            dconfig_settings,
            self.dlog,
        )
        self.dvalue: DValueSettings = DValueService.init_storage(self.dvalue_collection, dvalue_settings)
        self.scheduler = self.init_scheduler()
        self.dconfig_service = DConfigService
        self.dvalue_service = DValueService
        self.system_service = SystemService(app_config, self.dconfig, self.dvalue, self.scheduler, self.database)
        self.startup()
        self.logger.debug("app started")
        if not self.app_config.debug:
            self.dlog("app_start")

    def dlog(self, category: str, data=None):
        self.dlog_collection.insert_one(DLog(category=category, data=data))

    def send_telegram_message(self, message: str):
        token = self.dconfig.get("telegram_token")
        chat_id = self.dconfig.get("telegram_chat_id")
        if token and chat_id:
            return send_telegram_message(token, chat_id, message)

    def init_scheduler(
        self,
    ) -> Scheduler:
        scheduler = Scheduler(self.logger)
        scheduler.start()
        self.logger.debug("scheduler started")
        return scheduler

    def startup(self):
        pass

    def shutdown(self):
        self.scheduler.stop()
        if not self.app_config.debug:
            self.dlog("app_stop")
        self.stop()
        self.mongo_client.close()
        self.logger.debug("app stopped")
        os._exit(0)  # noqa

    def stop(self):
        pass

    @property
    def base_params(self):
        return BaseServiceParams(
            app_config=self.app_config,
            logger=self.logger,
            dconfig=self.dconfig,
            dvalue=self.dvalue,
            dlog=self.dlog,
            send_telegram_message=self.send_telegram_message,
        )
