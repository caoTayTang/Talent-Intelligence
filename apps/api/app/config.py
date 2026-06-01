from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    database_url: str = "postgresql://talent:talent@localhost:5432/talent_intelligence"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672//"
    celery_result_backend: str = "rpc://"
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = "talent-intelligence-dev"
    r2_public_base_url: str = ""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self.database_url


settings = Settings()
