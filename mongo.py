from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    MONGODB_URI: str
    MONGODB_DB: str = "aja"

    JWT_SECRET: str
    JWT_EXPIRES_MINUTES: int = 60 * 24 * 7  # 7 jours


@lru_cache
def get_settings() -> Settings:
    return Settings()


_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        s = get_settings()
        _client = AsyncIOMotorClient(s.MONGODB_URI)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    s = get_settings()
    return get_client()[s.MONGODB_DB]


async def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
