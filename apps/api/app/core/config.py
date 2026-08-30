from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la API, cargada desde variables de entorno / .env.

    BOOTSTRAP usa SQLite local; en producción DATABASE_URL apunta a PostgreSQL
    sin requerir cambios en el código de dominio (docs/tecnica/arquitectura.md §6).
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "gi-ot API"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./data/gi-ot.db"

    secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12

    uploads_dir: str = "./data/uploads"

    cors_origins: list[str] = ["http://localhost:3000"]

    # Email/SMTP configuration (opcional para MVP, requerido para envío real)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_use_tls: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
