"""Configuracion de la app: lee las variables de entorno desde el archivo .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Lee el .env e ignora las variables que todavia no usamos.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str


# Instancia unica que el resto de la app importa: `from app.config import settings`
settings = Settings()
