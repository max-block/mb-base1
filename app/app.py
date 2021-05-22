from app.config import AppConfig, DConfigSettings, DValueSettings
from app.db import DB
from app.services.base import AppServiceParams
from app.services.data_service import DataService
from mb_base1.app import BaseApp


class App(BaseApp):
    def __init__(self):
        super().__init__(AppConfig(), DConfigSettings(), DValueSettings())
        self.db: DB = DB(self.database)
        # services
        self.data_service = DataService(self.base_params)
        # scheduler
        self.scheduler.add_job(self.data_service.generate_data, 6000)

    @property
    def base_params(self):
        return AppServiceParams(super().base_params, self.db)
