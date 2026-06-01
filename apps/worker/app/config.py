from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    database_url: str = "postgresql://talent:talent@localhost:5432/talent_intelligence"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672//"
    celery_result_backend: str = "rpc://"

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    @property
    def psycopg_database_url(self) -> str:
        return self.database_url.replace("postgresql+psycopg://", "postgresql://", 1)


settings = Settings()
