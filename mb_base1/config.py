from pydantic import BaseSettings

from mb_base1 import __version__


class BaseAppConfig(BaseSettings):
    app_name: str
    data_dir: str
    access_token: str
    domain: str
    database_url: str
    debug: bool = False
    mb_base1_version: str = __version__
    app_version: str = "unknown"

    tags: list[str] = []
    main_menu: dict[str, str] = {}
    telegram_bot_help = "update me!"

    use_https: bool = True

    @property
    def tags_metadata(self):
        base = [
            {"name": "dconfig"},
            {"name": "dvalue"},
            {"name": "dlog"},
            {"name": "system"},
            {"name": "auth"},
            {"name": "base-ui"},
        ]
        app = [{"name": t} for t in self.tags]
        return app + base

    class Config:
        env_file = ".env"
