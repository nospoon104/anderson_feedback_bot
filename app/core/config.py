from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")

    db_host: str = Field(alias="DB_HOST")
    db_port: int = Field(alias="DB_PORT")
    db_name: str = Field(alias="DB_NAME")
    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")

    database_url: str = Field(alias="DATABASE_URL")

    debug: bool = Field(default=False, alias="DEBUG")
    sql_echo: bool = Field(default=False, alias="SQL_ECHO")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    ai_api_key: str = Field(alias="AI_API_KEY")
    ai_base_url: str = Field(
        default="https://ask.chadgpt.ru/api/v1",
        alias="AI_BASE_URL",
    )
    ai_model: str = Field(
        default="gpt-5.4-mini",
        alias="AI_MODEL",
    )
    ai_timeout: int = Field(default=60, alias="AI_TIMEOUT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
