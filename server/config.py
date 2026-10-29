from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Read from environment variables (or a .env file next to where the app starts)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./car_tracker.db"
    secret_key: str
    access_token_expire_minutes: int = 60 * 24
    cors_origins: list[str] = ["https://localhost:5173", "http://localhost:5173"]


settings = Settings()
