from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False

    app_env: str = "local"
    app_name: str = "KnowledgeHub API"
    app_version: str = "0.1.0"

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
