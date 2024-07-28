import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# load_dotenv(dotenv_path=Path("~/.env"))
DOTENV = os.path.join(os.path.dirname(__file__), ".env")

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=DOTENV)


settings = Settings()
