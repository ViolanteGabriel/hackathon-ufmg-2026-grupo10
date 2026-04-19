from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM via Groq (gratuito) — obtenha sua chave em https://console.groq.com
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Embeddings locais via sentence-transformers (sem chave de API necessária)
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    postgres_password: str = "enteros_dev"
    database_url: str = "postgresql+psycopg://enteros:enteros_dev@db:5432/enteros"

    jwt_secret: str = "change-me-only-for-demo"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    log_level: str = "INFO"
    data_dir: str = "/data"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
