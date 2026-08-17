from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    database_url: str = "postgresql://talent:talent@localhost:5432/talent_intelligence"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672//"
    celery_result_backend: str = "rpc://"

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = "talent-intelligence-dev"

    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_api_key: str = ""
    model_name: str = "openai/gpt-oss-120b"
    vlm_base_url: str = ""
    vlm_api_key: str = ""
    vlm_model_name: str = "qwen/qwen3.6-27b"
    vlm_mode: str = "auto"
    vlm_max_pages: int = 8
    vlm_pages_per_batch: int = 2
    embedding_base_url: str = "https://api.scaleway.ai/v1"
    embedding_api_key: str = ""
    embedding_model_name: str = "qwen3-embedding-8b"
    embedding_dimension: int = 4096
    tavily_api_key: str = ""

    @property
    def psycopg_database_url(self) -> str:
        return self.database_url.replace("postgresql+psycopg://", "postgresql://", 1)


settings = Settings()
