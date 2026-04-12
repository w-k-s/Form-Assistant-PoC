import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = ".env" if os.getenv("ENV") is None else f'.env.{os.getenv("ENV").lower()}'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")

    database_url: str
    google_client_id: str
    google_client_secret: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 72
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-south-1"
    bedrock_model_id: str = "mistral.ministral-3-3b-instruct"


settings = Settings()
