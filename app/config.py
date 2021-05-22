from decimal import Decimal

from app import __version__
from mb_base1.config import BaseAppConfig
from mb_base1.services.dconfig_service import DC, DConfigStorage
from mb_base1.services.dvalue_service import DV, DValueStorage


class AppConfig(BaseAppConfig):
    app_version: str = __version__
    tags: list[str] = ["data"]
    main_menu: dict[str, str] = {"/data": "data"}
    telegram_bot_help = """
/first_command - bla bla1
/second_command - bla bla2
"""


class DConfigSettings(DConfigStorage):
    telegram_token = DC("", "telegram bot token", hide=True)
    telegram_chat_id = DC(0, "telegram chat id")
    telegram_polling = DC(False)
    telegram_admins = DC("", "admin1,admin2,admin3")
    price = DC(Decimal("1.23"), "long long long long long long long long long long long long long long long long ")
    long_cfg_1 = DC("many lines \n" * 5)


class DValueSettings(DValueStorage):
    tmp1 = DV("bla")
    tmp2 = DV("bla")
    processed_block = DV(111, "bla bla about processed_block")
    last_checked_at = DV(None, "bla bla about last_checked_at", False)
